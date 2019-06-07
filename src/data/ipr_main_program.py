from builder import EnvironmentValues, DirectoryValues, LoggingValues
from builder import Writer, Reader
from ddi_ipam_pull import DdiCallTypes, IpamApiRequestGet, DdiCallFilenames
import logging
import time
import threading


class _BaseProgramClass:

    def __init__(self):
        self._log_cls = LoggingValues()
        logging.basicConfig(filename=self._log_cls.log_filename(),
                            level=logging.DEBUG,
                            filemode='a',
                            format=self._log_cls.log_format())
        self._logger = logging.getLogger(__name__)
        self._logger.info('Loading Project Environment Variables.')
        self.env_cls = EnvironmentValues()
        self.dir_cls = DirectoryValues()
        self.write_cls = Writer()
        self.reader_cls = Reader()
        self.call_types_cls = DdiCallTypes()
        self.filenames_cls = DdiCallFilenames()
        self.ext_call_setup_cls = IpamApiRequestGet()
        self._logger.info('Project Environment Variables Loaded.')
        self._network_data = []
        self.dl_lock = threading.Lock()
        max_concurrent_dl = 8
        self.dl_sem = threading.Semaphore(max_concurrent_dl)


class ProgramClass(_BaseProgramClass):

    def extensible_attribute_call(self):
        self._logger.info('Pulling current Extensible Attribute data.')
        _ext_attr_data = self.ext_call_setup_cls.ddi_call(
                         self.call_types_cls.extensible_attributes())
        self.write_cls.write_to_pkl(self.dir_cls.raw_dir(),
                                    self.filenames_cls.
                                    extensible_attributes_filename(),
                                    _ext_attr_data)
        self._logger.info('Ext Attr data written to .pkl file in Raw Dir.')

    def network_view_call(self):
        self._logger.info('Pulling current Network View Data.')
        _network_view_data = self.ext_call_setup_cls.ddi_call(
                            self.call_types_cls.
                            network_views())
        self.write_cls.write_to_pkl(self.dir_cls.raw_dir(),
                                    self.filenames_cls.
                                    network_views_filename(),
                                    _network_view_data)
        self._logger.info('Network View data written to .pkl file in raw Dir.')

    def _get_network(self, view):
        self.dl_sem.acquire()
        try:
            networks = self.ext_call_setup_cls.ddi_call(self.call_types_cls.
                                                        networks(view))
            with self.dl_lock:
                self._network_data += networks
        finally:
            self.dl_sem.release()

    def get_networks(self):
        self._logger.info('Pulling current IPAM Data.')
        network_views = self.reader_cls.read_from_pkl(
                            self.dir_cls.raw_dir(),
                            self.filenames_cls.
                            network_views_filename())
        start = time.perf_counter()
        threads = []
        for _ref in network_views:
            t = threading.Thread(target=self._get_network,
                                 args=(_ref['name'],))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
        end = time.perf_counter()

        self._logger.info("Downloaded {} Networks in {} seconds".
                          format(len(self._network_data), end - start))

        self.write_cls.write_to_pkl(self.dir_cls.raw_dir(),
                                    self.filenames_cls.networks_filename(),
                                    self._network_data)
        self._logger.info('Network Data written to .pkl file in raw Dir.')

