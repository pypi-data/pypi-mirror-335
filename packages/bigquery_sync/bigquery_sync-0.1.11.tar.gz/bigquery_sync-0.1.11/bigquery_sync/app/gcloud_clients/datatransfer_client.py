import google.auth
from google.oauth2 import service_account
from google.cloud import bigquery_datatransfer_v1
import logging


class DataTransferClient(object):

    def __init__(self, service_account_file_path=None, project=None, location='US'):
        self.logger = logging.getLogger(__name__)
        self.project = project
        self.location = location

        # Load credentials
        if service_account_file_path:
            # Assuming user is a path to the service account key file
            credentials = service_account.Credentials.from_service_account_file(service_account_file_path)
        else:
            # Use default credentials
            credentials, _ = google.auth.default()

        print(f"User: {credentials.service_account_email}")


        # Initialize the BigQuery client
        self.client = bigquery_datatransfer_v1.DataTransferServiceClient(credentials=credentials)
        self.logger = logging.getLogger(__name__)

    def list_scheduled_query_configs(self):
        parent = 'projects/{}/locations/{}'.format(self.project, self.location)
        return [transfer_config for transfer_config in self.client.list_transfer_configs(parent=parent)
                if transfer_config.data_source_id == 'scheduled_query']

    def update_transfer_config(self, transfer_config, update_mask):
        self.client.update_transfer_config(transfer_config=transfer_config, update_mask=update_mask)

    def get_transfer_config(self, name):
        return self.client.get_transfer_config(name=name)

    def delete_transfer_config(self, name):
        return self.client.delete_transfer_config(name=name)

    def create_transfer_config(self, config_dict):
        parent = 'projects/{}/locations/{}'.format(self.project, self.location)
        transfer_config = google.protobuf.json_format.ParseDict(
            config_dict,
            bigquery_datatransfer_v1.types.TransferConfig()._pb,
        )
        return self.client.create_transfer_config(parent=parent, transfer_config=transfer_config)
