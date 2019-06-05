import os
from dotenv import find_dotenv, load_dotenv


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
    """Builds the commonly used directories for the project."""

    def __init__(self):
        self._project_dir = os.path.join(os.path.dirname(__file__),
                                         os.pardir,
                                         os.pardir)
        self._raw_data_path = os.path.join(self._project_dir,
                                           'data',
                                           'raw')
        self._interim_data_path = os.path.join(self._project_dir,
                                               'data',
                                               'interim')
        self._processed_data_path = os.path.join(self._project_dir,
                                                 'data',
                                                 'processed')
        self._report_data_path = os.path.join(self._project_dir,
                                              'reports')

    def proj_dir(self):
        return self._project_dir

    def raw_dir(self):
        return self._raw_data_path

    def interim_dir(self):
        return self._interim_data_path

    def processed_dir(self):
        return self._processed_data_path

    def report_dir(self):
        return self._report_data_path
