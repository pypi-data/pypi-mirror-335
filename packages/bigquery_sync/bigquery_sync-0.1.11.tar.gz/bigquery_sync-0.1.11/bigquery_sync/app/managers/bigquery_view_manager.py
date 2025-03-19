import os
from bigquery_sync.app.gcloud_clients.bigquery_client import BigQueryClient
from bigquery_sync.app.utils.utils import create_dir


class BigQueryViewManager(object):

    def __init__(self, project, project_root_path, service_account_file_path=None):
        self.project = project
        self.project_root_path = project_root_path
        self.bqc = BigQueryClient(service_account_file_path=service_account_file_path, project=project)

    def __remove_invalid_sqls(self, path, file_list):
        files = os.listdir(path)
        for file in files:
            file_path = path + '/' + file
            if os.path.splitext(file)[1] == '.sql' and file not in file_list:
                os.remove(file_path)

    def fetch_views(self, datasets=None, excluded_datasets:list=None):
        print('Fetching views from BigQuery')
        bqc = self.bqc
        project = self.project
        project_path = self.project_root_path + '/' + project
        create_dir(path=project_path)
        if datasets is None:
            datasets = [k.dataset_id for k in bqc.list_datasets()]
        self.__remove_invalid_sqls(path=project_path, file_list=datasets)
        excluded_datasets = excluded_datasets or []
        for dataset in datasets:
            if dataset in excluded_datasets:
                continue
            dataset_path = project_path + '/' + dataset
            create_dir(path=dataset_path)
            tables = bqc.list_tables(dataset)
            table_list = [k.table_id + '.sql' for k in tables]
            self.__remove_invalid_sqls(path=dataset_path, file_list=table_list)
            for table in tables:
                if table.table_type == 'VIEW':
                    view = bqc.get_table(dataset_name=table.dataset_id, table_name=table.table_id)
                    print('Writing view: ' + table.table_id + ' in ' + dataset)
                    with open(dataset_path + '/' + table.table_id + '.sql', 'w') as output_file:
                        output_file.write(view.view_query)



    def delete_view(self, dataset, view):
        bqc = self.bqc
        view = os.path.splitext(view)[0]
        bqc.delete_view(dataset_name=dataset, view_name=view)
        if len(bqc.list_tables(dataset_name=dataset)) == 0:
            bqc.delete_dataset(dataset_name=dataset)

    def create_or_update_view(self, dataset, view, file_path=None, query=None):
        bqc = self.bqc
        view = os.path.splitext(view)[0]
        if file_path:
            with open(file_path, 'r') as sql_file:
                query = sql_file.read()
        if not bqc.does_dataset_exist(dataset_name=dataset):
            bqc.create_dataset(dataset_name=dataset)
        bqc.create_or_update_view(dataset_name=dataset, view_name=view, query=query)

    def delete_dataset(self, dataset, dataset_contents=True, not_found_ok=True):
        bqc = self.bqc
        bqc.delete_dataset(dataset_name=dataset, dataset_contents=dataset_contents, not_found_ok=not_found_ok)
