import os
from dotenv import find_dotenv, load_dotenv
from pathlib import Path


class EnvironmentVariables:
    """Loads the .env file and assigns the values so that the values may be
    called.
    """
    load_dotenv(find_dotenv())

    def __init__(self):
        self._payload = {
            'url': os.environ.get("DDI_URL"),
            'username': os.environ.get("DDI_USERNAME"),
            'password': os.environ.get("DDI_PASSWORD")
        }
        self._header = os.environ.get("IPR_HEADER_ROW").split(',')

    def payload_url(self):
        return self._payload['url']

    def payload_username(self):
        return self._payload['username']

    def payload_password(self):
        return self._payload['password']

    def header_row(self):
        return self._header


class DirectoryValues:
    """Builds the commonly used directories for the project.

    The static methods are for the initializer in building of the directory
    paths.

    The methods are for the client to call as needed.
    """

    def __init__(self):
        self._project_dir = Path(__file__).resolve().parents[3]
        self._raw_data_path = os.path.join(self._project_dir,
                                           self._data_foldername(),
                                           self._raw_foldername())
        self._interim_data_path = os.path.join(self._project_dir,
                                               self._data_foldername(),
                                               self._interim_foldername())
        self._processed_data_path = os.path.join(self._project_dir,
                                                 self._data_foldername(),
                                                 self._processed_foldername())
        self._reports_data_path = os.path.join(self._project_dir,
                                               self._reports_foldername())

    @staticmethod
    def _data_foldername():
        return 'data'

    @staticmethod
    def _raw_foldername():
        return 'raw'

    @staticmethod
    def _interim_foldername():
        return 'interim'

    @staticmethod
    def _processed_foldername():
        return 'processed'

    @staticmethod
    def _reports_foldername():
        return 'reports'

    def raw_dir(self):
        return self._raw_data_path

    def interim_dir(self):
        return self._interim_data_path

    def processed_dir(self):
        return self._processed_data_path

    def reports_dir(self):
        return self._reports_data_path
