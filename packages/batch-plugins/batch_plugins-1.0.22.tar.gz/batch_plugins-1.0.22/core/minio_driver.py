import logging
import boto3
from botocore.client import Config
import json
import os
import io
import csv
import pandas as pd


class MinioConnection:

    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, endpoint_url: str):

        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.endpoint_url = endpoint_url
        # self.minio_bucket_name = minio_bucket_name
        # self.minio_target_prefix = minio_target_prefix

        self.session = boto3.session.Session()

        self.config = Config(
            retries={
                'max_attempts': 5,
                'mode': 'standard'
            }
        )

    def __enter__(self):

        try:
            self.s3_client = self.session.client(
                service_name='s3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                endpoint_url=self.endpoint_url,
                config=self.config
            )
            logging.info('Connected to MINIO')
            return self.s3_client
        except Exception as e:
            logging.info('MINIO connection failed')
            logging.info(e)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.s3_client.close()
        logging.info('MINIO connection closed')


class MinioDriver:

    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, endpoint_url: str) -> None:
        self.client_cnxn = MinioConnection(aws_access_key_id, aws_secret_access_key, endpoint_url)

        self.standard_file_types = ['csv', 'usr', 'sql', 'xml']
        self.json_types = ['json']
        self.xls_types = ['xlsx']
        self.compressed_file_types = ['zip']

    # TODO: REMOVE METHODS
    def list_buckets(self):
        with self.client_cnxn as client:
            return client.list_buckets()

    def vers(self, buck, key):
        with self.client_cnxn as client:
            return client.get_object_attributes(Bucket=buck, Key=key,
                                                ObjectAttributes=['ETag', 'Checksum', 'ObjectParts', 'StorageClass',
                                                                  'ObjectSize'])

    def list_minio_objects(self, bucket: str, directory: str) -> list[dict]:
        """
        ## Returns list of objects under a directory ##
        :param bucket: minio bucket
        :param directory: the directory to paginate e.g. cid/customers/consumption/d0036/ready
        """

        returned = []

        with self.client_cnxn as client:

            token = None

            while True:
                try:
                    paginator = client.get_paginator('list_objects_v2')

                    ops_params = {
                        'Bucket': bucket,
                        'PaginationConfig': {'StartingToken': token}
                    }
                    if directory:
                        ops_params['Prefix'] = directory

                    try:
                        page_iterator = paginator.paginate(**ops_params)
                        response = [page for page in page_iterator]

                        content = response[0]

                        returned += content['Contents']

                        logging.info(f'Paginated')

                        if content['IsTruncated'] == False:
                            logging.info(f'not truncated')
                            break

                        token = content['NextContinuationToken']

                        logging.info(f'token: {token}')

                    except:
                        logging.error('Nothing to paginate')
                        break

                except Exception as e:
                    logging.error('Failed to paginate')
                    break

        return returned

    def read_object(self, file_type: str, bucket: str, key: str) -> None:
        """
        ## Returns single object ##
        :param file_type: object extension or type e.g. csv, json, dataflows
        :param bucket: minio bucket
        :param key: key to object
        """

        if file_type.lower() in self.standard_file_types:
            with self.client_cnxn as client:
                try:
                    obj = client.get_object(Bucket=bucket, Key=key)
                    logging.info(f'Retrived {bucket}/{key}')

                    data = obj['Body'].read()
                    return data.decode("utf-8")

                except Exception as e:
                    logging.error(f'Failed to get object: {bucket}/{key}')
                    raise e

        elif file_type.lower() in self.json_types:
            with self.client_cnxn as client:
                try:
                    obj = client.get_object(Bucket=bucket, Key=key)
                    logging.info(f'Retrived {bucket}/{key}')

                    data = obj['Body'].read()
                    json_data = json.loads(data)
                    return json_data

                except Exception as e:
                    logging.error(f'Failed to get object: {bucket}/{key}')
                    raise e

        elif file_type.lower() in self.xls_types:
            with self.client_cnxn as client:
                try:
                    obj = client.get_object(Bucket=bucket, Key=key)
                    logging.info(f'Retrived {bucket}/{key}')

                    data = obj['Body'].read()
                    return data

                except Exception as e:
                    logging.error(f'Failed to get object: {bucket}/{key}')
                    raise e
        else:
            logging.error(f'Unsupported format {file_type}')
            raise ValueError(f'Unsupported format {file_type}')

    def read_objects(self, file_type: str, bucket: str, key_list: list):
        """
        ## Returns all objects in key_list ##
        :param file_type: object extension or type e.g. csv, json, dataflows
        :param bucket: minio bucket
        :param key: list of keys to each object
        """

        if file_type.lower() in self.standard_file_types:

            with self.client_cnxn as client:
                for key in key_list:
                    try:
                        obj = client.get_object(Bucket=bucket, Key=key)
                        logging.info(f'Retrived {bucket}/{key}')

                        data = obj['Body'].read()
                        yield (key, data.decode("utf-8"))

                    except Exception as e:
                        logging.info(f'Failed to get object: {bucket}/{key}')
                        raise e
        elif file_type.lower() in self.compressed_file_types:
            with self.client_cnxn as client:
                for key in key_list:
                    try:
                        obj = client.get_object(Bucket=bucket, Key=key)
                        logging.info(f'Retrived {bucket}/{key}')

                        data = obj['Body'].read()
                        yield (key, data)

                    except Exception as e:
                        logging.info(f'Failed to get object: {bucket}/{key}')
                        raise e
        else:
            logging.error(f'Unsupported format {file_type}')
            raise ValueError(f'Unsupported format {file_type}')

    def read_objects_attr(self, file_type: str, bucket: str, key_list: list):
        """
        ## Returns all objects in key_list and filename ##
        :param file_type: object extension or type e.g. csv, json, dataflows
        :param bucket: minio bucket
        :param key: list of keys to each object
        """

        if file_type.lower() in self.standard_file_types:

            with self.client_cnxn as client:
                for key in key_list:
                    try:
                        obj = client.get_object(Bucket=bucket, Key=key)
                        logging.info(f'Retrived {bucket}/{key}')

                        data = obj['Body'].read()
                        yield (key, data.decode("utf-8"))

                    except Exception as e:
                        logging.info(f'Failed to get object: {bucket}/{key}')
                        raise e

        else:
            logging.error(f'Unsupported format {file_type}')
            raise ValueError(f'Unsupported format {file_type}')

    def minio_download_object(self, minio_bucket_name: str, key: str, download_path: str) -> None:
        """
        ## Download a file from Minio bucket ##
        :param minio_bucket_name: Bucket to upload to 
        :param key: Minio object key
        :param download_path: local path + filename e.g. /home/git/temp/file_name.csv
        """

        with self.client_cnxn as client:
            try:
                client.download_file(minio_bucket_name, key, download_path)
                logging.info('Downloaded: %s', key)
            except Exception as e:
                logging.error('Download failed: %s', key)
                raise e

    def minio_upload_object(self, object_list: list, local_dir: str, minio_bucket_name: str, object_key: str) -> None:
        """
        ## Upload a local file to an Minio bucket ##
        :param object_list: List to upload e.g. [file_name.csv, file_name1.csv, file_name2.csv]
        :param bucket: Bucket to upload to
        :param object_key: key without object name
        """

        with self.client_cnxn as client:

            for obj in object_list:
                local_obj_dir = os.path.join(local_dir, obj)
                sftp_obj_key = os.path.join(object_key, obj)

                try:
                    client.upload_file(local_obj_dir, minio_bucket_name, sftp_obj_key)
                    logging.info('Upload completed: %s || Bucket: %s || Location: %s', local_obj_dir, minio_bucket_name,
                                 sftp_obj_key)

                except Exception as e:
                    logging.error('Upload failed: %s || Bucket: %s || Location: %s', local_obj_dir, minio_bucket_name,
                                  sftp_obj_key)
                    raise e

    def copy_object(self, object_list: list, source_bucket: str, source_path: str, new_bucket: str,
                    new_path: str) -> None:
        """
        ## Copy object into another location (does NOT delete after copy) ##
        :param object_list: object name list to copy (NO KEYS/DIRECTORY) e.g. [file_name.csv, file_name1.csv, file_name2.csv]
        :param source_bucket: Bucket with the object to copy
        :param source_path: Directory of the object to copy e.g. cid/customers/consumption/d0036/in
        :param new_bucket: Bucket of copy location
        :param new_path: Directory of copy location e.g. cid/customers/consumption/d0036/ready
        """

        with self.client_cnxn as client:
            for obj in object_list:
                if source_path:
                    source_key = os.path.join(source_path, obj)
                else:
                    source_key = obj
                new_key = os.path.join(new_path, obj)

                try:
                    client.copy_object(
                        CopySource=f'{source_bucket}/{source_key}',
                        Bucket=new_bucket,
                        Key=new_key
                    )
                    logging.info(f'{source_bucket}/{source_key} copied to {new_bucket}/{new_key}')

                except Exception as e:
                    logging.error(f'Failed to copy {source_key}')
                    raise e

    def delete_object(self, object_list: list, bucket: str, path: str) -> None:
        """
        ## Delete objects in minio ##
        :param object_list: object name list to delete (NO KEYS/DIRECTORY) e.g. [file_name.csv, file_name1.csv, file_name2.csv]
        :param bucket: Bucket with object to delete
        :param path: Directory of objects to delete e.g. cid/customers/consumption/d0036/ready
        """

        with self.client_cnxn as client:
            for obj in object_list:
                key = os.path.join(path, obj)

                try:
                    client.delete_object(Bucket=bucket, Key=key)
                    logging.info(f'{bucket}/{key} deleted')

                except Exception as e:
                    logging.error(f'Failed to delete: {bucket}/{key}')
                    raise e

    def upload_bytes_object(self, file_object: json or str, bucket: str, key: str):
        """
        ## Upload data in memory to minio as object ##
        :param file_type: object extension or type e.g. csv, json, dataflows
        :param file_object: Object in memory e.g. string
        :param bucket: Bucket to upload
        :param key: Path + file name e.g. cid/customers/consumption/d0036/ready/example.sql
        """

        with self.client_cnxn as client:
            # convert json to bytestream
            file_obj_bytes = file_object.encode('utf-8')

            try:
                client.upload_fileobj(io.BytesIO(file_obj_bytes), bucket, key)
                logging.info(f'{key} Uploaded')

            except Exception as e:
                logging.info('Failed to upload bytestream')
                raise e

    def upload_df_csv(self, object, minio_bucket_name: str, object_key: str, seperator: str = None):
        with self.client_cnxn as client:
            try:
                csv_buf = io.StringIO()
                if seperator is not None:
                    object.to_csv(csv_buf, header=True, index=False, sep=seperator)
                else:
                    object.to_csv(csv_buf, header=True, index=False)
                csv_buf.seek(0)
                client.put_object(Bucket=minio_bucket_name, Body=csv_buf.getvalue(), Key=object_key)

                # client.upload_fileobj(io.BytesIO(object), minio_bucket_name, object_key)
                logging.info('Upload completed: Bucket: %s || Location: %s', minio_bucket_name,
                             object_key)

            except Exception as e:
                logging.error('Upload failed: Bucket: %s || Location: %s', minio_bucket_name,
                              object_key)
                raise e
    
    def upload_df_csv_no_quoting(self, object, minio_bucket_name: str, object_key: str, seperator: str = None):
        with self.client_cnxn as client:
            try:
                csv_buf = io.StringIO()
                if seperator is not None:
                    object.to_csv(csv_buf, header=True, index=False, quoting=csv.QUOTE_NONE, escapechar=' ', sep=seperator)
                else:
                    object.to_csv(csv_buf, header=True,  index=False, quoting=csv.QUOTE_NONE, escapechar=' ')
                csv_buf.seek(0)
                client.put_object(Bucket=minio_bucket_name, Body=csv_buf.getvalue(), Key=object_key)

                # client.upload_fileobj(io.BytesIO(object), minio_bucket_name, object_key)
                logging.info('Upload completed: Bucket: %s || Location: %s', minio_bucket_name,
                             object_key)

            except Exception as e:
                logging.error('Upload failed: Bucket: %s || Location: %s', minio_bucket_name,
                              object_key)
                raise e

    def upload_large_df_csv(self, df: pd.DataFrame, bucket_name: str, object_key: str, separator: str = ','):
        """
        Upload a large DataFrame as a CSV to an S3 bucket, using regular or multipart upload based on the DataFrame's size.

        :param df: DataFrame to be uploaded as CSV.
        :param bucket_name: Name of the S3 bucket.
        :param object_key: Key for the object in S3.
        :param separator: Separator for the CSV file, defaults to ','.
        """
        with self.client_cnxn as s3_client:
            try:
                # Minimum part size for S3 multipart (5MB)
                MIN_PART_SIZE = 5 * 1024 * 1024

                # Convert entire DataFrame to CSV and calculate total size
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, header=True, index=False, sep=separator)
                csv_buffer.seek(0, io.SEEK_END)
                total_size = csv_buffer.tell()
                csv_buffer.seek(0)

                # Calculate the appropriate part size
                part_size = max(MIN_PART_SIZE,
                                (total_size // 10000) * 1024)  # Ensure at least 5MB and not more than 10,000 parts

                multipart_upload = s3_client.create_multipart_upload(Bucket=bucket_name, Key=object_key)

                parts = []
                part_number = 0
                while True:
                    # Read part from CSV buffer
                    part_data = csv_buffer.read(part_size).encode('utf-8')
                    if not part_data:
                        break  # Break loop if no more data

                    # Increment part number
                    part_number += 1

                    # Upload part
                    part = s3_client.upload_part(
                        Body=part_data,
                        Bucket=bucket_name,
                        Key=object_key,
                        UploadId=multipart_upload['UploadId'],
                        PartNumber=part_number
                    )
                    parts.append({
                        'PartNumber': part_number,
                        'ETag': part['ETag']
                    })

                # Complete the multipart upload
                s3_client.complete_multipart_upload(
                    Bucket=bucket_name,
                    Key=object_key,
                    UploadId=multipart_upload['UploadId'],
                    MultipartUpload={'Parts': parts}
                )

                logging.info('Upload completed: Bucket: %s || Location: %s', bucket_name, object_key)

            except Exception as e:
                logging.error('Upload failed: Bucket: %s || Location: %s || Error: %s', bucket_name, object_key, str(e))
                raise