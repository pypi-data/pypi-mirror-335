from typing import Tuple
import numpy as np
import logging



class ValidateObject:
    def __init__(self):
        # see extensions dict below for supported extensions
        # obj_type e.g. D0036, D0010

        self.extensions = {
            'DATAFLOW': ['usr','out', 'cregi', 'd0148', 'uff'],
            'CSV': ['csv', 'out', 'xml', 'json', 'zip'],
            'DAT': ['dat'],
            'CNS': ['cns'],
            'JSON':['json'],
            'XLS': ['xls', 'xlsx'],
            'XLSX': ['xlsx'],
            'XML': ['xml'],
            'PARQUET': ['parquet', 'uff']
        }
        
        self.delimiter_map = {'COMMA': ',', 'TAB': '\t', 'SEMICOLON': ';', 'SPACE': ' ', 'PIPE': '|'}

    @staticmethod
    def validate_minio_files(pagination_response: list[dict], file_extension: list[str]) -> list[str]:
        """Compares file extensions of boto3 bucket pagination

        Args:
            pagination_response (list[dict]): List of dictionaries of objects found by pagination
            file_extension (list): List of valid file extensions e.g. ['csv', 'json'] 

        Returns:
            list: 2 lists, one of the valid list and anothe for invalid list
        """

        if 'NONE' in file_extension:
            valid_list = list(filter(lambda object: object['Size'] > 0 and (len(object['Key'].split('.')) == 1 or object['Key'].split('.')[-1] in file_extension), pagination_response))
            invalid_list = list(filter(lambda object: object['Size'] <= 0 and (object['Key'].split('.')[-1] not in file_extension or len(object['Key'].split('.')) > 1), pagination_response))
        else:
            valid_list = list(filter(lambda object: object['Size'] > 0 and object['Key'].split('.')[-1] in file_extension, pagination_response))
            invalid_list = list(filter(lambda object: object['Size'] <= 0 or object['Key'].split('.')[-1] not in file_extension, pagination_response))
        return valid_list, invalid_list

    @staticmethod
    def validate_file_list(file_list: list[str], file_extension: list[str]) -> list[str]:
        """Validates list of filename extensions

        Args:
            file_list (list[str]): List of file names e.g. ['file1.csv', 'file2.csv']
            file_extension (list[str]): List of valid file extensions e.g. ['csv', 'json'] 

        Returns:
            list[str]: List of all filenames with valid file extensions
        """

        if 'NONE' in file_extension:
            # If no file extension
            valid_list = list(filter(lambda _file: len(_file.split('.')) == 1 or _file.split('.')[-1].lower() in file_extension, file_list))
            invalid_list = list(filter(lambda _file: len(_file.split('.')) > 1 and _file.split('.')[-1].lower() not in file_extension, file_list))
        else:
            valid_list = list(filter(lambda _file: _file.split('.')[-1].lower() in file_extension, file_list))
            invalid_list = list(filter(lambda _file: _file.split('.')[-1].lower() not in file_extension, file_list))
        return valid_list, invalid_list


    def validate_extension(self, object_name: str, obj_type: str) -> bool:
        """Validates a single file/object name

        Args:
            object_name (str): name of object, no paths

        Returns:
            bool: _description_
        """

        name_components = object_name.lower().split('.')
        if obj_type != 'NONE':
            check = name_components[-1] in self.extensions[obj_type]
        elif obj_type == 'NONE':
            if len(name_components) == 1:
                check = True
            else:
                check = False

        return check


    def validate_extensions(self, object_list: list, obj_type: str) -> Tuple[list, list]:
        """Validates a list of file object names

        Args:
            name_list (list): list of file names file names with extension (no paths)

        Returns:
            list: empty list for all valid and list of invalid file names if invalid
        """

        # splits obj names and check extensions
        split_name_list = list(map(lambda name: name.lower().split('.'), object_list))
        if obj_type != 'NONE':
            check_results = np.array(list(map(lambda item: item[-1] in self.extensions[obj_type], split_name_list)))
        elif obj_type == 'NONE':
            check_results = np.array(list(map(lambda item: len(item) == 1, split_name_list)))

        # gets all invalid extensions
        invalid_name_loc = list(np.where(check_results == False)[0])
        invalid_extensions = [object_list[index] for index in invalid_name_loc]
        logging.info('Skipping objects: %s', invalid_extensions)

        # get all valid extensions
        try:
            valid_name_loc = list(np.where(check_results == True)[0])
            valid_extensions = [object_list[index] for index in valid_name_loc]
            logging.info('PASSED extension validation check')
            return valid_extensions, invalid_extensions

        except Exception as e:
            logging.error('No valid extensions found')
            raise e
    
    @staticmethod
    def validate_bytes(bytes: int or float):
        if bytes > 0:
            return True
        else:
            return False
    

    def get_delimiter(self, obj_type: str) -> str:
        """
        Returns the delimiter char for a DataCatalog delimiter definition.
        :return: str - delimiter as a String
        """
        
        delimiter = self.delimiter_map.get(obj_type)
        return delimiter