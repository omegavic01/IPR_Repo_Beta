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
from collections import OrderedDict
import pandas as pd
import logging
import time
from ipaddr import IPv4Network
from netaddr import IPNetwork
from builder import Cgn
from builder import DirectoryValues
from builder import DataFileNames
from builder import EnvironmentValues
from builder import LoggingValues
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

    def run_ipam_processing(self, interim_data):
        """Method that runs through all of the interim processing steps.  Then
        writes the panda dataframe to excel and to a pickle file.

        """
        self._logger.info('Starting the final step in data processing.')
        start = time.perf_counter()
        self.panda_processing_of_interim_data(interim_data)
        end = time.perf_counter()
        self._logger.info('Final processed the data in {} seconds'.
                          format(end - start))
        self._logger.info('Finished the final step in data processing.')

    @staticmethod
    def _compiling_data(data):
        vrf_idx_data_dict = {}
        vrf_dict = {}
        vrf_o_and_c_dict = {}
        for i in data:
            if i[15].startswith('00'):
                vrf_idx_data_dict[i[22]] = i

                def _get_vrf_o_c_dict(i, vrf_o_c_dict):
                    if i[15].split('-')[0] not in vrf_o_c_dict:
                        vrf_o_c_dict[i[15].split('-')[0]] = []
                    if i[15].split('-')[0] in vrf_o_c_dict:
                        if not i[23]:
                            pass
                        elif i[23] and isinstance(i[23], str):
                            vrf_o_c_dict[i[15].split('-')[0]] += \
                                list(map(int, i[23].split(',')))
                        elif i[23] and isinstance(i[23], int):
                            vrf_o_c_dict[i[15].split('-')[0]].append(i[23])
                        else:
                            if i[23] and isinstance(i[23], str):
                                vrf_o_c_dict[i[15].split('-')[0]] += \
                                    list(map(int, i[23].split(',')))
                            elif i[23] and isinstance(i[23], int):
                                vrf_o_c_dict[i[15].split('-')[0]].append(i[23])
                        if not i[24]:
                            pass
                        elif i[24] and isinstance(i[24], str):
                            vrf_o_c_dict[i[15].split('-')[0]] += \
                                list(map(int, i[24].split(',')))
                        elif i[24] and isinstance(i[24], int):
                            vrf_o_c_dict[i[15].split('-')[0]].append(i[24])
                        else:
                            if i[24] and isinstance(i[24], str):
                                vrf_o_c_dict[i[15].split('-')[0]] += \
                                    list(map(int, i[24].split(',')))
                            elif i[24] and isinstance(i[24], int):
                                vrf_o_c_dict[i[15].split('-')[0]].append(i[24])
                _get_vrf_o_c_dict(i, vrf_o_and_c_dict)
                if i[15].split('-')[0] not in vrf_dict:
                    vrf_dict[i[15].split('-')[0]] = [i]
                else:
                    vrf_dict[i[15].split('-')[0]].append(i)
        return vrf_idx_data_dict, vrf_dict, vrf_o_and_c_dict

    @staticmethod
    def _check_vrf_record_uncontested_vrfs(vrf_o_c_dict, vrf_idx):
        return_dict = dict()
        clean_vrf_list = list()
        for key in vrf_o_c_dict.keys():
            temp_dict = dict()
            temp_dict[key] = list()
            for o_c in vrf_o_c_dict[key]:
                if o_c in vrf_idx and key not in vrf_idx[o_c][15]:
                    temp_dict[key].append(vrf_idx[o_c][15])
            if temp_dict[key]:
                temp_dict[key] = list(set(temp_dict[key]))
                temp_dict[key] = ', '.join(temp_dict[key])
                return_dict.update(temp_dict)
            else:
                clean_vrf_list.append(temp_dict[key])
        return return_dict, clean_vrf_list

    @staticmethod
    def _check_vrf_against_entire_db(vrf_dict):
        clean_vrf = []
        for key in vrf_dict.keys():
            temp_vrf = []
            for i in vrf_dict[key]:
                if 'NO' in i[25] or 'NO' in i[26]:
                    temp_vrf.append('NO')
                    break
                else:
                    temp_vrf.append(key)
            if not temp_vrf or 'NO' in temp_vrf:
                continue
            else:
                clean_vrf.append(list(set(temp_vrf)))
        return clean_vrf

    @staticmethod
    def _conflict_overlap_check(master_interim_df):
        m_list_index = master_interim_df['Index'].to_list()
        m_list_cidr = master_interim_df['IPv4 Subnet'].to_list()
        m_list_cidr_set = list(OrderedDict.fromkeys(m_list_cidr))
        m_cidr_index_zip = list(zip(m_list_cidr, m_list_index))
        m_dict_overlap = {}
        m_dict_conflict = {}
        for i in m_list_cidr_set:
            m_dict_overlap[i] = []
            m_dict_conflict[i] = []
        for item in m_cidr_index_zip:
            if item[0] in m_dict_conflict:  # Conflict check
                m_dict_conflict[item[0]].append(item[1])
        for item in m_cidr_index_zip:
            for _ip in m_list_cidr_set:
                if int(_ip.split('.')[0]) < int(item[0].split('.')[0]):
                    continue
                if int(_ip.split('.')[1]) < int(item[0].split('.')[1]):
                    continue
                elif _ip == item[0]:
                    continue
                elif _ip.split('.')[0:2] == item[0].split('.')[0:2]:
                    if IPNetwork(_ip) in IPNetwork(item[0]):
                        m_dict_overlap[_ip].append(item[1])
                        continue
                elif int(item[0].split('.')[1]) < int(_ip.split('.')[1]):
                    break
                else:
                    print(item)
        return m_dict_overlap, m_dict_conflict

    def master_and_uncategorized_sheet_processing(self, master_data):
        """This method takes a copy of the full dataframe.  Processes it and
        returns the mashed data for writing the Master Sheet and Uncategorized
        Sheet.

        """
        temp_df = master_data.copy()
        # Filter out uneeded data.
        temp_df = temp_df.loc[
            (temp_df['extattrs_IPR Designation_value'] != 'leaf') &
            (temp_df['extattrs_IPR Designation_value'] != 'dup') &
            (temp_df['extattrs_IPR Designation_value'] != 'ignore') &
            (temp_df['extattrs_IPR Designation_value'] != 'divest') &
            (temp_df['extattrs_IPR Designation_value'] != 're-ip') &
            (temp_df['extattrs_IPR Designation_value'] != 'drop reserve') &
            (temp_df['extattrs_IPR Designation_value'] != 'parent') &
            (temp_df['/Cidr'] != 32) &
            (temp_df['network'] != '100.88.0.0/29') &
            (temp_df['network'] != '100.64.0.0/29') &
            (temp_df['network_view'] != 'Public-IP')]

        # Convert to dict for data processing.
        temp_dict = temp_df.to_dict('index')
        temp_master_dict = {}
        temp_uncategorized_dict = {}
        # Pull data out uncategorized data.
        for key in temp_dict.keys():
            if IPv4Network(temp_dict[key]['network']).is_private or \
                    Cgn.is_cgn(IPv4Network(temp_dict[key]['network'])):
                temp_master_dict.update({key: temp_dict[key]})
            else:
                temp_uncategorized_dict.update({key: temp_dict[key]})

        master_df = pd.DataFrame.from_dict(temp_master_dict, orient='index')
        uncategorized_df = pd.DataFrame.from_dict(
            temp_uncategorized_dict, orient='index')

        # Rename column header
        header_dict = self.env_cls.header_row_dict()
        master_df.rename(columns=header_dict, inplace=True)
        master_df = master_df.reset_index()
        del master_df['index']
        master_df['Index'] = master_df.index + 10001

        # Performs Conflict and Overlap Check
        master_overlaps, master_conflicts = \
            self._conflict_overlap_check(master_df)
        master_df['Conflict Subnet Overlap - Index No.'] = ''
        master_df['Conflict Subnet - Index No.'] = ''
        master_df['No Overlap'] = ''
        master_df['No Conflict'] = ''
        master_df['Conflict Subnet Overlap - Count'] = ''
        master_df['Conflict Subnet - Count'] = ''
        for row in master_df.index.values:
            if master_overlaps[master_df.loc[row, 'IPv4 Subnet']]:
                if len(master_overlaps[master_df.loc[row, 'IPv4 Subnet']]) > 1:
                    master_df.loc[
                        row, 'Conflict Subnet Overlap - Index No.'] = \
                        ', '.join(str(e) for e in master_overlaps[
                            master_df.loc[row, 'IPv4 Subnet']])
                    master_df.loc[
                        row, 'Conflict Subnet Overlap - Count'] = \
                        len(master_overlaps[master_df.loc[row, 'IPv4 Subnet']])
                else:
                    master_df.loc[
                        row, 'Conflict Subnet Overlap - Index No.'] = \
                        master_overlaps[master_df.loc[row, 'IPv4 Subnet']][0]
                    master_df.loc[row, 'Conflict Subnet Overlap - Count'] = 1
                master_df.loc[row, 'No Overlap'] = 'NO'
            else:
                master_df.loc[row, 'No Overlap'] = 'YES'
            if len(master_conflicts[master_df.loc[row, 'IPv4 Subnet']]) > 2:
                temp_list = master_conflicts[
                    master_df.loc[row, 'IPv4 Subnet']].copy()
                temp_list.remove(row + 10001)
                master_df.loc[row, 'Conflict Subnet - Index No.'] = \
                    ', '.join(str(e) for e in temp_list)
                master_df.loc[row, 'No Conflict'] = 'NO'
                master_df.loc[row, 'Conflict Subnet - Count'] = len(temp_list)
            elif len(master_conflicts[master_df.loc[row, 'IPv4 Subnet']]) == 2:
                temp_list = master_conflicts[
                    master_df.loc[row, 'IPv4 Subnet']].copy()
                temp_list.remove(row + 10001)
                master_df.loc[row, 'Conflict Subnet - Index No.'] = \
                    temp_list[0]
                master_df.loc[row, 'No Conflict'] = 'NO'
                master_df.loc[row, 'Conflict Subnet - Count'] = 1
            else:
                master_df.loc[row, 'No Conflict'] = 'YES'

        return master_df, uncategorized_df

    def panda_processing_of_interim_data(self, interim_data):
        workbook_file = self.dir_cls.processed_dir() + '\\' + \
                        self.filename_cls.processed_filename()
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
        writer = pd.ExcelWriter(workbook_file, engine='xlsxwriter')

        # Master and Uncategorized processing.
        master_df, uncategorized_df = \
            self.master_and_uncategorized_sheet_processing(processing_data)
        master_df.to_excel(writer, sheet_name='Master', index=False)
        master_df_to_list = master_df.values.tolist()
        vrf_idx, vrf_dict, vrf_o_c_dict = \
            self._compiling_data(master_df_to_list)
        clear_vrf = self._check_vrf_against_entire_db(vrf_dict)
        clear_vrf_df = pd.DataFrame(clear_vrf)

        vrf_summaries, clean_vrfs = self._check_vrf_record_uncontested_vrfs(
            vrf_o_c_dict, vrf_idx)
        vrf_summaries_df = pd.DataFrame.from_dict(vrf_summaries,
                                                  orient='index')

        # Full Dataset sheet
        processing_data.to_excel(writer, sheet_name='Full-Dataset',
                                 index=False,
                                 header=self.env_cls.header_row_list())
        # IPR Designation Filters Sheets
        processing_data[processing_data[
            'extattrs_IPR Designation_value'].isin(['leaf'])].to_excel(
            writer, sheet_name='Filt-Leaf', index=False,
            header=self.env_cls.header_row_list())
        processing_data[processing_data[
            'extattrs_IPR Designation_value'].isin(['dup'])].to_excel(
            writer, sheet_name='Filt-Dup', index=False,
            header=self.env_cls.header_row_list())
        processing_data[processing_data[
            'extattrs_IPR Designation_value'].isin(['ignore'])].to_excel(
            writer, sheet_name='Filt-Ignore', index=False,
            header=self.env_cls.header_row_list())
        processing_data[processing_data[
            'extattrs_IPR Designation_value'].isin(['divest'])].to_excel(
            writer, sheet_name='Filt-Divest', index=False,
            header=self.env_cls.header_row_list())
        processing_data[processing_data[
            'extattrs_IPR Designation_value'].isin(['re-ip'])].to_excel(
            writer, sheet_name='Filt-Re-IP', index=False,
            header=self.env_cls.header_row_list())
        processing_data[processing_data[
            'extattrs_IPR Designation_value'].isin(['drop reserve'])].to_excel(
            writer, sheet_name='Filt-Drop Reserve', index=False,
            header=self.env_cls.header_row_list())
        processing_data[processing_data[
            'extattrs_IPR Designation_value'].isin(['parent'])].to_excel(
            writer, sheet_name='Filt-OMC-IT-Parent Subnet', index=False,
            header=self.env_cls.header_row_list())
        # IP Address Filters
        processing_data[processing_data[
            '/Cidr'].isin([32])].to_excel(
            writer, sheet_name='Filt-Cidr-32', index=False,
            header=self.env_cls.header_row_list())
        processing_data[processing_data[
            'network'].isin(['100.88.0.0/29'])].to_excel(
            writer, sheet_name='Filt-100.88-Cidr-29', index=False,
            header=self.env_cls.header_row_list())
        processing_data[processing_data[
            'network'].isin(['100.64.0.0/29'])].to_excel(
            writer, sheet_name='Filt-100.64-Cidr-29', index=False,
            header=self.env_cls.header_row_list())
        # Network View Filters
        processing_data[processing_data[
            'network_view'].isin(['Public-IP'])].to_excel(
            writer, sheet_name='Filt-Public-IP-View', index=False,
            header=self.env_cls.header_row_list())
        # Uncategorized Sheet
        uncategorized_df.to_excel(
            writer, sheet_name='Filt-Uncategorized', index=False,
            header=self.env_cls.header_row_list())
        clear_vrf_df.to_excel(
            writer, sheet_name='Clear-VRF', index=False,
            header=["Clear VRF's"])
        vrf_summaries_df.to_excel(
            writer, sheet_name='Filt-Conflicting-VRF', index=True,
            header=["Conflicting VRF's"], index_label='VRF #')

        # Formatting Workbook
        workbook = writer.book
        worksheet = writer.sheets['Master']
        left = workbook.add_format({'align': 'left'})
        worksheet.set_column('W:Y', None, left)
        writer.save()


