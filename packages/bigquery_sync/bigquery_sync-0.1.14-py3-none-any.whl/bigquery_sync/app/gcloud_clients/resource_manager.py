import google.auth
from google.oauth2 import service_account
import logging
from google.cloud import resourcemanager_v3


class ResourceManager(object):

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
        self.resource_client = resourcemanager_v3.ProjectsClient(credentials=credentials)
        self.logger = logging.getLogger(__name__)

    def get_project_number(self, project_id):
        # Create a client for the Resource Manager
        try:
            # Get the project details
            project = self.resource_client.get_project(name=f"projects/{project_id}")

            # Return the project number
            return project.name.split('/')[-1]
        except Exception as e:
            print(f"Error retrieving project number: {e}")
            return None
