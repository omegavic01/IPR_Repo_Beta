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
from collections import MutableMapping
import pandas as pd
import logging
import time
import json
from ipaddr import IPv4Network
from builder import Cgn
from builder import DirectoryValues
from builder import DataFileNames
from builder import EnvironmentValues
from builder import LoggingValues
from builder import ProjMiscValues
from builder import Reader
from builder import Writer


class _BaseIpamProcessing:

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
        self.misc_values_cls = ProjMiscValues()
        self.reader_cls = Reader()
        self.writer_cls = Writer()

    def _convert_flatten(self, data, parent_key='', sep='_'):
        """Method to convert input of nested dict's to a flattened dict

        default seperater '_'

        """
        items = []
        for key, value in data.items():
            new_key = parent_key + sep + key if parent_key else key

            if isinstance(value, MutableMapping):
                items.extend(self._convert_flatten(
                    value, new_key, sep=sep).items())
            else:
                items.append((new_key, value))
        return dict(items)

    def _flatten_data(self, data_to_be_flattened):
        """Method to flatten the requested data."""
        return [self._convert_flatten(data_to_be_flattened[i])
                for i in range(len(data_to_be_flattened))]

    @staticmethod
    def get_listed_values(data):
        """Loops through data and identifies a list.  If list then convert
        to a string seperated by a ;.

        """
        ea_updater = {}
        for key, value in data[0].items():
            if isinstance(value, list):
                ea_updater[key] = '; '.join(str(e) for e in value)
        return ea_updater

    @staticmethod
    def put_listed_values(updater_data, source_data, ea_att):
        """Replaces the converted listed values to the source dataset values.
        This follows get_listed_values.

        """
        for key, value in updater_data.items():
            source_data.at[key, ea_att] = value
        return source_data


class IpamDataInterim(_BaseIpamProcessing):
    """Class to read in networks and networkcontainers to then be smashed,
    mangled, and spit out into a .pickle and .xlsx file

    """

    def run_ipam_interim(self,
                         raw_data,
                         xlsx_filename,
                         panda_filename,
                         dicted_filename):
        """Method that runs through all of the interim processing steps.  Then
        writes the panda dataframe to excel and to a pickle file.

        """
        self._logger.info('Starting the interim process for the raw data.')
        start = time.perf_counter()
        output_data = \
            self.ea_ipr_designation_processing(
                self.ea_datacenter_processing(
                    self.panda_processing_of_flattened_data(
                        self._flatten_data(
                            raw_data))))

        output_data.to_excel(self.dir_cls.interim_dir() + '\\' +
                             xlsx_filename)
        output_data.to_pickle(self.dir_cls.interim_dir() + '\\' +
                              panda_filename)
        self.writer_cls.write_to_pkl(
            self.dir_cls.interim_dir(),
            dicted_filename,
            output_data.to_dict())

        end = time.perf_counter()
        self._logger.info('Interim processed the data in {} seconds'.
                          format(end - start))
        self._logger.info('Finished the interim processing step.')

    def get_raw_data_networks_networkcontainers(self):
        """Gets the network and networkcontainer data.  Returns the two
        datasets as one list.

        """
        networks = self.reader_cls.read_from_pkl(
            self.dir_cls.raw_dir(),
            self.filename_cls.networks_filename())
        networkcontainers = self.reader_cls.read_from_pkl(
            self.dir_cls.raw_dir(),
            self.filename_cls.networkcontainers_filename())
        return networks + networkcontainers

    def ea_datacenter_processing(self, data):
        """Processes the ea_datacenter column.  To be have any lists converted
        to strings and seperated by a ;.

        """
        ea_value = 'extattrs_Datacenter_value'
        dc_data = [data[ea_value].to_dict()]
        updater_dcdata = self.get_listed_values(dc_data)
        return self.put_listed_values(updater_dcdata, data, ea_value)

    def ea_ipr_designation_processing(self, data):
        """Processes the ea_ipr_designation column.  To convert any lists to
        strings and seperated by a ;.

        """
        ea_value = 'extattrs_IPR Designation_value'
        dc_data = [data[ea_value].to_dict()]
        updater_dcdata = self.get_listed_values(dc_data)
        return self.put_listed_values(updater_dcdata, data, ea_value)

    @staticmethod
    def panda_processing_of_flattened_data(raw_nets):
        """Turns the returned flat dict into a panda dataframe.

        Further processing:

        1. Add 'net_type' column.
        2. Add oct1, oct2, oct3, oct4, and /Cidr columns.
        3. Add oct1, oct2, oct3, oct4, and /Cidr columns.
        4. Sorting Data via line 2 values.
        5. Return Indexed data starting at 10000
        """

        net_flat_df = pd.DataFrame(raw_nets)

        # Further processing Line 1.
        net_flat_df['net_type'] = net_flat_df['_ref'].str.split(
            '/', expand=True)[0]

        # Further processing Line 2.
        oct_list = ['Oc-1', 'Oc-2', 'Oc-3', 'Oc-4', '/Cidr']
        network_col = net_flat_df['network'].str.split(".", expand=True)
        net_flat_df[oct_list[0]] = network_col[0].astype(str).astype(int)
        net_flat_df[oct_list[1]] = network_col[1].astype(str).astype(int)
        net_flat_df[oct_list[2]] = network_col[2].astype(str).astype(int)
        split_third_value = network_col[3].str.split("/", expand=True)
        net_flat_df[oct_list[3]] = split_third_value[0].astype(str).astype(int)
        net_flat_df[oct_list[4]] = split_third_value[1].astype(str).astype(int)

        # Further processesing Line 3.
        network_col = net_flat_df['network'].str.split("/", expand=True)
        net_flat_df['IP Subnet'] = network_col[0].astype(str)
        net_flat_df['IP Cidr'] = network_col[1].astype(str).astype(int)

        # Further processing Line 4.
        net_flat_df = net_flat_df.sort_values(
            oct_list, ascending=[True, True, True, True, True]
        )

        # Further processing Line 5.
        net_flat_df.index = range(len(net_flat_df.index))
        net_flat_df.index += 10000
        return net_flat_df


class IpamDataProcessed(_BaseIpamProcessing):

    def run_ipam_interim(self, interim_data, xlsx, pickle):
        """Method that runs through all of the interim processing steps.  Then
        writes the panda dataframe to excel and to a pickle file.

        """
        self._logger.info('Starting the final step in data processing.')
        start = time.perf_counter()
        output_data = \
            self.ea_ipr_designation_processing(
                self.ea_datacenter_processing(
                    self.panda_processing_of_flattened_data(
                        self._flatten_data(
                            interim_data))))

        output_data.to_excel(self.dir_cls.processed_dir() + '\\' + xlsx)
        output_data.to_pickle(self.dir_cls.processed_dir() + '\\' + pickle)
        end = time.perf_counter()
        self._logger.info('Final processed the data in {} seconds'.
                          format(end - start))
        self._logger.info('Finished the final step in data processing.')

    def panda_processing_of_interim_data(self, interim_data):
        processing_data = interim_data[
            ['network', 'extattrs_Region_List_value', 'extattrs_Country_value',
             'extattrs_City_value',
             'extattrs_Address_value', 'extattrs_Site_value',
             'extattrs_Datacenter_value',
             'extattrs_Division_value', 'extattrs_Requester Email_value',
             'extattrs_Agency_value',
             'extattrs_VLAN Description_value', 'comment',
             'extattrs_Interface Name_value',
             'net_type', 'network_view', 'extattrs_IPR Designation_value',
             'Oc-1', 'Oc-2', 'Oc-3', 'Oc-4',
             '/Cidr']].copy()
        processing_data.insert(loc=0, column='Disposition', value='')
        writer = pd.ExcelWriter('multiple_sheets.xlsx', engine='xlsxwriter')
        temp_df = processing_data.copy()
        # Master IPR Designation Filtering
        temp_df = temp_df[temp_df['extattrs_IPR Designation_value'] != 'leaf']
        temp_df = temp_df[temp_df['extattrs_IPR Designation_value'] != 'dup']
        temp_df = temp_df[temp_df['extattrs_IPR Designation_value'] != 'ignore']
        temp_df = temp_df[temp_df['extattrs_IPR Designation_value'] != 'divest']
        temp_df = temp_df[temp_df['extattrs_IPR Designation_value'] != 're-ip']
        temp_df = temp_df[temp_df['extattrs_IPR Designation_value'] != 'drop reserve']
        temp_df = temp_df[temp_df['extattrs_IPR Designation_value'] != 'parent']
        # Master IP Address Filters
        temp_df = temp_df[temp_df['/Cidr'] != 32]
        temp_df = temp_df[temp_df['network'] != '100.88.0.0/29']
        temp_df = temp_df[temp_df['network'] != '100.64.0.0/29']
        # Network View Filters
        temp_df = temp_df[temp_df['network_view'] != 'Public-IP']

        # Take filtered dataframe and create uncatagorized and master.

        temp_dict = temp_df.to_dict('index')
        temp_master_dict = {}
        temp_uncategorized_dict = {}
        for key in temp_dict.keys():
            if IPv4Network(temp_dict[key]['network']).is_private or \
                    Cgn.is_cgn(IPv4Network(temp_dict[key]['network'])):
                temp_master_dict.update({key: temp_dict[key]})
            else:
                temp_uncategorized_dict.update({key: temp_dict[key]})

        master_df = pd.DataFrame.from_dict(temp_master_dict, orient='index')
        uncategorized_df = pd.DataFrame.from_dict(temp_uncategorized_dict, orient='index')

        # Rename column header
        header_dict = self.env_cls.header_row_dict()
        master_df.rename(columns=header_dict, inplace=True)
        master_df = master_df.reset_index()
        del master_df['index']
        master_df['Index'] = master_df.index + 10001
        master_df.to_excel(writer, sheet_name='Master', index=False)
        # Full Dataset sheet
        processing_data.to_excel(writer, sheet_name='Full-Dataset', index=False)
        # Filt-Uncategorized sheet
        uncategorized_df.to_excel(writer, sheet_name='Filt-Uncategorized', index=False)
        # IPR Designation Filters Sheets
        # processing_data[processing_data['extattrs_IPR Designation_value'].isin(['leaf'])].to_excel(writer, sheet_name='Filt-Leaf', index=False)
        processing_data[processing_data['extattrs_IPR Designation_value'].isin(['leaf'])].to_excel(writer, sheet_name='Filt-Leaf', index=False, header=self.env_cls.header_row_list())
        processing_data[processing_data['extattrs_IPR Designation_value'].isin(['dup'])].to_excel(writer, sheet_name='Filt-Dup', index=False)
        processing_data[processing_data['extattrs_IPR Designation_value'].isin(['ignore'])].to_excel(writer, sheet_name='Filt-Ignore', index=False)
        processing_data[processing_data['extattrs_IPR Designation_value'].isin(['divest'])].to_excel(writer, sheet_name='Filt-Divest', index=False)
        processing_data[processing_data['extattrs_IPR Designation_value'].isin(['re-ip'])].to_excel(writer, sheet_name='Filt-Re-IP', index=False)
        processing_data[processing_data['extattrs_IPR Designation_value'].isin(['drop reserve'])].to_excel(writer, sheet_name='Filt-Drop Reserve', index=False)
        processing_data[processing_data['extattrs_IPR Designation_value'].isin(['parent'])].to_excel(writer, sheet_name='Filt-OMC-IT-Parent Subnet', index=False)
        # IP Address Filters
        processing_data[processing_data['/Cidr'].isin([32])].to_excel(writer, sheet_name='Filt-Cidr-32', index=False)
        processing_data[processing_data['network'].isin(['100.88.0.0/29'])].to_excel(writer, sheet_name='Filt-100.88-Cidr-29', index=False)
        processing_data[processing_data['network'].isin(['100.64.0.0/29'])].to_excel(writer, sheet_name='Filt-100.64-Cidr-29', index=False)
        # Network View Filters
        processing_data[processing_data['network_view'].isin(['Public-IP'])].to_excel(writer, sheet_name='Filt-Public-IP-View', index=False)

        # Prepare Master Sheet


        writer.save()

