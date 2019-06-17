#!/usr/bin/python
""" Copyright 2007 HVictor
Licensed to PSF under a Contributor Agreement.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing
permissions and limitations under the License.

"""

import os
from pathlib import Path
from dotenv import find_dotenv, load_dotenv


class EnvironmentValues:
    """Loads the .env file and assigns the values so that the values may be
    called.

    """
    load_dotenv(find_dotenv())

    def __init__(self):
        self._ddi_payload = {
            'url': os.environ.get("DDI_URL"),
            'username': os.environ.get("DDI_USERNAME"),
            'password': os.environ.get("DDI_PASSWORD")
        }
        self._ipr_header = os.environ.get("IPR_HEADER_ROW").split(',')

    def payload_url(self):
        """Returns DDI_URL from .env file."""
        return self._ddi_payload['url']

    def payload_username(self):
        """Returns DDI_USERNAME from .env file."""
        return self._ddi_payload['username']

    def payload_password(self):
        """Returns DDI_PASSWORD from .env file."""
        return self._ddi_payload['password']

    def header_row(self):
        """Returns IPR_HEADER_ROW from .env file."""
        return self._ipr_header


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
        os.makedirs(self._raw_data_path, exist_ok=True)
        os.makedirs(self._interim_data_path, exist_ok=True)
        os.makedirs(self._processed_data_path, exist_ok=True)
        os.makedirs(self._reports_data_path, exist_ok=True)

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
        """Returns raw folder directory path."""
        return self._raw_data_path

    def interim_dir(self):
        """Returns interim folder directory path."""
        return self._interim_data_path

    def processed_dir(self):
        """Returns processed folder directory path."""
        return self._processed_data_path

    def reports_dir(self):
        """Returns reports folder directory path."""
        return self._reports_data_path


class LoggingValues:
    """Provides a central source for logging values."""
    def __init__(self):
        self._logging_format = self._log_format()
        self._logging_filename = self._log_filename()

    @staticmethod
    def _log_format():
        return '[%(asctime)s, %(name)s, %(levelname)s] %(message)s'

    @staticmethod
    def _log_filename():
        return 'logfile.log'

    def log_format(self):
        """Returns logging format."""
        return self._logging_format

    def log_filename(self):
        """Returns logging filename."""
        return self._logging_filename


class DataFilenames:

    @staticmethod
    def ipam_dump_interim_xlsx():
        return 'ipam_dump_interim.xlsx'

    @staticmethod
    def ipam_dump_interim_pickle():
        return 'ipam_dump_interim.pickle'
