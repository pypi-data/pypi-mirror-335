import os
import re
import simplejson
from bigquery_sync.app.gcloud_clients.bigquery_client import BigQueryClient
from bigquery_sync.app.gcloud_clients.datatransfer_client import DataTransferClient
from bigquery_sync.app.gcloud_clients.pubsub_client import PubSubClient

from bigquery_sync.app.config.config import SCHEDULED_QUERIES
from bigquery_sync.app.utils.utils import format_snake_case, create_dir
from bigquery_sync.app.exceptions.exceptions import InvalidScheduledConfigError, InvalidScheduledName
from bigquery_sync.app.managers.git_manager import GitManager
from bigquery_sync.app.gcloud_clients.resource_manager import ResourceManager


class ScheduledQueryManager(object):
    WEEKLY_MAP = {'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6, 'sun': 7}
    WEEKLY_REVERT_MAP = {v: k for k, v in WEEKLY_MAP.items()}
    UPDATE_MASK = {
        'paths': ['destination_dataset_id', 'display_name', 'schedule', 'params', 'notification_pubsub_topic']}

    def __init__(self, project, project_root_path, service_account_file_path, git_manager: GitManager):
        self.dtc = DataTransferClient(project=project, service_account_file_path=service_account_file_path)
        self.pubsub_client = PubSubClient(project=project, service_account_file_path=service_account_file_path)
        self.project = project
        self.project_root_path = project_root_path
        self.git_manager = git_manager
        self.service_account_file_path = service_account_file_path
        self.exist_pubsub_topic = set()

    def fetch_scheduled_queries(self):
        dtc = self.dtc
        project = self.project
        project_path = self.project_root_path + '/' + project
        create_dir(path=project_path)
        scheduled_queries_path = project_path + '/' + SCHEDULED_QUERIES
        create_dir(path=scheduled_queries_path)
        scheduled_query_configs = dtc.list_scheduled_query_configs()
        existed_scheduled_query_configs = set()
        for scheduled_query_config in scheduled_query_configs:
            existed_scheduled_query_configs.add(format_snake_case(scheduled_query_config.display_name))
            self.output_scheduled_query_config(scheduled_query_config=scheduled_query_config,
                                               schedule_queries_path=scheduled_queries_path)

        self.__remove_invalid_scheduled_query_configs(path=scheduled_queries_path,
                                                      file_list=existed_scheduled_query_configs)

    def __remove_invalid_scheduled_query_configs(self, path, file_list):
        files = os.listdir(path)
        for file in files:
            file_path = path + '/' + file
            if os.path.splitext(file)[1] in ['.json', '.sql'] and os.path.splitext(file)[0] not in file_list:
                os.remove(file_path)

    def output_scheduled_query_config(self, scheduled_query_config, schedule_queries_path):
        output_dict = {'name': scheduled_query_config.name}
        destination = {
            'dataset': scheduled_query_config.destination_dataset_id,
            'table': scheduled_query_config.params.get('destination_table_name_template', None)
        }
        write_mode = None

        if 'write_disposition' in scheduled_query_config.params:
            write_mode = scheduled_query_config.params['write_disposition'].split('_')[1].lower()
        configuration = {
            'schedule': self.create_schedule_dict(scheduled_query_config.schedule),
            'destination': destination,
            'write_mode': write_mode,
            'notification_pubsub_topic': scheduled_query_config.notification_pubsub_topic.split('/')[-1]
        }
        output_dict['configuration'] = configuration
        formatted_filename = format_snake_case(scheduled_query_config.display_name)
        with open(schedule_queries_path + '/' + formatted_filename + '.json', 'w') as output_file:
            output_file.write(simplejson.dumps(output_dict, indent=4))
        with open(schedule_queries_path + '/' + formatted_filename + '.sql', 'w') as output_file:
            output_file.write(scheduled_query_config.params['query'])

    def create_schedule_dict(self, schedule):
        schedule_words = schedule.split(' ')
        if schedule_words[0] == 'every':
            if ':' in schedule_words[2]:
                if schedule_words[1] == 'day':
                    return self.__create_schedule_dict(schedule_type='hourly', repeat=24,
                                                       time_hour=int(schedule_words[2].split(':')[0]),
                                                       time_minute=int(schedule_words[2].split(':')[1]))
                else:  # weekly
                    return self.__create_schedule_dict(schedule_type='weekly',
                                                       repeat=[self.WEEKLY_MAP[word] for word in
                                                               schedule_words[1].split(',')],
                                                       time_hour=int(schedule_words[2].split(':')[0]),
                                                       time_minute=int(schedule_words[2].split(':')[1]))
            elif schedule_words[2] == 'hours':
                return self.__create_schedule_dict(schedule_type='hourly', repeat=int(schedule_words[1]))
        elif schedule_words[2] == 'month':
            return self.__create_schedule_dict(schedule_type='monthly',
                                               repeat=[int(day) for day in schedule_words[0].split(',')],
                                               time_hour=int(schedule_words[3].split(':')[0]),
                                               time_minute=int(schedule_words[3].split(':')[1]))
        else:
            raise InvalidScheduledConfigError('Invalid format of schedule in configuration, please contact engineer.')

    def __create_empty_schedule(self):
        return {
            'repeat': {'hourly': None, 'weekly': None, 'monthly': None},
            'time': {'hour': None, 'minute': None}
        }

    def __create_schedule_dict(self, schedule_type, repeat, time_hour=None, time_minute=None):
        schedule = self.__create_empty_schedule()
        schedule['repeat'][schedule_type] = repeat
        schedule['time']['hour'] = time_hour
        schedule['time']['minute'] = time_minute
        return schedule

    def create_schedule_string(self, schedule):
        if schedule['repeat']['hourly'] is not None:
            if schedule['repeat']['hourly'] != 24 or None in (
                    schedule['time']['hour'], schedule['time']['minute']):
                return 'every ' + str(schedule['repeat']['hourly']) + ' hours'
            else:
                return 'every day ' + str(schedule['time']['hour']) + ':' + str(schedule['time']['minute']).zfill(2)
        elif schedule['repeat']['weekly'] is not None:
            return 'every ' + ','.join([self.WEEKLY_REVERT_MAP[i] for i in schedule['repeat']['weekly']]) + ' ' + \
                str(schedule['time']['hour']) + ':' + str(schedule['time']['minute']).zfill(2)
        elif schedule['repeat']['monthly'] is not None:
            return ','.join([str(i) for i in schedule['repeat']['monthly']]) + ' of month ' + \
                str(schedule['time']['hour']) + ':' + str(schedule['time']['minute']).zfill(2)

    def validate_scheduled_job_config(self, file_path):
        with open(file_path, 'r') as json_file:
            config_dict = simplejson.load(json_file)
        file_name = os.path.splitext(file_path.split('/')[-1])[0]
        correct_file_name = format_snake_case(config_dict['configuration']['display_name'])
        repeat = config_dict['configuration']['schedule']['repeat']
        time = config_dict['configuration']['schedule']['time']
        destination = config_dict['configuration']['destination']
        write_mode = config_dict['configuration']['write_mode']

        if file_name != correct_file_name or not os.path.exists(os.path.splitext(file_path)[0] + '.sql'):
            raise InvalidScheduledConfigError(
                "Filename doesn't match display name. Should be renamed to {filename}.json and {filename}.sql and commit again.".format(
                    filename=correct_file_name))

        if sum(v is not None for v in repeat.values()) != 1:
            raise InvalidScheduledConfigError('Invalid number of repeat values, should be only one key with value.')

        if repeat.get('hourly'):
            if not isinstance(repeat['hourly'], int):
                raise InvalidScheduledConfigError('Invalid hourly value, should be integer.')
            if repeat['hourly'] <= 0:
                raise InvalidScheduledConfigError('Invalid hourly value, should be a positive integer.')
            if repeat['hourly'] != 24 and (time['hour'] is not None or time['minute'] is not None):
                raise InvalidScheduledConfigError('Hourly scheduled query should not have time value.')

        if repeat.get('weekly'):
            self.check_weekly_and_monthly(repeat=repeat, schedule_type='weekly', range_min=1, range_max=7)

        if repeat.get('monthly'):
            self.check_weekly_and_monthly(repeat=repeat, schedule_type='monthly', range_min=1, range_max=31)

        if repeat.get('hourly') is None or repeat.get('hourly') == 24:
            if time['hour'] is None or time['minute'] is None:
                raise InvalidScheduledConfigError('No time value in this scheduled query configuration.')
            if time['hour'] >= 24 or time['hour'] < 0:
                raise InvalidScheduledConfigError('Invalid time hour value. RANGE->[0,23].')
            if time['minute'] >= 60 or time['minute'] < 0:
                raise InvalidScheduledConfigError('Invalid time minute value. RANGE->[0,59]')

        if re.match(r'^([A-z0-9_$]*|{([A-z0-9\"%+\-|\\\.;])+})*$', destination['table']) is None:
            raise InvalidScheduledConfigError('Invalid table name.')

        client = BigQueryClient(project=self.project)
        if destination['dataset'] not in [k.dataset_id for k in client.list_datasets()]:
            raise InvalidScheduledConfigError('Not found dataset {}:{}.'.format(self.project, destination['dataset']))
        if write_mode not in ['truncate', 'append']:
            raise InvalidScheduledConfigError(
                'Invalid write mode, should be truncate or append'.format(self.project, destination['dataset']))

        if config_dict.get('name') is None:
            error_message = 'Please run following command to create a scheduled query and commit again:\n'
            command = '{}/runscript.py admin.create_scheduled_query {} {}'.format(self.project_root_path, self.project,
                                                                                  file_name)
            raise InvalidScheduledConfigError(error_message + command)

    def check_weekly_and_monthly(self, repeat, schedule_type, range_min, range_max):
        if not isinstance(repeat[schedule_type], list):
            raise InvalidScheduledConfigError('Invalid {} type, it should be a list.'.format(schedule_type))
        if not all(range_max >= i >= range_min for i in repeat[schedule_type]):
            raise InvalidScheduledConfigError(
                'Invalid {} value. RANGE->[{},{}].'.format(schedule_type, range_min, range_max))

    def delete_scheduled_query(self, old_ref, new_ref, file_path):
        dtc = self.dtc

        config_name = self.__get_config_name(self.git_manager.git.diff(old_ref, new_ref, '--', file_path))
        dtc.delete_transfer_config(name=config_name)

    def update_scheduled_query(self, file_name):
        dtc = self.dtc
        json_dict, query = self.__read_json_and_sql(file_name=file_name)
        json_dict['configuration']['display_name'] = file_name

        if 'name' not in json_dict:
            raise InvalidScheduledName('No name field in configuration.')
        project_number_from_file = json_dict['name'].split('/')[1]
        project_number = ResourceManager(service_account_file_path=self.service_account_file_path).get_project_number(
            self.project)

        if project_number_from_file != project_number:
            raise InvalidScheduledName('Invalid project number.')

        transfer_config = dtc.get_transfer_config(name=json_dict['name'])

        transfer_config = self.__update_config(transfer_config=transfer_config,
                                               configuration=json_dict['configuration'],
                                               query=query)
        dtc.update_transfer_config(transfer_config=transfer_config, update_mask=self.UPDATE_MASK)

    def create_scheduled_query(self, file_name):
        dtc = self.dtc
        json_dict, query = self.__read_json_and_sql(file_name=file_name)
        json_dict['configuration']['display_name'] = file_name
        config_dict = self.__create_config_dict(configuration=json_dict['configuration'], query=query)
        return dtc.create_transfer_config(config_dict=config_dict)

    def __read_json_and_sql(self, file_name):
        project = self.project
        scheduled_query_path = self.project_root_path + '/' + project + '/' + SCHEDULED_QUERIES + '/' + file_name
        with open(scheduled_query_path + '.json', 'r') as json_file:
            json_dict = simplejson.load(json_file)
        with open(scheduled_query_path + '.sql', 'r') as sql_file:
            query = sql_file.read()
        return json_dict, query

    def __update_config(self, transfer_config, configuration, query):
        transfer_config.display_name = configuration['display_name']
        transfer_config.schedule = self.create_schedule_string(configuration['schedule'])

        if configuration['destination']['dataset'] and configuration['destination']['table']:
            transfer_config.destination_dataset_id = configuration['destination']['dataset']
            transfer_config.params['destination_table_name_template'] = configuration['destination']['table']

        transfer_config.params['query'] = query

        if configuration['write_mode']:
            transfer_config.params['write_disposition'] = 'WRITE_' + configuration['write_mode'].upper()

        if configuration['notification_pubsub_topic']:
            if configuration['notification_pubsub_topic'] not in self.exist_pubsub_topic:
                topic = self.pubsub_client.create_pubsub_topic(self.project, configuration['notification_pubsub_topic'])
                self.exist_pubsub_topic.add(topic.name)
            transfer_config.notification_pubsub_topic = self.pubsub_client.client.topic_path(self.project,
                                                                                             configuration[
                                                                                                 'notification_pubsub_topic'])
        return transfer_config

    def __get_config_name(self, string_data):
        return re.search(r'projects\S+/locations/\S+/transferConfigs/[^"]+', string_data)[0]

    def __create_config_dict(self, configuration, query):
        config_dict = {
            "display_name": configuration['display_name'],
            "data_source_id": "scheduled_query",
            "params": {
                "query": query,
                "partitioning_field": "",
            },
            "schedule": self.create_schedule_string(configuration['schedule']),
        }
        if configuration['write_mode']:
            config_dict['params']['write_disposition'] = 'WRITE_' + configuration['write_mode'].upper()

        if configuration['destination']['dataset']:
            config_dict['destination_dataset_id'] = configuration['destination']['dataset']

        if configuration['destination']['table']:
            config_dict['params']['destination_table_name_template'] = configuration['destination']['table']

        if configuration['notification_pubsub_topic']:
            if configuration['notification_pubsub_topic'] not in self.exist_pubsub_topic:
                topic = self.pubsub_client.create_pubsub_topic(self.project, configuration['notification_pubsub_topic'])
                self.exist_pubsub_topic.add(topic.name)
            config_dict['notification_pubsub_topic'] = self.pubsub_client.client.topic_path(self.project,
                                                                                            configuration[
                                                                                                'notification_pubsub_topic'])
        return config_dict
