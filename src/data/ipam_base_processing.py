#!/usr/bin/python
"""
Copyright 2007 HVictor
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
from collections import MutableMapping
import logging
from builder import DirectoryValues
from builder import DataFileNames
from builder import EnvironmentValues
from builder import LoggingValues
from builder import Reader
from builder import Writer


class BaseIpamProcessing:
    """Base class for ipam data processing."""
    def __init__(self):
        self._log_cls = LoggingValues()
        logging.basicConfig(filename=self._log_cls.log_filename(),
                            level=logging.DEBUG,
                            filemode='a',
                            format=self._log_cls.log_format())
        self._logger = logging.getLogger(__name__)
        self.dir_cls = DirectoryValues()
        self.filename_cls = DataFileNames()
        self.env_cls = EnvironmentValues()
        self.reader_cls = Reader()
        self.writer_cls = Writer()

    def _convert_flatten(self, data, parent_key='', sep='_'):
        """
        Method to convert input of nested dict's to a flattened dict

        default seperater '_'
        """
        items = []
        for key, value in data.items():
            new_key = parent_key + sep + key if parent_key else key

            if isinstance(value, MutableMapping):
                items.extend(
                    self._convert_flatten(value, new_key, sep=sep).items())
            else:
                items.append((new_key, value))
        return dict(items)

    def _flatten_data(self, data_to_be_flattened):
        """Method to flatten the requested data."""
        return [
            self._convert_flatten(data_to_be_flattened[i])
            for i in range(len(data_to_be_flattened))
        ]

    def split_out_network(self, _df, column_to_split):
        """Method for splitting out a subnet and assigning to columns."""
        oct_listed = self.oct_list()
        network_col = _df[column_to_split].str.split(".", expand=True)
        _df[oct_listed[0]] = network_col[0].astype(str).astype(int)
        _df[oct_listed[1]] = network_col[1].astype(str).astype(int)
        _df[oct_listed[2]] = network_col[2].astype(str).astype(int)
        split_third_value = network_col[3].str.split("/", expand=True)
        _df[oct_listed[3]] = split_third_value[0].astype(str).astype(int)
        _df[oct_listed[4]] = split_third_value[1].astype(str).astype(int)
        return _df

    def sort_df_by_oct_list(self, _df):
        """Method for sorting oct_list columns in ascending order."""
        return _df.sort_values(
            self.oct_list(), ascending=[True, True, True, True, True])

    @staticmethod
    def oct_list():
        """Column header for splitting out a subnet."""
        return ['Oc-1', 'Oc-2', 'Oc-3', 'Oc-4', '/Cidr']

    @staticmethod
    def get_listed_values(data):
        """
        Loops through data and identifies a list.  If list then convert
        to a string seperated by a ;.
        """
        ea_updater = {}
        for key, value in data[0].items():
            if isinstance(value, list) and value:
                ea_updater[key] = ', '.join(str(e) for e in sorted(value))
        return ea_updater

    @staticmethod
    def put_listed_values(updater_data, source_data, ea_att):
        """
        Replaces the converted listed values to the source dataset values.
        This follows get_listed_values.
        """
        for key, value in updater_data.items():
            source_data.at[key, ea_att] = value
        return source_data

    @staticmethod
    def reindex_df(_df):
        """Function for indexing of subnets."""
        _df.index = range(len(_df.index))
        _df.index += 10000
        return _df
