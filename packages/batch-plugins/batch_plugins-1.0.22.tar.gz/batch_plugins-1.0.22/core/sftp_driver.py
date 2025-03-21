import paramiko
import logging
import os
import io
import pandas as pd
from datetime import datetime, timezone, timedelta
from dateutil import parser
import pytz
import re
import time

from core.util import Util

class SftpConnection:

    def __init__(self,  authentication: str,
                        host: str,
                        port: str or int,
                        username: str = None,
                        password: str = None,
                        privatekey: str = None,
                        passphrase: str = None):

        """ params data structure
        params = {
            'authentication': authentication,
            'host': server_url,
            'port':port,
            'username': username,
            'password': password,
            'privatekey': privatekey,
            'passphrase': passphrase
        }
        """

        # ---------- core data ----------
        self.authentication = authentication
        self.host = host
        self.port = int(port)
        self.username = username
        self.password = password
        self.privatekey = privatekey
        self.passphrase = passphrase

        self.transport = None

    def connect(self) -> None:
        self.pkey = None
        self.sftp = None
        self.key = None

        try:
            self.transport = paramiko.Transport((self.host, self.port), disabled_algorithms=dict(
                pubkeys=["rsa-sha2-512", "rsa-sha2-256"]))

            if self.authentication.upper() == 'USERNAME/PASSWORD':
                self.transport.connect(username=self.username, password=self.password, pkey=self.key)

            elif self.authentication.upper() == 'USERNAME/PRIVATEKEY':
                self.pkey = paramiko.RSAKey.from_private_key_file(self.privatekey)
                self.transport.connect(username=self.username, password=self.password, pkey=self.pkey)

            elif self.authentication.upper() == 'USERNAME/PASSPHRASE/PRIVATEKEY':
                self.pkey = paramiko.RSAKey.from_private_key_file(self.privatekey, self.passphrase)
                self.transport.connect(username=self.username, pkey=self.pkey)

            else:
                raise ValueError(f'{self.authentication} SFTP authentication method not supported/recognised')

            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            logging.info(f'{self.authentication} SFTP connection to {self.host} established')
            return self.sftp

        except Exception as e:
            logging.error(f'{self.authentication} SFTP connection to {self.host} failed')
            raise e

    def close(self) -> None:
        try:
            self.transport.close()
            logging.info(f'{self.host} SFTP transport closed')
            self.sftp.close()
            logging.info(f'{self.host} SFTP connection closed')
        except Exception as e:
            logging.error('Failed to close SFTP connection')
            logging.error(e)

class SftpDriver:

    def __init__(self,  authentication: str,
                        host: str,
                        port: str,
                        username: str,
                        password: str,
                        privatekey: str,
                        passphrase: str) -> None:

        self.sftp = SftpConnection(authentication,
                                    host,
                                    port,
                                    username,
                                    password,
                                    privatekey,
                                    passphrase,
                                    )

    def connect(self):
        self.sftp_cnxn = self.sftp.connect()

    def disconnect(self):
        self.sftp_cnxn.close()

    def list_all_sftp_objects(self, sftp_path) -> list[str]:
        return self.sftp_cnxn.listdir(sftp_path)

    def download_sftp_objects(self, object_list: list, sftp_dir: str, local_dir: str) -> None:
        """Download a file to an SFTP server to local dir
        :param object_list: list of the object to download (inclu. extension)
        :param sftp_path: folder location of desired objects 
        :param local_dir: local path store downloads
        """

        for obj in object_list:
            sftp_obj_dir = os.path.join(sftp_dir, obj)
            local_obj_dir = os.path.join(local_dir, obj)

            try:
                self.sftp_cnxn.get(sftp_obj_dir, local_obj_dir)
                logging.info('%s downloaded', obj)
            except:
                logging.info('%s failed to download', obj)

    def read_sftp_files_as_df(self, object_list: list, sftp_dir: str) -> list:
        """Read from an SFTP server and return them as a dictionary of DataFrames.

        :param object_list: List of object filenames to download (including extension).
        :param sftp_dir: Folder location of the desired objects on SFTP.
        :return: Dictionary where keys are filenames and values are Pandas DataFrames.
        """
        dataframes = {}

        for obj in object_list:
            sftp_obj_dir = os.path.join(sftp_dir, obj)

            try:
                # Read the file into memory
                with io.BytesIO() as file_buffer:
                    self.sftp_cnxn.getfo(sftp_obj_dir, file_buffer)
                    file_buffer.seek(0)  # Reset buffer position

                    # Determine file type and read accordingly
                    if obj.endswith('.csv'):
                        df = pd.read_csv(file_buffer)
                    elif obj.endswith(('.xls', '.xlsx')):
                        df = pd.read_excel(file_buffer)
                    elif obj.endswith('.json'):
                        df = pd.read_json(file_buffer)
                    else:
                        logging.warning("Unsupported file format: %s", obj)
                        continue  # Skip unsupported files
                    dataframes[obj] = df
                    logging.info("%s read into DataFrame", obj)

            except Exception as e:
                logging.error("Failed to read %s: %s", obj, str(e))

        return dataframes


    def read_sftp_files_as_strings(self, object_list: list, sftp_dir: str) -> dict:
        """Download files from an SFTP server and return them as a dictionary of strings.

        :param object_list: List of object filenames to download (including extension).
        :param sftp_dir: Folder location of the desired objects on SFTP.
        :return: Dictionary where keys are filenames and values are file contents as strings.
        """
        file_contents = {}

        for obj in object_list:
            sftp_obj_dir = os.path.join(sftp_dir, obj)

            try:
                # Read the file into memory
                with io.BytesIO() as file_buffer:
                    self.sftp_cnxn.getfo(sftp_obj_dir, file_buffer)
                    file_buffer.seek(0)  # Reset buffer position

                    # Read as string (assuming text files)
                    content = file_buffer.read().decode("utf-8")
                    file_contents[obj] = content
                    logging.info("%s read as string", obj)

            except Exception as e:
                logging.error("Failed to read %s: %s", obj, str(e))

        return file_contents

    def pull_obj_ids(self, sftp_path: str, file_name: str = None) -> list:
        """Pulls list of all files matching file_name pattern
        Returns:
            list: List of filenames (inclu. extensions) that are valid
        """
        _all_items = self.sftp_cnxn.listdir_attr(sftp_path)
        counter = len(_all_items)
        logging.info(f'Total files in SFTP: {counter}')
        _item_list = [_item.filename for _item in _all_items]
        if file_name is not None:
            filename_filter_list = file_name.split(";")
            _filtered_item_list = []
            for fnf in filename_filter_list:
                pattern = r'^.*' + fnf.format(YYYYMMDD=r"\d{8}") + r'.*$'
                _filtered_item_list.extend([fname for fname in _item_list if re.match(pattern, fname)])
        else:
            _filtered_item_list = _item_list
        logging.debug(f'Files found: {_filtered_item_list}')
        return _filtered_item_list


    def pull_obj_ids_between(self, sftp_path: str, from_dttm_str: str, to_dttm_str: str, file_name: str = None) -> list:
        """Pulls list of all files equal to/after the datetime

        Args:
            datetime (datetime): Datetime str of last run

        Returns:
            list: List of filenames (inclu. extensions) that are valid
        """

        # from datetime
        _beginning_dttm = Util.get_beginning_hour(from_dttm_str)
        # to datetime
        _end_dttm = Util.get_beginning_hour(to_dttm_str)

        _all_items = self.sftp_cnxn.listdir_attr(sftp_path)
        counter = len(_all_items)

        logging.info(f'Pulling filenames from dttm: {_beginning_dttm}')
        logging.info(f'Pulling filenames to dttm: {_end_dttm}')
        logging.info(f'Total files in SFTP: {counter}')

        try:
            _raw_list = list(filter(
                lambda f: (datetime.fromtimestamp(f.st_mtime, tz=pytz.timezone('UTC')) >= _beginning_dttm) and
                            (datetime.fromtimestamp(f.st_mtime, tz=pytz.timezone('UTC')) < _end_dttm),
                _all_items))
        except Exception as e:
            logging.error(f'Failed to pull files between {_beginning_dttm} - {_end_dttm}')
            raise ValueError(e)

        _item_list = [_item.filename for _item in _raw_list]

        if file_name is not None:
            filename_filter_list = file_name.split(";")
            _filtered_item_list = []
            for fnf in filename_filter_list:
                pattern = r'^.*' + fnf.format(YYYYMMDD=r"\d{8}") + r'.*$'
                _filtered_item_list.extend([fname for fname in _item_list if re.match(pattern, fname)])
        else:
            _filtered_item_list = _item_list
        logging.debug(f'Files found: {_filtered_item_list}')
        return _filtered_item_list


    def upload_objects_to_sftp(self, object_list: list, sftp_dir: str, local_dir: str) -> None:

        """Upload a file to an SFTP server from a local directory
        :param object_list: list of the object to upload (inclu. extension)
        :param sftp_path: folder location to upload objects 
        :param local_dir: local path of uploaded objects
        """

        for obj in object_list:
            sftp_obj_dir = os.path.join(sftp_dir, obj)
            local_obj_dir = os.path.join(local_dir, obj)

            try:
                self.sftp_cnxn.put(local_obj_dir, sftp_obj_dir, confirm=False)
                logging.info(f'{obj} uploaded')
            except:
                logging.info(f'{obj} failed to upload')

    def download_up_to_date_sftp_object(self, sftp_object: str, sftp_dir: str, local_dir: str, 
                                        start_time: str, secs_to_sleep: int, number_of_tries: int) -> None:

        """Download an up-to-date version of file if exists from an SFTP server to local dir 
        :param sftp_object: object to download (inclu. extension)
        :param sftp_path: folder location of desired objects 
        :param local_dir: local path store downloads
        :param start_time: time that the file is expected to be updated after
        """

        sftp_obj_dir = os.path.join(sftp_dir, sftp_object)
        local_obj_dir = os.path.join(local_dir, sftp_object)

        start_ts = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
        #start_ts = start_time

        download_done = False
        counter = 0
        while not download_done:
            counter += 1
            if counter == number_of_tries:
                download_done = True
            time.sleep(secs_to_sleep)
            try:
                file_info = self.sftp_cnxn.stat(sftp_obj_dir)
                file_update_time = datetime.fromtimestamp(file_info.st_mtime)
                logging.info(f'Counter: {counter} - Start Time: {start_ts} - File Update Time: {file_update_time}')
                if file_update_time >= start_ts: # Check if it's a new file
                    logging.info(f'{sftp_object} downloading...')
                    try:
                        self.sftp_cnxn.get(sftp_obj_dir, local_obj_dir)
                    except:
                        logging.info('%s failed to download', sftp_object)
                    download_done = True
                else:
                    logging.info(f'{sftp_object} is older than start time')                    
            except:
                logging.info(f'{sftp_object} is not there yet!')