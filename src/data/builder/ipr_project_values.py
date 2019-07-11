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
import json
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
        self._ipr_header_dict = os.environ.get("IPR_HEADER_ROW_DICT")
        self._ipr_header_list = os.environ.get("IPR_HEADER_ROW_LIST")
        self._tacacs_username = os.environ.get("TACACS_USERNAME")
        self._tacacs_password = os.environ.get("TACACS_PASSWORD")
        self._tody_cools = os.environ.get("TODY_COOLS")

    def payload_url(self):
        """Returns DDI_URL from .env file."""
        return self._ddi_payload['url']

    def payload_username(self):
        """Returns DDI_USERNAME from .env file."""
        return self._ddi_payload['username']

    def payload_password(self):
        """Returns DDI_PASSWORD from .env file."""
        return self._ddi_payload['password']

    def header_row_dict(self):
        """Returns IPR_HEADER_ROW from .env file."""
        return json.loads(self._ipr_header_dict)

    def header_row_list(self):
        """Returns IPR_HEADER_ROW from .env file."""
        return self._ipr_header_list.split(',')

    def tacacs_username(self):
        """Returns TACACS_USERNAME from .env file."""
        return self._tacacs_username

    def tacacs_password(self):
        """Returns TACACS_PASSWORD from .env file."""
        return self._tacacs_password

    def tody_cools(self):
        """Returns TODY_COOLS IP from .env file."""
        return self._tody_cools


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


class DataFileNames:
    """Place to store filenames."""

    @staticmethod
    def ipam_dump_interim_xlsx():
        """Interim spreadhseet name."""
        return 'ipam_dump_interim_xlsx.xlsx'

    @staticmethod
    def ipam_dump_interim_panda():
        """Interim panda data pickle file name."""
        return 'ipam_dump_interim_panda.pkl'

    @staticmethod
    def ipam_dump_interim_dicted():
        """Interim dictionary data pickle file name."""
        return 'ipam_dump_interim_dicted.pkl'

    @staticmethod
    def ipam_dump_processed_xlsx():
        """Processed spreadsheet filename."""
        return 'ipam_dump_processed.xlsx'

    @staticmethod
    def ipam_dump_processed_pickle():
        """Processed pickled filename."""
        return 'ipam_dump_processed.pkl'

    @staticmethod
    def extensible_attributes_filename():
        """Returns filename for extensible attributes."""
        return 'extensible_attributes.pkl'

    @staticmethod
    def extensible_attributes_list_values_filename():
        """Returns filename for extensible attributes."""
        return 'extensible_attributes_list_values.pkl'

    @staticmethod
    def network_views_filename():
        """Returns filename for network views."""
        return 'network_views.pkl'

    @staticmethod
    def networks_filename():
        """Returns filename for networks filename."""
        return 'networks.pkl'

    @staticmethod
    def networkcontainers_filename():
        """Returns filename for networkcontainers filename."""
        return 'networkcontainers.pkl'

    @staticmethod
    def processed_filename():
        """Returns filename for IPAM-to-IPR Spreadsheet filename."""
        return 'IPAM-to-IPR.xlsx'

    @staticmethod
    def master_pkl_filename():
        """Returns filename for Master pickle filename."""
        return 'master_pkl.pkl'

    @staticmethod
    def percent_blank_filename():
        """Returns filename for networkcontainers filename."""
        return 'MASTER - Report by percent-BLANK.xlsx'

    @staticmethod
    def vrf_to_agency_filename():
        """Returns filename for vrf to agency dictionary filename."""
        return 'vrf_to_agency_dict.pkl'

    @staticmethod
    def ipam_agency_list_filename():
        """Returns filename for vrf to agency dictionary filename."""
        return 'ipam_agency_list.pkl'

    @staticmethod
    def view_to_vrf_lib():
        """Returns filename for vrf to agency dictionary filename."""
        return 'view_to_vrf_lib.pkl'

    @staticmethod
    def vrf_to_view_lib():
        """Returns filename for vrf to agency dictionary filename."""
        return 'vrf_to_view_lib.pkl'

    @staticmethod
    def src_global_addresses():
        """Returns source filename for global addresses."""
        return 'Global Addresses for IPR 2019-05-01.xlsx'

    @staticmethod
    def global_addresses_lib():
        """Returns source filename for global addresses."""
        return 'global_addresses.pkl'

    @staticmethod
    def errored_import_configs():
        """Returns source filename for global addresses."""
        return 'errored_import_lines.csv'

    @staticmethod
    def errored_import_configs():
        """Returns source filename for global addresses."""
        return 'errored_import_add_lines.csv'
