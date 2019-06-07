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
from builder import EnvironmentValues, DirectoryValues, LoggingValues
import logging
import requests
import json
import time


class _BaseDdiIpamPull:

    def __init__(self):
        self._env_cls = EnvironmentValues()
        self._dir_cls = DirectoryValues()
        self._log_cls = LoggingValues()
        self._ddi_url = self._env_cls.payload_url()
        self._ddi_username = self._env_cls.payload_username()
        self._ddi_password = self._env_cls.payload_password()
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.basicConfig(filename=self._log_cls.log_filename(),
                            level=logging.INFO,
                            format=self._log_cls.log_format())
        self._logger = logging.getLogger(__name__)


class IpamApiRequestGet(_BaseDdiIpamPull):

    def ddi_call(self, _):
        """DDI API Call.

        Args:
            self._item: The missing puzzle piece needed for the api call.  The
            return value of Class DdiCallTypes.
        Returns:
            The requests content decoded to 'utf-8' then returns as a python
            object after going through a json.loads process.

        """
        trynetwork = 3
        net_call = None
        self._logger.info('Calling DDI for: %s', _)
        for iview in range(trynetwork):
            try:
                net_call = requests.get(self._ddi_url +
                                        _,
                                        auth=(self._ddi_username,
                                              self._ddi_password),
                                        verify=False)
                break
            except requests.exceptions.ConnectionError as nerrt:
                if iview < trynetwork - 1:
                    self._logger.warning('Failed %s lookup. Round %s of 3.',
                                         _,
                                         iview)
                    time.sleep(5)
                    continue
                else:
                    self._logger.warning(
                        'Timeout Error for container view: %s, %s, %s',
                        _,
                        iview,
                        nerrt)
                    return []
        return json.loads(net_call.content.decode('utf-8'))


class DdiCallTypes:

    @staticmethod
    def extensible_attributes():
        return 'extensibleattributedef?'

    @staticmethod
    def network_views():
        return 'networkview?'


class DdiCallFilenames:

    @staticmethod
    def extensible_attributes_filename():
        return 'extensible_attributes.pkl'

    @staticmethod
    def network_views_filename():
        return 'network_views.pkl'
