import sys
import os
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from dateutil import parser as date_parser
import shutil

class Util:
    #! Utility class to be used as a method namespace

    @staticmethod
    def get_beginning_hour(timestamp: str or datetime) -> datetime:
        """Reset timestamp to beginning beginning of the hour e.g. 2024-05-05 12:43:11+00:00 -> 2024-05-05 12:00:00+00:00
            Note: TIMESTAMPS MUST BE TIMEZONE AWARE

        Args:
            timestamp (str | datetime): Timestamp date format (yyyy-mm-dd) and time format inclu. timezone (hh:mm:ssz) 

        Returns:
            datetime: datetime object where the minutes, seconds are reset to 0
        """
        if isinstance(timestamp, str):
            timestamp = date_parser.parse(timestamp)

        if timestamp.tzinfo is None or timestamp.tzinfo.utcoffset(timestamp) is None:
            raise ValueError('Timestamp is not timezone aware. A timezone needs to be added.')
        return timestamp.replace(minute=0, second=0, microsecond=0)

    @staticmethod
    def create_download_dir(download_path: str) -> None:
        """creates a local folder for downloads

        Args:
            download_path (str): Unix path to directed folder

        Raises:
            e: Unable to create directory
        """
        try:
            os.makedirs(download_path, exist_ok=True)
            logging.info('Temp directory created')
        except Exception as e:
            logging.error('Failed to create temp directory')
            raise e
    
    @staticmethod
    def list_local_objects(local_download_path: str) -> list:
        # Lists all objs in a folder on local drive
        """Lists all objs in a folder on local directory

        Args:
            download_path (str): Unix path to directed folder

        Returns:
            list: List of filenames within the specified folder
        """
        return [filename.lower() for filename in os.listdir(local_download_path)]
    
    @staticmethod
    def delete_download_dir(download_path: str) -> None:
        """deletes a directory recursively

        Args:
            download_path (str): Unix path to directed folder
        """
        try:
            shutil.rmtree(download_path)
            logging.info('Directory deleted')
        except Exception as e:
            logging.error('Failed to delete directory')
            logging.error(e)

    @staticmethod
    def write_file_to_download_dir(local_download_path: str, filename: str, data: str) -> None:
        """Writes data and saves to a file

        Args:
            local_download_path (str): Path to destination folder
            filename (str): Name of file e.g. file1.csv
            data (str): Data to be written to file
        """
        save_path = os.path.join(local_download_path, filename)
        with open(save_path, 'w') as f:
            try:
                f.write(data)
                logging.info(f'File downloaded to: {local_download_path} with file name: {filename}')
            except Exception as e:
                logging.error(f'Failed to save the file to: {local_download_path} with file name: {filename}')
                raise ValueError(e)

    @staticmethod
    def flatten_dict(raw_dict: dict, parent_key: str = '', sep: str = '_') -> dict:
        """ Flattens a dictionary object with nested key values into a flat dictionary. 

        Args:
            raw_dict (dict): Dictionary object to be flattened
            parent_key (str, optional): Set during recursive execution
            sep (str, optional): Separator used to concat parent-child keys

        Returns:
            dict: flat dictionary with no more than 1 layer of nested values
        """
        items = []
        for key, val in raw_dict.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(val, dict):
                items.extend(Util.flatten_dict(val, new_key, sep=sep).items())
            else:
                items.append((new_key, val))
        return dict(items)