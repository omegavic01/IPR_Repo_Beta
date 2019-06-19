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

from builder import DirectoryValues, LoggingValues
from builder import Writer, Reader
from ipam_apirequest_calltypes_callfilenames import \
    IpamCallTypes, \
    IpamApiRequest, \
    IpamCallFilenames
import logging
import time
import threading


class _BaseIpamGetsToWrite:

    def __init__(self):
        self._log_cls = LoggingValues()
        logging.basicConfig(filename=self._log_cls.log_filename(),
                            level=logging.DEBUG,
                            filemode='a',
                            format=self._log_cls.log_format())
        self._logger = logging.getLogger(__name__)
        self._logger.info('Loading Project Environment Variables.')
        self.dir_cls = DirectoryValues()
        self.write_cls = Writer()
        self.reader_cls = Reader()
        self.call_types_cls = IpamCallTypes()
        self.filenames_cls = IpamCallFilenames()
        self.ext_call_setup_cls = IpamApiRequest()
        self._logger.info('Project Environment Variables Loaded.')
        self._network_data = []
        self.dl_lock = threading.Lock()
        max_concurrent_dl = 8
        self.dl_sem = threading.Semaphore(max_concurrent_dl)


class IpamGetsToWrite(_BaseIpamGetsToWrite):

    def get_extensible_attributes(self):
        self._logger.info('Pulling current Extensible Attribute data.')

        _ext_attr_data = self.ext_call_setup_cls.loads_as_json(
            self.ext_call_setup_cls.ipam_api_request(
                self.call_types_cls.extensible_attributes()).
            text)
        self.write_cls.write_to_pkl(self.dir_cls.raw_dir(),
                                    self.filenames_cls.
                                    extensible_attributes_filename(),
                                    _ext_attr_data)
        self._logger.info('Ext Attr data written to .pkl file in Raw Dir.')

    def get_extensible_attributes_list_values(self):
        self._logger.info('Pulling current Extensible Attribute data.')
        _ext_attr_list_data = self.ext_call_setup_cls.loads_as_json(
            self.ext_call_setup_cls.ipam_api_request(
                self.call_types_cls.extensible_attributes_list_values()).
            text)
        self.write_cls.write_to_pkl(
            self.dir_cls.raw_dir(),
            self.filenames_cls.extensible_attributes_list_values_filename(),
            _ext_attr_list_data)
        self._logger.info('Ext Att list data written to .pkl file in Raw Dir.')

    def get_network_views(self):
        self._logger.info('Pulling current Network View Data.')
        _network_view_data = self.ext_call_setup_cls.loads_as_json(
            self.ext_call_setup_cls.ipam_api_request(
                self.call_types_cls.network_views()).
            text)
        self.write_cls.write_to_pkl(self.dir_cls.raw_dir(),
                                    self.filenames_cls.
                                    network_views_filename(),
                                    _network_view_data)
        self._logger.info('Network View data written to .pkl file in raw Dir.')

    def _get_ipam_networks(self, call):
        self.dl_sem.acquire()
        try:
            networks = self.ext_call_setup_cls.loads_as_json(
                self.ext_call_setup_cls.ipam_api_request(call).text)
            with self.dl_lock:
                self._network_data += networks
        finally:
            self.dl_sem.release()

    def get_networks(self):
        self._logger.info('Pulling IPAM Networks.')
        network_views = self.return_network_views()
        start = time.perf_counter()
        threads = []
        for _ref in network_views:
            # if _ref == network_views[5]:
            #     break
            network_call = self.call_types_cls.networks(_ref['name'])
            t = threading.Thread(target=self._get_ipam_networks,
                                 args=(network_call,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
        end = time.perf_counter()

        self._logger.info("Downloaded {} Networks in {} seconds".
                          format(len(self._network_data), end - start))

        self.write_cls.write_to_pkl(self.dir_cls.raw_dir(),
                                    self.filenames_cls.
                                    networks_filename(),
                                    self._network_data)
        self._network_data = []
        self._logger.info('IPAM data written to .pkl file in raw Dir.')

    def get_networkcontainers(self):
        self._logger.info('Pulling IPAM Networkcontainers.')
        network_views = self.return_network_views()
        start = time.perf_counter()
        threads = []
        for _ref in network_views:
            # if _ref == network_views[5]:
            #     break
            network_call = self.call_types_cls.networkcontainers(_ref['name'])
            t = threading.Thread(target=self._get_ipam_networks,
                                 args=(network_call,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
        end = time.perf_counter()

        self._logger.info("Downloaded {} Networks in {} seconds".
                          format(len(self._network_data), end - start))

        self.write_cls.write_to_pkl(self.dir_cls.raw_dir(),
                                    self.filenames_cls.
                                    networkcontainers_filename(),
                                    self._network_data)
        self._network_data = []
        self._logger.info('IPAM data written to .pkl file in raw Dir.')

    def return_network_views(self):
        return self.reader_cls.read_from_pkl(self.dir_cls.raw_dir(),
                                             self.filenames_cls.
                                             network_views_filename())
