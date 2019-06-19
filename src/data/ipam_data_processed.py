import sys
from builder import DirectoryValues
from builder import DataFileNames
from builder import LoggingValues
from builder import Reader
from ipam_apirequest_calltypes_callfilenames import IpamCallFilenames
import pandas as pd
import pickle
from collections import MutableMapping
import json


class IpamDataProcessed:

    def __init__(self):
        self.dir_cls = DirectoryValues()
        self.filename_cls = DataFileNames()
        self.reader_cls = Reader()

    def run_ipam_processed(self, interim_data):
        """Run's through all the methods with the ipam_dump_interim_xlsx file.

        """
        output_data = self.ea_datacenter_processing(
            self.ea_ipr_designation_processing(
                interim_data))
        output_data.to_excel(self.dir_cls.processed_dir() + '\\' +
                             self.filename_cls.ipam_dump_processed_xlsx())
        output_data.to_pickle(self.dir_cls.processed_dir() + '\\' +
                              self.filename_cls.ipam_dump_processed_pickle())

    def load_pickle_file(self, dir, filename):
        return self.reader_cls.read_from_pkl(dir, filename)


    @staticmethod
    def get_listed_values(data):
        ea_updater = {}
        for k, v in data[0].items():
            if isinstance(v, list):
                ea_updater[k] = '; '.join(str(e) for e in v)
        return ea_updater

    @staticmethod
    def put_listed_values(updater_data, source_data, ea):
        for k, v in updater_data.items():
            source_data.at[k, ea] = v
        return source_data

    def ea_datacenter_processing(self, data):
        ea_value = 'extattrs_Datacenter_value'
        dc_data = [data[ea_value].to_dict()]
        updater_dcdata = self.get_listed_values(dc_data)
        return self.put_listed_values(updater_dcdata, data, ea_value)

    def ea_ipr_designation_processing(self, data):
        ea_value = 'extattrs_IPR Designation_value'
        dc_data = [data[ea_value].to_dict()]
        updater_dcdata = self.get_listed_values(dc_data)
        return self.put_listed_values(updater_dcdata, data, ea_value)

