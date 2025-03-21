from ftplib import FTP
from datetime import datetime
import os


class FtpDriver:
    """A class for interacting with an FTP server."""

    def __init__(self, host, username, password):
        """
        Initialize the FTPServerDriver object.

        Args:
            host (str): The hostname or IP address of the FTP server.
            username (str): The username for the FTP server login.
            password (str): The password for the FTP server login.
        """
        self.host = host
        self.username = username
        self.password = password
        self.ftp = FTP()

    def connect(self):
        """
        Connect to the FTP server.

        Raises:
            ConnectionError: If unable to establish a connection to the FTP server.
            ftplib.error_perm: If authentication fails.
        """
        try:
            self.ftp.connect(self.host)
            self.ftp.login(self.username, self.password)
        except Exception as e:
            raise ConnectionError("Failed to connect to the FTP server.") from e

    def disconnect(self):
        """Disconnect from the FTP server."""
        try:
            self.ftp.quit()
        except Exception as e:
            raise ConnectionError("Failed to disconnect from the FTP server.") from e

    def list_files_by_pattern(self, pattern):
        """
        List files on the FTP server that match the given name pattern.

        Args:
            pattern (str): The name pattern to match.

        Returns:
            List[str]: A list of file names matching the given pattern.

        Raises:
            ftplib.error_perm: If an error occurs while listing files.
        """
        try:
            file_list = []
            self.ftp.retrlines('NLST', file_list.append)
            matched_files = [file for file in file_list if pattern in file]
            return matched_files
        except Exception as e:
            raise Exception("Failed to list files on the FTP server.") from e

    def download_files_by_date_and_pattern(self, date: str or datetime, pattern, local_dir, ftp_dir):
        """
        Download files from the FTP server based on the provided date, name pattern, and directories.

        Args:
            date (str): The date threshold for file addition in the format "YYYY/MM/DD".
            pattern (str): The name pattern to match.
            local_dir (str): The local directory to save the downloaded files.
            ftp_dir (str): The directory on the FTP server from which to download files.

        Raises:
            ftplib.error_perm: If an error occurs while downloading files.
            ValueError: If the provided date is not in the expected format.
        """
        try:
            self.ftp.cwd(ftp_dir)
            files = self.list_files_by_pattern(pattern)
            if isinstance(date, str):
                date_threshold = datetime.strptime(date, "%Y/%m/%d")
            else:
                date_threshold = date
            download_check = False
            for file in files:
                file_date = self.get_file_added_date(file)
                if file_date >= date_threshold:
                    local_path = os.path.join(local_dir, file)
                    with open(local_path, 'wb') as local_file:
                        self.ftp.retrbinary('RETR ' + file, local_file.write)
                    download_check = True
            return download_check
        except ValueError as ve:
            raise ValueError(
                "Invalid START_DATE date format. Please provide the date in the format 'YYYY/MM/DD'.") from ve
        except Exception as e:
            raise Exception("Failed to download files from the FTP server.") from e

    def get_file_added_date(self, filename):
        """
        Get the added date of a file on the FTP server.

        Args:
            filename (str): The name of the file.

        Returns:
            datetime.datetime: The added date of the file.

        Raises:
            ftplib.error_perm: If an error occurs while retrieving file information.
            ValueError: If the file date format is invalid.
        """
        try:
            raw_time = self.ftp.sendcmd('MDTM ' + filename)
            file_date = datetime.strptime(raw_time[4:], '%Y%m%d%H%M%S')
            return file_date
        except Exception as e:
            raise Exception("Failed to retrieve the added date of the file.") from e
