from google.cloud import bigquery
from jinja2 import Template

class BigQueryExecutor:
    def __init__(self, credentials_path):
        # Initialize ClickHouse connection
        self.client = bigquery.Client.from_service_account_json(credentials_path)

    def read_sql_file(self, file_path, params = {}):
        # Read the SQL query from the file
        with open(file_path, 'r') as file:
            query_template = Template(file.read())

        # Render the query with the parameters
        query = query_template.render(**params)
        return query

    def execute_query(self, query):
        # Execute the query using ClickHouse connect
        query_job = self.client.query(query)
        # Wait for the job to complete and get the result
        result = query_job.result()

        # Retrieve result rows
        result_rows = [dict(row) for row in result]

        # Retrieve column names
        result_columns = [field.name for field in result.schema]

        # Retrieve job summary
        execution_summary = {
            "read_rows": result.total_rows,  # Total rows in result
            "read_bytes": query_job.total_bytes_processed,  # Bytes processed by the query
            "written_rows": query_job.num_dml_affected_rows if query_job.num_dml_affected_rows else 0,  # Rows affected by DML queries (INSERT, UPDATE, DELETE)
            "written_bytes": query_job.total_bytes_billed - query_job.total_bytes_processed if query_job.total_bytes_billed and query_job.total_bytes_processed else 0,
            "total_rows_to_read": result.total_rows,
            "result_rows": result.total_rows,
            "result_bytes": sum([len(str(row)) for row in result_rows]),  # Estimate result size in bytes
            "elapsed_ns": (query_job.ended - query_job.started).total_seconds() * 1e9 if query_job.ended and query_job.started else None,
            "query_id": query_job.job_id
        }
        return result_rows, result_columns, execution_summary