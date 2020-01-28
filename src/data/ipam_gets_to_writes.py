#!/usr/bin/python
import logging
import json
import time
import threading
from builder import DirectoryValues, DataFileNames, LoggingValues
from builder import Writer, Reader
from ipam_apirequest_calltypes import IpamCallTypes, IpamApiRequest


class IpamGetsToWrite:
    """Class containing methods for making DDI call's."""
    # pylint: disable = R0902
    # 11/7 (too-many-instance-attributes) Known and like it this way.
    def __init__(self):
        self._log_cls = LoggingValues()
        logging.basicConfig(filename=self._log_cls.log_filename(),
                            level=logging.DEBUG,
                            filemode='a',
                            format=self._log_cls.log_format())
        self._logger = logging.getLogger(__name__)
        self.dir_cls = DirectoryValues()
        self.write_cls = Writer()
        self.reader_cls = Reader()
        self.call_types_cls = IpamCallTypes()
        self.filenames_cls = DataFileNames()
        self.ext_call_setup_cls = IpamApiRequest()
        self._network_data = []
        self.dl_lock = threading.Lock()
        max_concurrent_dl = 8
        self.dl_sem = threading.Semaphore(max_concurrent_dl)

    def get_extensible_attributes(self):
        """Requests the extensible attributes defined within DDI."""
        self._logger.info('Pulling current Extensible Attribute data.')

        _ext_attr_data = json.loads(
            self.ext_call_setup_cls.ipam_api_request(
                self.call_types_cls.extensible_attributes()).text)

        self.write_cls.write_to_pkl(self.dir_cls.raw_dir(),
                                    self.filenames_cls.
                                    extensible_attributes_filename(),
                                    _ext_attr_data)
        self._logger.info('Ext Attr data written to .pkl file in Raw Dir.')

    def get_extensible_attributes_list_values(self):
        """
        Requests the extensible attributes listed values defined within DDI.
        """
        self._logger.info('Pulling current Extensible Attribute data.')
        _ext_attr_list_data = json.loads(
            self.ext_call_setup_cls.ipam_api_request(
                self.call_types_cls.extensible_attributes_list_values()).
            text)
        self.write_cls.write_to_pkl(
            self.dir_cls.raw_dir(),
            self.filenames_cls.extensible_attributes_list_values_filename(),
            _ext_attr_list_data)
        self._logger.info('Ext Att list data written to .pkl file in Raw Dir.')

    def get_network_views(self):
        """Requests a the network_view data from DDI."""
        self._logger.info('Pulling current Network View Data.')
        _network_view_data = json.loads(
            self.ext_call_setup_cls.ipam_api_request(
                self.call_types_cls.network_views()).text)

        self.write_cls.write_to_pkl(self.dir_cls.raw_dir(),
                                    self.filenames_cls.
                                    network_views_filename(),
                                    _network_view_data)
        self._logger.info('Network View data written to .pkl file in raw Dir.')

    def _get_ipam_networks(self, call):
        """Multi Threading portion of the requests."""
        self.dl_sem.acquire()
        try:
            networks = json.loads(
                self.ext_call_setup_cls.ipam_api_request(call).text)
            with self.dl_lock:
                self._network_data += networks
        finally:
            self.dl_sem.release()

    def get_networks(self):
        """Requests the networks defined within DDI by view."""
        self._logger.info('Pulling IPAM Networks.')
        self._network_data = []
        network_views = self.return_network_views()
        start = time.perf_counter()
        threads = []
        for _ref in network_views:
            network_call = self.call_types_cls.networks(_ref['name'])
            _t = threading.Thread(target=self._get_ipam_networks,
                                  args=(network_call,))
            _t.start()
            threads.append(_t)

        for _t in threads:
            _t.join()
        end = time.perf_counter()

        self._logger.info("Downloaded %s Networks in %2f seconds",
                          len(self._network_data), end - start)

        self.write_cls.write_to_pkl(self.dir_cls.raw_dir(),
                                    self.filenames_cls.
                                    networks_filename(),
                                    self._network_data)
        self._logger.info('IPAM data written to .pkl file in raw Dir.')

    def get_networkcontainers(self):
        """Requests the networkcontainers defined within DDI by view."""
        self._logger.info('Pulling IPAM Networkcontainers.')
        self._network_data = []
        network_views = self.return_network_views()
        start = time.perf_counter()
        threads = []
        for _ref in network_views:
            network_call = self.call_types_cls.networkcontainers(_ref['name'])
            _t = threading.Thread(target=self._get_ipam_networks,
                                  args=(network_call,))
            _t.start()
            threads.append(_t)

        for _t in threads:
            _t.join()
        end = time.perf_counter()

        self._logger.info("Downloaded %s Networks in %2f seconds",
                          len(self._network_data), end - start)

        self.write_cls.write_to_pkl(self.dir_cls.raw_dir(),
                                    self.filenames_cls.
                                    networkcontainers_filename(),
                                    self._network_data)
        self._logger.info('IPAM data written to .pkl file in raw Dir.')

    def return_network_views(self):
        """Reads in the network views."""
        return self.reader_cls.read_from_pkl(self.dir_cls.raw_dir(),
                                             self.filenames_cls.
                                             network_views_filename())
