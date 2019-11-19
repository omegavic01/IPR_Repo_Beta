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

import time
from collections import OrderedDict
from ipaddr import IPv4Network
from netaddr import IPNetwork
import netaddr
from pandas import pandas as pd
from builder import Cgn
from ipam_base_processing import BaseIpamProcessing


class IpamDataProcessed(BaseIpamProcessing):
    """Processing phase of the IPAM data."""

    def __init__(self):
        BaseIpamProcessing.__init__(self)

        # Pulls in interim data file for processing.
        self.workbook_file = self.dir_cls.processed_dir() + '\\' + \
            self.filename_cls.processed_filename()

        # Builds pandas writer object.
        self.writer = pd.ExcelWriter(self.workbook_file, engine='xlsxwriter')

    def run_ipam_processing(self):
        """
        Method that runs through all of the interim processing steps.  Then
        writes the panda dataframe to excel and to a pickle file.

        """
        self._logger.info('Starting the final step in data processing.')
        start = time.perf_counter()
        self.panda_processing_of_interim_data()
        end = time.perf_counter()
        time_taken = end - start
        self._logger.info('Final processed the data in %2f seconds',
                          time_taken)
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
    def summary_conflict_overlap_check(summary_df):
        """
        Main Logic for the conflict and overlap check.

        Returns two dictionaries:
            str(m_dict_overlap): list(indexes of the key (subnet) that
                                overlaps.
            str(m_dict_conflict): list(indexes of the key(subnet) that
                                conflicts.

        """

        """
        Builds a list with all the subnets and indexes in the following format:
                <class 'tuple'>: ('10.0.0.0/16', 10001)
                <class 'tuple'>: ('10.0.0.0/22', 10002)

        """
        cidr_index_zip = list(zip(summary_df['IPv4 Subnet'].to_list(),
                                  summary_df['Index'].to_list(),
                                  )
                              )

        # Builds a list of unique cidr's while maintaining order.
        list_cidr_set = list(OrderedDict.fromkeys(
            summary_df['IPv4 Subnet'].to_list()))

        # Builds dictionaries for storage of data.
        dict_overlap = {}
        dict_conflict = {}

        # Unique list of cidr values become the keys to the dictionaries.
        for i in list_cidr_set:
            dict_overlap[i] = []
            dict_conflict[i] = []

        # IPAM conflict check.
        for item in cidr_index_zip:
            if item[0] in dict_conflict:
                dict_conflict[item[0]].append(item[1])

        # IPAM overlap check.
        for item in cidr_index_zip:
            for _ip in list_cidr_set:
                if int(_ip.split('.')[0]) < int(item[0].split('.')[0]):
                    continue
                if int(_ip.split('.')[1]) < int(item[0].split('.')[1]):
                    continue
                elif _ip == item[0]:
                    continue
                elif _ip.split('.')[0:2] == item[0].split('.')[0:2]:
                    if IPNetwork(_ip) in IPNetwork(item[0]):
                        dict_overlap[_ip].append(item[1])
                        continue
                elif int(item[0].split('.')[1]) < int(_ip.split('.')[1]):
                    break
                else:
                    print(
                        item)  # Need to update this statement to send to log.

        # Returns the dictionaries with offending indexes in a list
        return dict_overlap, dict_conflict

    @staticmethod
    def summary_update_df_conflict_overlap_data(overlaps,
                                                conflicts,
                                                summary_df):
        """
        Function to build out the summary dataframe with the identified
        information gathered from the _conflict_overlap_check function call.

        """

        # Adds new columns to the summary dataframe.
        summary_df['Conflict Subnet Overlap - Index No.'] = ''
        summary_df['Conflict Subnet - Index No.'] = ''
        summary_df['No Overlap'] = ''
        summary_df['No Conflict'] = ''
        summary_df['Conflict Subnet Overlap - Count'] = ''
        summary_df['Conflict Subnet - Count'] = ''

        # Loops through to update new columns.
        for row in summary_df.index.values:
            # Overlap Updates.
            if overlaps[summary_df.loc[row, 'IPv4 Subnet']]:
                if len(overlaps[summary_df.loc[row, 'IPv4 Subnet']]) > 1:
                    summary_df.loc[
                        row, 'Conflict Subnet Overlap - Index No.'] = \
                        ', '.join(str(e) for e in overlaps[
                            summary_df.loc[row, 'IPv4 Subnet']])
                    summary_df.loc[
                        row, 'Conflict Subnet Overlap - Count'] = \
                        len(overlaps[summary_df.loc[row, 'IPv4 Subnet']])
                else:
                    summary_df.loc[
                        row, 'Conflict Subnet Overlap - Index No.'] = \
                        overlaps[summary_df.loc[row, 'IPv4 Subnet']][0]
                    summary_df.loc[row, 'Conflict Subnet Overlap - Count'] = 1
                summary_df.loc[row, 'No Overlap'] = 'NO'
            else:
                summary_df.loc[row, 'No Overlap'] = 'YES'
            # Conflict Updates.
            if len(conflicts[summary_df.loc[row, 'IPv4 Subnet']]) > 2:
                temp_list = conflicts[
                    summary_df.loc[row, 'IPv4 Subnet']].copy()
                temp_list.remove(row + 10001)
                summary_df.loc[row, 'Conflict Subnet - Index No.'] = \
                    ', '.join(str(e) for e in temp_list)
                summary_df.loc[row, 'No Conflict'] = 'NO'
                summary_df.loc[row, 'Conflict Subnet - Count'] = len(temp_list)
            elif len(conflicts[summary_df.loc[row, 'IPv4 Subnet']]) == 2:
                temp_list = conflicts[
                    summary_df.loc[row, 'IPv4 Subnet']].copy()
                temp_list.remove(row + 10001)
                summary_df.loc[row, 'Conflict Subnet - Index No.'] = \
                    temp_list[0]
                summary_df.loc[row, 'No Conflict'] = 'NO'
                summary_df.loc[row, 'Conflict Subnet - Count'] = 1
            else:
                summary_df.loc[row, 'No Conflict'] = 'YES'

    def _tweak_and_save_workbook(self):
        workbook = self.writer.book
        worksheet_summary = self.writer.sheets['Summary']
        left = workbook.add_format({'align': 'left'})
        worksheet_summary.set_column('W:Y', None, left)
        self.writer.save()

    def _build_free_space_tab(self, unique_subnets):

        def find_free_space(start, end):
            free_space = []
            range_to_cidrs = netaddr.iprange_to_cidrs(start, end)

            def compare_networks(range_to_cidrs_data):
                for inet in range_to_cidrs_data:
                    if IPNetwork(inet) == IPNetwork(start) or IPNetwork(
                            inet) == IPNetwork(end):
                        continue
                    elif IPNetwork(start) in IPNetwork(inet) and IPNetwork(
                            end) in IPNetwork(inet):
                        temp_ip_list = netaddr.cidr_exclude(
                            IPNetwork(inet),
                            IPNetwork(start))
                        if IPNetwork(end) in temp_ip_list and len(
                                temp_ip_list) > 1:
                            temp_ip_list.remove(IPNetwork(end))
                            free_space.extend(temp_ip_list)
                            continue
                    elif IPNetwork(start) in IPNetwork(inet):
                        free_space.extend(
                            netaddr.cidr_exclude(IPNetwork(inet),
                                                 IPNetwork(
                                                     start)))
                        continue
                    elif IPNetwork(end) in IPNetwork(inet):
                        free_space.extend(
                            netaddr.cidr_exclude(IPNetwork(inet),
                                                 IPNetwork(end)))
                        continue
                    else:
                        free_space.append(IPNetwork(inet))
                return free_space

            return compare_networks(range_to_cidrs)

        # Free Space Check
        ipnetwork_addr = []
        for addr in unique_subnets:
            ipnetwork_addr.append(addr)
        cidr_merged_addresses_list = netaddr.cidr_merge(ipnetwork_addr)
        merged_free_space = []
        for enum, net in enumerate(cidr_merged_addresses_list):
            if len(cidr_merged_addresses_list) == enum + 1:
                continue
            temp_data = find_free_space(net,
                                        cidr_merged_addresses_list[
                                            enum + 1])
            if temp_data:
                merged_free_space.extend(temp_data)
        private_free_space = []
        for ipnetwork in merged_free_space:
            if ipnetwork.is_private():
                private_free_space.append(ipnetwork)

        # Convert to string then process
        free_space_list_of_strings = []
        for ipnetwork in private_free_space:
            _ip = ipnetwork.__str__()
            split_subnet = _ip.split('.')
            split_cidr = split_subnet[3].split('/')
            temp_subnet_list = (
                _ip, int(split_subnet[0]), int(split_subnet[1]),
                int(split_subnet[2]), int(split_cidr[0]),
                int(split_cidr[1]))
            free_space_list_of_strings.append(temp_subnet_list)

        free_space_labels = [
            'IPv4 Subnet', 'Oc-1', 'Oc-2', 'Oc-3', 'Oc-4', 'Cidr']
        free_space_df = pd.DataFrame.from_records(
            free_space_list_of_strings,
            columns=free_space_labels)
        free_space_df = free_space_df.sort_values('Cidr', ascending=True)

        free_space_df.to_excel(
            self.writer, sheet_name='Summary_Free_Space', index=False)
        self.writer_cls.write_to_pkl(
            self.dir_cls.raw_dir(),
            self.filename_cls.free_space_df_filename(),
            free_space_df)

    def _vrf_summaries_processing_tab(self, vrf_index, vrf_o_c_dictionary):
        """Builds and writes the "Conflicting VRF's" worksheet."""
        vrf_summaries_df = pd.DataFrame.from_dict(
            self._check_vrf_record_uncontested_vrfs(
                vrf_o_c_dictionary, vrf_index)[0], orient='index')

        vrf_summaries_df.to_excel(
            self.writer, sheet_name='Filt-Conflicting-VRF', index=True,
            header=["Conflicting VRF's"], index_label='VRF #')

    def _clear_vrf_tab(self, vrf_dictionary):
        """Builds and writes the "Clear VRF's" worksheet."""
        clear_vrf_df = pd.DataFrame(
            self._check_vrf_against_entire_db(vrf_dictionary))

        clear_vrf_df.to_excel(
            self.writer, sheet_name='Clear-VRF', index=False,
            header=["Clear VRF's"])

    def summary_and_un_categorized_sheet_processing(self, temp_df):
        """
        This method takes a copy of the full dataframe.  Processes it and
        returns the mashed data for writing the Summary and Uncategorized
        Sheet.

        """

        # Building out dataset for summary and uncategorized processing.
        temp_df = temp_df.loc[
            (temp_df['/Cidr'] != 32) &
            (temp_df['network'] != '100.88.0.0/29') &
            (temp_df['network'] != '100.64.0.0/29') &
            (temp_df['network_view'] != 'Public-IP') &
            (temp_df['network_view'] != 'CDSTEST') &
            (temp_df['network_view'] != 'IPR-HMB')]
        temp_df = temp_df[~temp_df['/Cidr'].isin(
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])]
        temp_df = temp_df[
            ~temp_df['extattrs_IPR Designation_value'].str.contains(
                'leaf', na=False)]
        temp_df = temp_df[
            ~temp_df['extattrs_IPR Designation_value'].str.contains(
                'retired', na=False)]
        temp_df = temp_df[
            ~temp_df['extattrs_IPR Designation_value'].str.contains(
                'dup', na=False)]
        temp_df = temp_df[
            ~temp_df['extattrs_IPR Designation_value'].str.contains(
                'ignore', na=False)]
        temp_df = temp_df[
            ~temp_df['extattrs_IPR Designation_value'].str.contains(
                'divest', na=False)]
        temp_df = temp_df[
            ~temp_df['extattrs_IPR Designation_value'].str.contains(
                'drop reserve', na=False)]
        temp_df = temp_df[
            ~temp_df['extattrs_IPR Designation_value'].str.contains(
                'parent', na=False)]
        temp_df = temp_df[
            ~temp_df['extattrs_IPR Designation_value'].str.contains(
                'decom', na=False)]

        # Convert the dataframe to a dictionary with the index as keys.
        temp_dict = temp_df.to_dict('index')

        # Builds dictionaries for the data to be stored in.
        temp_summary_dict = {}
        temp_uncategorized_dict = {}

        """
        Builds the two dictionaries based on private or cgn matching 
        requirements.  If a subnet is is neither a private or cgn ip address
        it is considered un-categorized.

        An extension was created for the ipaddr module located in the Builder
        directory.  Needed to do this in order to create a carrier grade nat
        filter.
        """
        for key in temp_dict.keys():
            if IPv4Network(temp_dict[key]['network']).is_private or \
                    Cgn.is_cgn(IPv4Network(temp_dict[key]['network'])):
                temp_summary_dict.update({key: temp_dict[key]})
            else:
                temp_uncategorized_dict.update({key: temp_dict[key]})

        # Build dataframes from the newly created dictionaries.
        summary_df = pd.DataFrame.from_dict(temp_summary_dict, orient='index')
        uncategorized_df = pd.DataFrame.from_dict(
            temp_uncategorized_dict, orient='index')

        # Dataframe cleanup prior to conflict and overlap check.
        header_dict = self.env_cls.header_row_dict()
        summary_df.rename(columns=header_dict, inplace=True)
        summary_df = summary_df.reset_index()
        del summary_df['index']
        summary_df['Index'] = summary_df.index + 10001

        # Overlap and Conflict Check against the master_df dataframe.
        summary_overlaps, summary_conflicts = \
            self.summary_conflict_overlap_check(summary_df)

        # Updates the summary dataframe with the overlap and conflict data.
        self.summary_update_df_conflict_overlap_data(
            summary_overlaps,
            summary_conflicts,
            summary_df)

        return summary_df, uncategorized_df

    def panda_processing_of_interim_data(self):
        """Main Processing method."""

        # Builds a dataframe from interim dataset with the following columns.
        interim_data = self.reader_cls.read_from_pkl(
            self.dir_cls.interim_dir(),
            self.filename_cls.ipam_dump_interim_panda())
        processing_data = interim_data[
            ['network', 'extattrs_Region_List_value', 'extattrs_Country_value',
             'extattrs_City_value', 'extattrs_Address_value',
             'extattrs_Site_value', 'extattrs_Datacenter_value',
             'extattrs_Division_value', 'extattrs_Requester Email_value',
             'extattrs_Agency_value', 'extattrs_VLAN Description_value',
             'comment', 'extattrs_Interface Name_value', 'net_type',
             'network_view', 'extattrs_IPR Designation_value', 'Oc-1', 'Oc-2',
             'Oc-3', 'Oc-4', '/Cidr'
             ]
        ].copy()

        # Updates dataframe with a Disposition column.
        processing_data.insert(loc=0, column='Disposition', value='')



        # Sends dataframe for summary and uncategorized tab processing.
        summary_df, un_categorized_df = \
            self.summary_and_un_categorized_sheet_processing(
                processing_data)

        # Writes out the Summary tab.
        summary_df.to_excel(self.writer, sheet_name='Summary', index=False)
        self.writer_cls.write_to_pkl(self.dir_cls.raw_dir(),
                                     self.filename_cls.master_df_filename(),
                                     summary_df)

        # Writes out the Full-Dataset tab.
        processing_data.to_excel(self.writer, sheet_name='Full-Dataset',
                                 index=False,
                                 header=self.env_cls.header_row_list())

        # Pickles the full dataset.
        self.writer_cls.write_to_pkl(self.dir_cls.raw_dir(),
                                     self.filename_cls.
                                     full_dataset_df_filename(),
                                     processing_data)

        # A nested list of attributes used for spreadsheet tab creation.
        processing_data_worksheets = [
            ['leaf', 'extattrs_IPR Designation_value', 'Filt-Leaf', False],
            ['dup', 'extattrs_IPR Designation_value', 'Filt-Dup', False],
            ['ignore', 'extattrs_IPR Designation_value', 'Filt-Ignore', False],
            ['divest', 'extattrs_IPR Designation_value', 'Filt-Divest', False],
            ['drop reserve', 'extattrs_IPR Designation_value',
             'Filt-Drop Reserve', False],
            ['parent', 'extattrs_IPR Designation_value',
             'Filt-OMC-IT-Parent Subnet', False],
            [[32], '/Cidr', 'Filt-Cidr-32', False],
            [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
             '/Cidr', 'Filt-Large-Subnets', False],
            ['100.88.0.0/29', 'network', 'Filt-100.88-Cidr-29', False],
            ['100.64.0.0/29', 'network', 'Filt-100.64-Cidr-29', False],
            ['100.64.0.0/29', 'network', 'Filt-100.64-Cidr-29', False],
            ['Public-IP', 'network_view', 'Filt-Public-IP-View', False],
            ['retired', 'extattrs_IPR Designation_value', 'Filt-Retired',
             False]
        ]

        # IPR Designation Filters Sheets
        for processing in processing_data_worksheets:
            if isinstance(processing[0], str):
                processing_data[processing_data[
                    processing[1]].str.contains(processing[0], na=False)]. \
                    to_excel(self.writer,
                             sheet_name=processing[2],
                             index=processing[3],
                             header=self.env_cls.header_row_list())
            if isinstance(processing[0], (int, list)):
                processing_data[processing_data[
                    processing[1]].isin(processing[0])]. \
                    to_excel(self.writer,
                             sheet_name=processing[2],
                             index=processing[3],
                             header=self.env_cls.header_row_list())

        # Uncategorized Sheet
        un_categorized_df.to_excel(
            self.writer, sheet_name='Filt-Uncategorized', index=False,
            header=self.env_cls.header_row_list())

        # Build dataset for _clear_vrf and _vrf_summaries_processing
        vrf_idx, vrf_dict, vrf_o_c_dict = \
            self._compiling_data(summary_df.values.tolist())

        self._clear_vrf_tab(vrf_dict)
        self._vrf_summaries_processing_tab(vrf_idx, vrf_o_c_dict)
        self._build_free_space_tab(summary_df['IPv4 Subnet'].unique())
        self._tweak_and_save_workbook()
