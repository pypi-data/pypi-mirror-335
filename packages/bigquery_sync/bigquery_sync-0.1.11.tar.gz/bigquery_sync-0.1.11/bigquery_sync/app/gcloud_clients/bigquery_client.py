
from google.oauth2 import service_account
import google.auth
import logging

from google.cloud import bigquery # pylint: disable=import-error
from google.cloud.exceptions import Conflict, ServerError, ClientError # pylint: disable=import-error
from google.cloud.exceptions import NotFound, BadRequest # pylint: disable=import-error
from google.api_core import retry, exceptions # pylint: disable=import-error


import datetime
import logging
import os
import pytz
import uuid
import itertools
from concurrent.futures import TimeoutError

from enum import Enum, unique
import http.client as http_client



class BigQueryJobException(Exception):
    pass


class BigQueryPendingException(Exception):
    pass


class BigQueryServerError(ServerError):
    pass


class BigQueryClientError(ClientError):
    pass


class BigQueryStreamException(Exception):
    pass


TIMEOUT_HOURS = 90 * 24
TIMEOUT_SECONDS = 90 * 24 * 60 * 60


@unique
class UploadFileType(Enum):
    CSV = bigquery.job.SourceFormat.CSV
    JSON = bigquery.job.SourceFormat.NEWLINE_DELIMITED_JSON


class BigQueryClient(object):

    def __init__(self, service_account_file_path=None, project=None):
        # Define the scopes
        scopes = [
            "https://www.googleapis.com/auth/bigquery",
            "https://www.googleapis.com/auth/drive"  # Add Google Drive scope
        ]
        
        # Load credentials
        if service_account_file_path:
            # Assuming user is a path to the service account key file
            credentials = service_account.Credentials.from_service_account_file(service_account_file_path, scopes=scopes)
        else:
            # Use default credentials
            credentials, _ = google.auth.default(scopes=scopes)
        
        # Initialize the BigQuery client
        self.client = bigquery.Client(credentials=credentials, project=project)
        self.logger = logging.getLogger(__name__)

    @property
    def project(self):
        return self.client.project

    def does_dataset_exist_by_ref(self, dataset_ref):
        try:
            self.client.get_dataset(dataset_ref)
        except NotFound:
            return False
        return True

    def does_dataset_exist(self, dataset_name):
        try:
            dataset_ref = self.client.dataset(dataset_name)
        except NotFound:
            return False
        return self.does_dataset_exist_by_ref(dataset_ref)

    def create_dataset(self, dataset_name, project=None, labels=None):
        dataset = bigquery.Dataset('{project}.{dataset}'.format(
            project=project or self.client.project or 'ata-analytics', dataset=dataset_name
        ))
        if labels:
            dataset.labels = labels
        return self.client.create_dataset(dataset)

    def delete_dataset(self, dataset_name, dataset_contents=False, not_found_ok=True):
        return self.client.delete_dataset(dataset=dataset_name, delete_contents=dataset_contents, not_found_ok=not_found_ok)

    def does_table_exist_by_ref(self, table_ref):
        try:
            self.client.get_table(table_ref)
        except NotFound:
            return False
        return True

    def does_table_exist(self, dataset_name, table_name):
        try:
            dataset_ref = self.client.dataset(dataset_name)
            table_ref = dataset_ref.table(table_name)
        except NotFound:
            return False
        return self.does_table_exist_by_ref(table_ref)

    def get_table(self, dataset_name, table_name):
        dataset_ref = self.client.dataset(dataset_name)
        table_ref = dataset_ref.table(table_name)
        return self.client.get_table(table_ref)

    def move_table(self, source_dataset_name, source_table_name, destination_dataset_name, destination_table_name):
        return self._move_table(source_dataset_name, source_table_name, destination_dataset_name, destination_table_name, delete=True)

    def copy_table(self, source_dataset_name, source_table_name, destination_dataset_name, destination_table_name):
        return self._move_table(source_dataset_name, source_table_name, destination_dataset_name, destination_table_name, delete=False)

    def _move_table(self, source_dataset_name, source_table_name, destination_dataset_name, destination_table_name, delete):
        self.logger.debug("Moving/Copying table %s to %s in dataset %s" % (source_table_name, destination_table_name, source_dataset_name))
        source_dataset_ref = self.client.dataset(source_dataset_name)
        source_table_ref = source_dataset_ref.table(source_table_name)

        destination_dataset_ref = self.client.dataset(destination_dataset_name)
        destination_table_ref = destination_dataset_ref.table(destination_table_name)

        job_config = bigquery.CopyJobConfig()
        job_config.write_disposition = bigquery.job.WriteDisposition.WRITE_TRUNCATE

        job = self.client.copy_table(source_table_ref, destination_table_ref, job_config=job_config)
        job.result()

        if delete is True:
            self.client.delete_table(source_table_ref)
        return job

    def __set_table_partitioning(self, table,
                                 time_partitioning=False, time_partitioning_field=None,
                                 range_partitioning=False, range_partitioning_field=None,
                                 range_partitioning_start=None, range_partitioning_end=None,
                                 range_partitioning_interval=None):
        if time_partitioning:
            if isinstance(time_partitioning, bigquery.TimePartitioning):
                table.time_partitioning = time_partitioning
            else:
                table.time_partitioning = bigquery.TimePartitioning(
                    field=time_partitioning_field
                )
        if range_partitioning:
            if isinstance(range_partitioning, bigquery.RangePartitioning):
                table.range_partitioning = range_partitioning
            else:
                table.range_partitioning = bigquery.RangePartitioning(
                    field=range_partitioning_field,
                    range_=bigquery.PartitionRange(
                        start=range_partitioning_start,
                        end=range_partitioning_end,
                        interval=range_partitioning_interval
                    )
                )


    def copy_table_schema_only(self, source_dataset_name, source_table_name,
                               destination_dataset_name, destination_table_name,
                               time_partitioning=False, time_partitioning_field=None,
                               range_partitioning=False, range_partitioning_field=None,
                               range_partitioning_start=None, range_partitioning_end=None,
                               range_partitioning_interval=None, clustering_fields=None):
        source_dataset_ref = self.client.dataset(source_dataset_name)
        source_table_ref = source_dataset_ref.table(source_table_name)
        source_table = self.client.get_table(source_table_ref)

        destination_dataset_ref = self.client.dataset(destination_dataset_name)
        destination_table_ref = destination_dataset_ref.table(destination_table_name)

        table = bigquery.Table(destination_table_ref)
        table.schema = source_table.schema

        table.time_partitioning = source_table.time_partitioning
        table.range_partitioning = source_table.range_partitioning
        self.__set_table_partitioning(
            table=table, time_partitioning=time_partitioning, time_partitioning_field=time_partitioning_field,
            range_partitioning=range_partitioning, range_partitioning_field=range_partitioning_field,
            range_partitioning_start=range_partitioning_start, range_partitioning_end=range_partitioning_end,
            range_partitioning_interval=range_partitioning_interval
        )
        table.clustering_fields = clustering_fields

        # If it already exists we don't care, Conflict comes back when it exists.
        try:
            self.client.create_table(table)
        except Conflict:
            pass

    def upload_file_to_table(self, dataset_name, table_name, filename, filetype, truncate=False, schema=None, async_upload=False, **kwargs):
        with open(filename, "rb") as handle:
            return self.upload_handle_to_table(dataset_name=dataset_name, table_name=table_name, file_handle=handle, filetype=filetype, truncate=truncate, schema=schema, async_upload=async_upload, **kwargs)

    def upload_handle_to_table(self, dataset_name, table_name, file_handle, filetype, schema=None, truncate=False, async_upload=False, **kwargs):
        # Backwards compatibility until fixed everywhere
        if 'async' in kwargs:
            async_upload = kwargs['async']
        assert isinstance(filetype, UploadFileType)

        file_handle.seek(0, os.SEEK_END)
        length = file_handle.tell()
        file_handle.seek(0, os.SEEK_SET)

        write_disposition = bigquery.job.WriteDisposition.WRITE_TRUNCATE if truncate is True else bigquery.job.WriteDisposition.WRITE_APPEND

        self.logger.debug("%s file of size %s to %s.%s" % ("Overwriting" if truncate else "Appending", length, dataset_name, table_name))

        dataset_ref = self.client.dataset(dataset_name)

        # So, technically upload_from_file supports being called on a non-existent table, with create disposition CREATE_IF_NEEDED (default).
        # and a schema defined (required). Buuuuuut, it isn't supported to send a partitioning_type, so, you can't really create all table types. :(
        if schema is not None:
            self.create_table_if_missing(dataset_name, table_name, schema=schema, time_partitioning="$" in table_name)
        table_ref = dataset_ref.table(table_name)

        # Heavy usage has shown infrequent occurences of BadStatusLine on upload
        # Solution: Retry on failure. I only expect a single failure, but don't want to retry forever
        count = 0
        job_id = str(uuid.uuid4())

        job_config = bigquery.LoadJobConfig()
        job_config.source_format = filetype.value
        job_config.write_disposition = bigquery.job.WriteDisposition.WRITE_TRUNCATE if truncate else bigquery.job.WriteDisposition.WRITE_APPEND

        while True:
            try:
                # See https://cloud.google.com/bigquery/loading-data for other formats
                self.logger.info("lowlevel - starting upload to: %s.%s, length: %s" % (dataset_name, table_name, length))
                job = self.client.load_table_from_file(file_handle, table_ref, job_id=job_id, job_config=job_config)
                self.logger.info("upload job started: %s to %s.%s" % (job.job_id, dataset_name, table_name))
                break
            except http_client.BadStatusLine as e:
                self.logger.error("BAD STATUS LINE! destination: %s.%s length: %s" % (dataset_name, table_name, length))
                if count > 10:
                    raise
                count += 1
            except Conflict as e:
                # This should mean a duplicate upload, in which case we can go assume this was already uploaded and not worry about it.
                self.logger.error("Exception: %s, Duplicate upload? job_name: %s to %s.%s" % (e, job_id, dataset_name, table_name))
                # log and fetch job so we can exit like everything went ok
                job = self.get_job(job_id)
                self.logger.warn("upload job started (duplicate): %s to %s.%s" % (job.job_id, dataset_name, table_name))
                break
            except Exception as e:
                self.logger.error("Some exception on upload to %s.%s (%s): %s" % (dataset_name, table_name, "raising" if count > 5 else "retrying", e))
                # Going to retry MORE
                if count > 5:
                    raise
                count += 1
                # in case we were part way into streaming the file, i think. Symptom - ValueError(u'Stream must be at beginning.')
                file_handle.seek(0, os.SEEK_SET)

        if async_upload:
            return job
        else:
            # Could do something with @retry.Retry instead to be cleaner
            try:
                job.result()
            except exceptions.InternalServerError:
                job.result()
            except Exception as e:
                logging.error("Exception when checking job status: %s job_id: %s" % (e, job_id))
                raise
            return job

    @retry.Retry(predicate=retry.if_exception_type((exceptions.Forbidden, exceptions.InternalServerError, exceptions.TooManyRequests)))
    def query(self, query, wait_for_completion=True, dry_run=False, use_legacy_sql=False, query_parameters=None, labels=None):
        self.logger.info('querying with query:\n%s' % query)

        job_config = bigquery.QueryJobConfig()
        job_config.use_legacy_sql = use_legacy_sql
        job_config.dry_run = dry_run
        if query_parameters is not None:
            job_config.query_parameters = query_parameters
        
        if labels is not None:
            job_config.labels = labels
            
        query_job = self.client.query(query, job_config=job_config)

        exception = None
        try:
            # If we've got a basic error like syntax or missing table this will not timeout but will return the exception
            exception = query_job.exception(timeout=1)
        except TimeoutError:
            pass
        if exception is not None:
            raise exception


        # If dry_run, after just .begin() the job is done, and, the job_id doesn't exist in bigquery, so you can't fetch the job result
        if wait_for_completion and not dry_run:
            query_job.result()

        return query_job

    def query_to_df(self, query, drop=None, index=None, wait_for_completion=True, dry_run=False, **kwargs):
        query_job = self.query(query=query, **kwargs)
        if not wait_for_completion or dry_run:
            return None
        df = query_job.result().to_dataframe()
        if drop:
            df = df.drop(columns=drop)
        if index:
            df = df.set_index(keys=index)
        return df

    def query_to_list(self, query, flat=False, wait_for_completion=True, dry_run=False, **kwargs):
        query_job = self.query(query=query, **kwargs)
        if not wait_for_completion or dry_run:
            return None

        retval = [row.values() for row in query_job.result()]
        if flat:
            retval_size = len(retval)
            retval = [val[0] for val in retval if len(val) == 1]
            if len(retval) != retval_size:
                raise ValueError('Query result with more than one columns cannot be flattened.')

        return retval

    def query_to_dict(self, query, wait_for_completion=True, dry_run=False, **kwargs):
        query_job = self.query(query=query, **kwargs)
        if not wait_for_completion or dry_run:
            return None

        result = query_job.result()
        retval = {column.name: [] for column in result.schema}
        for row in result:
            for column, value in row.items():
                retval[column].append(value)

        return retval

    def delete_table(self, dataset_name, table_name):
        dataset_ref = self.client.dataset(dataset_name)
        table_ref = dataset_ref.table(table_name)
        if self.does_table_exist_by_ref(table_ref):
            self.client.delete_table(table_ref)
            return True
        return False

    def list_datasets(self, label=None, value=None):
        pt = None
        params = {'page_token': pt, }

        if label is not None:
            dataset_filter = 'labels.%s' % label
            if value is not None:
                dataset_filter = '%s:%s' % (dataset_filter, value)
            params['filter'] = dataset_filter

        datasets = list(self.client.list_datasets(**params))
        return datasets

    def list_tables(self, dataset_name):
        dataset_ref = self.client.dataset(dataset_name)
        pt = None
        tables = list(self.client.list_tables(dataset_ref, page_token=pt))
        return tables

    def list_tables_by_prefix(self, dataset_name, prefix):
        tables = self.list_tables(dataset_name)

        return [x for x in tables if x.table_id.startswith(prefix)]

    def list_all_tables_with_partitions_near_limit(self, days_to_warn_in_advance):
        datasets = self.client.list_datasets()
        result = []
        default_partition_limit = 10000
        for dataset in datasets:
            num_of_tables = len(list(self.client.list_tables(dataset.dataset_id)))
            # Querying from INFORMATION_SCHEMA.PARTITIONS is limited to 1000 tables.
            # See https://cloud.google.com/bigquery/docs/information-schema-partitions
            if num_of_tables > 1000:
                raise ValueError('Cannot query from %s.%s.INFORMATION_SCHEMA.PARTITIONS.'
                                 'Over 1000 BigQuery tables - current table count %s'
                                 % (self.project, dataset.dataset_id, num_of_tables))
            query = f"""
            SELECT table_name, COUNT(*) as total_partitions
            FROM `{self.project}.{dataset.dataset_id}.INFORMATION_SCHEMA.PARTITIONS`
            GROUP BY table_name
            """
            query_job = self.client.query(query)
            query_result = query_job.result()
            for r in query_result:
                if r.total_partitions >= default_partition_limit - days_to_warn_in_advance:
                    result.append((f"{self.project}.{dataset.dataset_id}.{r.table_name}", r.total_partitions))
        return sorted(result, key=lambda t: t[-1], reverse=True)

    def get_job_bytes_processed(self, job, unit='b'):
        """
        Accepts units b, k, m, g
        conversion is 1000s
        """
        processed_bytes = int(job._properties['statistics']['totalBytesProcessed'])
        if unit == 'k':
            return processed_bytes / (1000.0)
        if unit == 'm':
            return processed_bytes / (1000.0 * 1000.0)
        if unit == 'g':
            return processed_bytes / (1000.0 * 1000.0 * 1000.0)
        return processed_bytes

    def get_query_bytes_processed(self, query, unit='b'):
        job = self.query(query, dry_run=True)
        return self.get_job_bytes_processed(job, unit=unit)

    def fetch_jobs_until(self, job_id=None, num_hours=TIMEOUT_HOURS):
        return list(self.iter_fetch_jobs_until(job_id, num_hours))

    def iter_fetch_jobs_until(self, job_id=None, num_hours=TIMEOUT_HOURS, state_filter=None):
        job_iterator = self.client.list_jobs(page_token=None, state_filter=state_filter, all_users=True)
        date = pytz.utc.localize(datetime.datetime.now() - datetime.timedelta(hours=num_hours))

        for job in job_iterator:
            if job_id == job.job_id or job.created < date:
                return
            yield job

    def is_native_schema_change(self, old_schema, new_schema):

        # deleting a column is not supported
        if len(old_schema) > len(new_schema):
            return False

        for old_field in old_schema:
            matches = [f for f in new_schema if f.name == old_field.name]

            # changing a column's name is not supported
            if len(matches) != 1:
                return False
            new_field = matches[0]

            # changing a column's mode (aside from relaxing REQUIRED columsn to NULLABLE) is not supported
            if old_field.mode != new_field.mode and (old_field.mode != 'REQUIRED' or new_field.mode != 'NULLABLE'):
                return False

            # changing a column's data type is not supported
            elif old_field.field_type != new_field.field_type:
                return False

        for new_field in new_schema:
            if [f for f in old_schema if f.name == new_field.name]:
                continue

            # adding a required column is not supported
            if new_field.mode != 'NULLABLE':
                return False

        return True

    def change_table_schema(self, dataset_name, table_name, new_schema):
        assert self.does_table_exist(dataset_name, table_name)

        dataset_ref = self.client.dataset(dataset_name)
        table_ref = dataset_ref.table(table_name)
        table = self.client.get_table(table_ref)

        if not self.is_native_schema_change(table.schema, new_schema):
            self.logger.error('not valid schema change %s to %s' % (table.schema, new_schema))
            return False

        table.schema = new_schema
        try:
            self.client.update_table(table, ['schema'])
        except BadRequest as e:
            self.logger.error('bad bigquery request to update table schema %s' % e)
            return False
        return True

    @retry.Retry(predicate=retry.if_exception_type((exceptions.Forbidden, exceptions.InternalServerError, exceptions.TooManyRequests)))
    def stream_rows(self, dataset_name, table_name, payload, insert_ids=None):
        """
        Insert rows into BigQuery using the Streaming API
        https://cloud.google.com/bigquery/streaming-data-into-bigquery

        :param dataset_name: Name of the dataset
        :param table_name: Name of the table
        :param payload: A list of dictionaries which contain the data of the row to be inserted
        :param insert_ids: An optional list of strings representing the 'insertId' of the corresponding payload
                           at the same index.  If specified, should be exactly the same length as payload.
        """
        if insert_ids is not None and len(payload) != len(insert_ids):
            raise ValueError("If specified, the length of insert_ids must equal payload")

        dataset_ref = self.client.dataset(dataset_name)
        table_ref = dataset_ref.table(table_name)

        for i in itertools.count(0, step=1):
            current_load = payload[i * 10000: (i + 1) * 10000]
            if not current_load:
                return

            current_insert_ids = insert_ids[i * 10000: (i + 1) * 10000] if insert_ids is not None else None

            max_attempts = 5
            for attempt_index in range(max_attempts):
                attempt_num = attempt_index + 1

                errors = self.client.insert_rows_json(table_ref, json_rows=current_load, row_ids=current_insert_ids)
                if not errors:
                    break

                log_func = self.logger.warning if attempt_num < max_attempts else self.logger.error
                for e in errors:
                    log_func("bigquery stream row ran into errors (attempt {attempt_num}/{max_attempts}): {e}".format(
                        attempt_num=attempt_num, max_attempts=max_attempts, e=e))
            else:
                raise BigQueryStreamException()

    @retry.Retry(predicate=retry.if_exception_type((exceptions.Forbidden, exceptions.InternalServerError, exceptions.TooManyRequests)))
    def query_into_table(
            self,
            query,
            destination_dataset_name,
            destination_table_name,
            wait_for_completion=False,
            use_legacy_sql=False,
            truncate=True,
            time_partitioning=False,
            time_partitioning_field=None,
            range_partitioning=False,
            range_partitioning_field=None,
            range_partitioning_start=None,
            range_partitioning_end=None,
            range_partitioning_interval=None,
            batch=False,
            clustering_fields=None,
            labels=None,
            **kwargs):

        # Backwards compatibility until everywhere is fixed
        if 'async' in kwargs:
            wait_for_completion = not kwargs['async']         

        destination_table_ref = self.client.dataset(destination_dataset_name).table(destination_table_name)

        self.logger.info('query into table %s.%s with query:\n%s' % (destination_dataset_name, destination_table_name, query))

        job_config = bigquery.QueryJobConfig()
        job_config.destination = destination_table_ref
        job_config.use_legacy_sql = use_legacy_sql
        job_config.write_disposition = bigquery.job.WriteDisposition.WRITE_TRUNCATE if truncate else bigquery.job.WriteDisposition.WRITE_APPEND
        job_config.priority = bigquery.job.QueryPriority.BATCH if batch else bigquery.job.QueryPriority.INTERACTIVE
    
        self.__set_table_partitioning(
            table=job_config, time_partitioning=time_partitioning, time_partitioning_field=time_partitioning_field,
            range_partitioning=range_partitioning, range_partitioning_field=range_partitioning_field,
            range_partitioning_start=range_partitioning_start, range_partitioning_end=range_partitioning_end,
            range_partitioning_interval=range_partitioning_interval
        )
        if clustering_fields:
            job_config.clustering_fields = clustering_fields
        
        if labels:
            job_config.labels = labels

        query_job = self.client.query(query, job_config=job_config)

        if wait_for_completion:
            query_job.result(timeout=TIMEOUT_SECONDS)
            return query_job
        else:
            return query_job

    def create_table_if_missing(self, dataset_name, table_name, schema,
                                time_partitioning=False, time_partitioning_field=None,
                                range_partitioning=False, range_partitioning_field=None,
                                range_partitioning_start=None, range_partitioning_end=None,
                                range_partitioning_interval=None, clustering_fields=None):
        if time_partitioning and range_partitioning:
            raise ValueError('Table may only have one type of partition')

        dataset_ref = self.client.dataset(dataset_name)

        # '$' means date partition and we don't have to create date partitions, just the root tables without the $YYYYMMDD
        if "$" in table_name:
            table_name = table_name[:table_name.index("$")]
        table_ref = dataset_ref.table(table_name)

        if self.does_table_exist_by_ref(table_ref):
            return

        self.logger.info("Creating %s.%s because it doesn't exist" % (dataset_name, table_name))

        table = bigquery.Table(table_ref)
        table.schema = schema

        self.__set_table_partitioning(
            table=table, time_partitioning=time_partitioning, time_partitioning_field=time_partitioning_field,
            range_partitioning=range_partitioning, range_partitioning_field=range_partitioning_field,
            range_partitioning_start=range_partitioning_start, range_partitioning_end=range_partitioning_end,
            range_partitioning_interval=range_partitioning_interval
        )
        if clustering_fields:
            table.clustering_fields = clustering_fields

        # If it already exists we don't care, Conflict comes back when it exists.
        try:
            self.client.create_table(table)
        except Conflict:
            pass

    def get_job(self, job_id):
        return self.client.get_job(job_id)

    def fetch_results(self, job):
        logging.warning("Deprecated! just used job.result()")
        return [r for r in self.iter_fetch_results(job)]

    def iter_fetch_results(self, job):
        logging.warning("Deprecated! just used job.result()")
        for r in job.result():
            yield r

    def create_view(self, dataset_name, view_name, query):
        dataset_ref = self.client.dataset(dataset_name)
        view = bigquery.Table(dataset_ref.table(view_name))
        view.view_query = query
        self.client.create_table(view)

    def update_view(self, dataset_name, view_name, query):
        view = bigquery.Table(self.client.dataset(dataset_name).table(view_name))
        view.view_query = query
        self.client.update_table(view, ['view_query'])

    def delete_view(self, dataset_name, view_name, not_found_ok=True):
        view = self.get_table(dataset_name=dataset_name, table_name=view_name)
        self.client.delete_table(table=view, not_found_ok=not_found_ok)

    def create_or_update_view(self, dataset_name, view_name, query):
        try:
            self.create_view(dataset_name=dataset_name, view_name=view_name, query=query)
        except Conflict:
            self.update_view(dataset_name=dataset_name, view_name=view_name, query=query)

    def is_table_a_view(self, dataset_name, table_name):
        view = self.get_table(dataset_name=dataset_name, table_name=table_name)
        return view.view_query is not None
