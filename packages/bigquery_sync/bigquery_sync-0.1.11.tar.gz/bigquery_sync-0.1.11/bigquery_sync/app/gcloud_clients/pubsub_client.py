import google.auth
from google.oauth2 import service_account
import logging
from google.cloud import pubsub_v1
from google.api_core import exceptions


class PubSubClient(object):

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

        self.client = pubsub_v1.PublisherClient(credentials=credentials)

        self.logger = logging.getLogger(__name__)

    def get_pubsub_topic(self, project_id, topic_id):
        topic_path = self.client.topic_path(project_id, topic_id)
        try:
            return self.client.get_topic(request={"topic": topic_path})
        except exceptions.NotFound:
            print(f"Topic does not exist: {topic_path}")
            return None

    def create_pubsub_topic(self, project_id, topic_id):
        topic_path = self.client.topic_path(project_id, topic_id)
        topic = self.get_pubsub_topic(project_id, topic_id)
        if topic:
            return topic
        try:
            topic = self.client.create_topic(request={"name": topic_path})
            print(f"Created Pub/Sub topic: {topic.name}")
            return topic
        except Exception as e:
            print(f"Error creating Pub/Sub topic: {e}")
