import os
import json

from bigquery_sync.app.config.config import RETRY_COUNT, SCHEDULED_QUERIES
from bigquery_sync.app.managers import GitManager, BigQueryViewManager, ScheduledQueryManager
from bigquery_sync.app.utils.dependency_graph import DependencyGraph
from bigquery_sync.app.utils.utils import get_dependency_views_dict
from google.api_core.exceptions import NotFound as BigQueryDataNotFound, BadRequest as BigQueryBadRequest
from bigquery_sync.app.exceptions.exceptions import InvalidScheduledName
from bigquery_sync.app.config.config import DEFAULT_SCHEDULED_CONFIG_JSON


class SyncGitBigqueryManager():
    def __init__(self, git_manager: GitManager, projects: list, projects_root_path: str,
                 service_account_file_path=None, do_not_fetch :dict = None):
        self.git_manager = git_manager
        self.do_not_fetch = do_not_fetch
        self.projects = [projects] if isinstance(projects, str) else projects
        self.projects_root_path = projects_root_path
        self.service_account_file_path = service_account_file_path

    def sync_from_bigquery_to_git(self, commit_and_push=True,
                                  only_fetch: dict = None,
                                  message='[AUTO] Fetch the following updates from BigQuery', include_files_in_message=True):

        for i in range(RETRY_COUNT):
            raise_push_error = (i == RETRY_COUNT - 1)

            if commit_and_push:
                self.git_manager.git_pull()
            

            for project in self.projects:
                only_fetch_datasets = None
                if only_fetch:
                    if not  only_fetch.get(project):
                        continue
                    only_fetch_datasets = [key for key, value in only_fetch.items() if value]
                
                
                do_not_fetch_dataset = self.do_not_fetch.get(project)
                if do_not_fetch_dataset:
                    exclude_datasets = [key for key, value in do_not_fetch_dataset.items() if value]
                    
                bigquery_view_manager = BigQueryViewManager(project=project, project_root_path=self.projects_root_path,
                                                            service_account_file_path=self.service_account_file_path
                                                            )
                
                bigquery_view_manager.fetch_views(datasets=only_fetch_datasets,excluded_datasets= exclude_datasets)
                scheduled_query_manager = ScheduledQueryManager(project=project,
                                                                project_root_path=self.projects_root_path,
                                                                service_account_file_path=self.service_account_file_path,
                                                                git_manager=self.git_manager
                                                                )
                scheduled_query_manager.fetch_scheduled_queries()

                if not commit_and_push:
                    break

            if commit_and_push:
                is_committed = self.git_manager.git_commit(message=message,
                                                           include_files_in_message=include_files_in_message)
                if not is_committed:
                    break
                is_pushed = self.git_manager.git_push(raise_push_error=raise_push_error, reset_on_error=True)
                if is_pushed:
                    break

    def sync_from_git_to_bigquery(self, old_ref=None, new_ref=None, branch_name=None):

        if branch_name == 'master' and old_ref != new_ref:
            diff_staged_files_by_project = self.git_manager.get_staged_files_dict(path=self.projects_root_path,
                                                                                  old_ref=old_ref, new_ref=new_ref)
            for project, diff_file_status_dict in diff_staged_files_by_project.items():
                bigquery_view_manager = BigQueryViewManager(project=project, project_root_path=self.projects_root_path)
                scheduled_query_manager = ScheduledQueryManager(project=project,
                                                                project_root_path=self.projects_root_path,
                                                                service_account_file_path=self.service_account_file_path,
                                                                git_manager=self.git_manager
                                                                )
                dependency_views_dict = get_dependency_views_dict(diff_file_status_dict=diff_file_status_dict,
                                                                  check_status=[self.git_manager.STATUS_ADD,
                                                                                self.git_manager.STATUS_MODIFY,
                                                                                self.git_manager.STATUS_RENAME_TO])
                dependency_graph = DependencyGraph(dependency_nodes_dict=dependency_views_dict)
                ordered_dependency_queries = dependency_graph.topological_sort()
                scheduled_file = {}
                for file_path, status in diff_file_status_dict.items():
                    file_path_without_extension = os.path.splitext(file_path)[0]
                    dataset, view = file_path.split('/')[-2:]

                    if os.path.splitext(file_path)[1] not in ['.sql', '.json']:
                        continue

                    if SCHEDULED_QUERIES == dataset:
                        json_file_path = f"{file_path_without_extension}.json"
                        if not os.path.exists(json_file_path):
                            with open(json_file_path, 'w') as json_file:
                                json.dump(DEFAULT_SCHEDULED_CONFIG_JSON, json_file, indent=4)

                        if file_path_without_extension not in scheduled_file:
                            scheduled_file[file_path_without_extension] = file_path
                            self.__process_file_in_git(bigquery_view_manager, scheduled_query_manager, project, old_ref,
                                                       new_ref, file_path=file_path, status=status,
                                                       is_scheduled_file=True)

                    elif status in [self.git_manager.STATUS_DELETE,
                                    self.git_manager.STATUS_RENAME_FROM]:
                        self.__process_file_in_git(bigquery_view_manager, scheduled_query_manager, project, old_ref,
                                                   new_ref, file_path=file_path, status=status, is_scheduled_file=False)
                    else:
                        print('Ignoring file: {}'.format(file_path))

                for file_path in ordered_dependency_queries:
                    if os.path.splitext(file_path)[1] not in ['.sql']:
                        continue
                    self.__process_file_in_git(bigquery_view_manager, scheduled_query_manager, project, old_ref,
                                               new_ref, file_path=file_path, status=diff_file_status_dict[file_path],
                                               is_scheduled_file=False)

    def __process_file_in_git(self, bigquery_view_manager, scheduled_query_manager, project, old_ref, new_ref,
                              file_path, status, is_scheduled_file=False):
        dataset, view = file_path.split('/')[-2:]
        file_name = os.path.splitext(file_path.split('/')[-1])[0]

        try:
            if not is_scheduled_file:
                if status in [self.git_manager.STATUS_DELETE, self.git_manager.STATUS_RENAME_FROM]:
                    print('Deleting view {}.{}.{}'.format(project, dataset, view), end=' ')
                    bigquery_view_manager.delete_view(dataset=dataset, view=view)
                    print('[SUCCESS]')
                else:
                    print('Creating or updating view {}.{}.{}'.format(project, dataset, view), end=' ')
                    bigquery_view_manager.create_or_update_view(dataset=dataset, view=view, file_path=file_path)
                    print('[SUCCESS]')
            else:
                if status == self.git_manager.STATUS_DELETE:
                    print('Deleting scheduled query {}.{}'.format(project, file_name), end=' ')
                    scheduled_query_manager.delete_scheduled_query(old_ref=old_ref, new_ref=new_ref,
                                                                   file_path=file_path)
                    print('[SUCCESS]')
                elif status in [self.git_manager.STATUS_MODIFY,
                                self.git_manager.STATUS_RENAME_TO]:
                    print('Updating scheduled query {}.{}'.format(project, file_name), end=' ')
                    try:
                        scheduled_query_manager.update_scheduled_query(file_name=file_name)
                    except (InvalidScheduledName, BigQueryDataNotFound):
                        print(' Scheduled query {}.{} not valid for update. Try to create'.format(project, file_name),
                              end=' ')
                        scheduled_query_manager.create_scheduled_query(file_name=file_name)

                elif status == self.git_manager.STATUS_ADD:
                    scheduled_query_manager.create_scheduled_query(file_name=file_name)

        except FileNotFoundError as err:
            print('[FAILED] FileNotFoundError')
            print(str(err))
        except BigQueryDataNotFound as err:
            print('[FAILED] BigQueryDataNotFound')
            scheduled_query_manager.create_scheduled_query(file_name=file_name)
        except BigQueryBadRequest as err:
            print('[FAILED] BigQueryBadRequest')
            print(err.errors[0]['message'])
