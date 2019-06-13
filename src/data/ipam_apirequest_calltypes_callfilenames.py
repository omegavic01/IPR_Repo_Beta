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

import logging
import json
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from builder import EnvironmentValues, LoggingValues
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class IpamApiRequest:
    """IPAM API Call Definition."""

    def __init__(self):
        self._env_cls = EnvironmentValues()
        self._log_cls = LoggingValues()
        self._ipam_url = self._env_cls.payload_url()
        self._ipam_username = self._env_cls.payload_username()
        self._ipam_password = self._env_cls.payload_password()
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.basicConfig(filename=self._log_cls.log_filename(),
                            level=logging.INFO,
                            format=self._log_cls.log_format())
        self._logger = logging.getLogger(__name__)

    def ipam_api_request(self, _):
        """IPAM API Call.

        Args:
            self._item: The missing puzzle piece needed for the api call.  The
            return value of Class IpamCallTypes.
        Returns:
            The requests content decoded to 'utf-8' then returns as a python
            object after going through a json.loads process.

        """
        try_call_countdown = 3
        net_call = None
        self._logger.info('Calling IPAM for: %s', _)
        for countdown in range(try_call_countdown):
            try:
                net_call = requests.get(self._ipam_url +
                                        _,
                                        auth=(self._ipam_username,
                                              self._ipam_password),
                                        verify=False)
                break
            except requests.exceptions.ConnectionError as nerrt:
                if countdown < try_call_countdown - 1:
                    self._logger.warning('Failed %s lookup. Round %s of 3.',
                                         _,
                                         countdown)
                    time.sleep(5)
                    continue
                else:
                    self._logger.warning(
                        'Timeout Error for container view: %s, %s, %s',
                        _,
                        countdown,
                        nerrt)
                    return []
        return net_call
        # return json.loads(net_call.content.decode('utf-8'))

    @staticmethod
    def load_as_json(_):
        return json.loads(_)

class IpamCallTypes:
    """Defined call types needed for the api calls."""

    @staticmethod
    def extensible_attributes():
        """Returns the fields needed for an extensible attributes ipam call."""
        return 'extensibleattributedef?'

    @staticmethod
    def extensible_attributes_list_values():
        """Returns the fields needed for an extensible attributes ipam call."""
        return "extensibleattributedef?" \
               "_return_fields=" \
               "list_values," \
               "comment," \
               "name," \
               "type"

    @staticmethod
    def network_views():
        """Returns the fields needed for a network views ipam call."""
        return 'networkview?'

    @staticmethod
    def networks(view):
        """Returns the fields needed from networks ipam call."""
        return "network?" \
               "_return_fields=" \
               "extattrs," \
               "comment," \
               "network," \
               "network_view," \
               "utilization&" \
               "network_view=" + view + \
               "&_max_results=-5000"

    @staticmethod
    def networkcontainers(view):
        """Returns the fields needed from networkcontainers ipam call."""
        return "networkcontainer?" \
               "_return_fields=" \
               "extattrs," \
               "comment," \
               "network," \
               "network_view," \
               "utilization&" \
               "network_view=" + view + \
               "&_max_results=-5000"


class IpamCallFilenames:
    """Filenames defined for ipam pulls."""

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
