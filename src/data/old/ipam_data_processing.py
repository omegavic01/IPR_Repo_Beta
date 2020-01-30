#!/usr/bin/python
import time
from collections import OrderedDict
from ipaddr import IPv4Network
from netaddr import IPNetwork
import netaddr
import pandas as pd
from openpyxl import Workbook
import os
from builder import Cgn
from ipam_base_processing import BaseIpamProcessing


class IpamDataProcessed(BaseIpamProcessing):
    """Processing phase of the IPAM data."""

    def run_ipam_processing(self,
                            interim_data,
                            summary=True,
                            full_dataset_ipr_d=None):
        """
        Method that runs through all of the interim processing steps.  Then
        writes the panda dataframe to excel and to a pickle file.

        """
        self._logger.info('Starting the final step in data processing.')
        start = time.perf_counter()
        self.panda_processing_of_interim_data(interim_data,
                                              summary,
                                              full_dataset_ipr_d)
        end = time.perf_counter()
        time_taken = end - start
        self._logger.info('Final processed the data in %2f seconds',
                          time_taken)
        self._logger.info('Finished the final step in data processing.')

    @staticmethod
    def _tweak_and_save_workbook(write, summary):
        workbook = write.book
        worksheet_summary = write.sheets['Summary']
        left = workbook.add_format({'align': 'left'})
        worksheet_summary.set_column('W:Y', None, left)
        if summary:
            worksheet_summary_forecast = write.sheets['Summary Forecast']
            worksheet_summary_forecast.set_column('W:Y', None, left)
        write.save()

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

        """Builds a list of unique cidr's while maintaining order."""
        list_cidr_set = list(OrderedDict.fromkeys(
            summary_df['IPv4 Subnet'].to_list()
                                                  )
                             )

        """
        Builds overlap and conflict dictionaries for this functions data 
        storage.
        
        """
        dict_overlap = {}
        dict_conflict = {}

        """Unique list of cidr values become the keys to the dictionaries."""
        for i in list_cidr_set:
            dict_overlap[i] = []
            dict_conflict[i] = []

        """
        Updates dictionaries if the item value is found in the conflict 
        dictionary.
        
        """
        for item in cidr_index_zip:
            if item[0] in dict_conflict:  # Conflict check
                dict_conflict[item[0]].append(item[1])

        """
        Logic for the overlap check.  Sped up process by filtering on first
        and second octets.
        
        """
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
                    print(item) # Need to update this statement to send to log.

        """Returns the dictionaries with offending indexes in a list"""
        return dict_overlap, dict_conflict

    @staticmethod
    def summary_update_df_conflict_overlap_data(overlaps,
                                                conflicts,
                                                summary_df):
        """
        Function to build out the summary dataframe with the identified
        information gathered from the _conflict_overlap_check function call.

        """

        """Adds new columns to the summary dataframe."""
        summary_df['Conflict Subnet Overlap - Index No.'] = ''
        summary_df['Conflict Subnet - Index No.'] = ''
        summary_df['No Overlap'] = ''
        summary_df['No Conflict'] = ''
        summary_df['Conflict Subnet Overlap - Count'] = ''
        summary_df['Conflict Subnet - Count'] = ''

        """Loops through to update new columns."""
        for row in summary_df.index.values:
            """Overlap Updates."""
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
            """Conflict Updates."""
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

    def summary_and_un_categorized_sheet_processing(self, temp_df):
        """
        This method takes a copy of the full dataframe.  Processes it and
        returns the mashed data for writing the Summary and Uncategorized
        Sheet.

        """

        """
        Here I am filtering out uneeded data that is not to be included in 
        the summary and uncategoried tabs.
        
        """
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

        """Convert the dataframe to a dictionary with the index as keys."""
        temp_dict = temp_df.to_dict('index')

        """Builds dictionaries for the data to be stored in."""
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

        """Build dataframes from the newly created dictionaries."""
        summary_df = pd.DataFrame.from_dict(temp_summary_dict, orient='index')
        uncategorized_df = pd.DataFrame.from_dict(
            temp_uncategorized_dict, orient='index')

        """Dataframe cleanup prior to conflict and overlap check."""
        header_dict = self.env_cls.header_row_dict()
        summary_df.rename(columns=header_dict, inplace=True)
        summary_df = summary_df.reset_index()
        del summary_df['index']
        summary_df['Index'] = summary_df.index + 10001

        """Overlap and Conflict Check against the master_df dataframe."""
        summary_overlaps, summary_conflicts = \
            self.summary_conflict_overlap_check(summary_df)

        """Updates the summary dataframe with the overlap and conflict data."""
        self.summary_update_df_conflict_overlap_data(
            summary_overlaps,
            summary_conflicts,
            summary_df)

        return summary_df, uncategorized_df

    def panda_processing_of_interim_data(self,
                                         interim_data,
                                         summary,
                                         full_dataset_ipr_d):
        """Main Processing method."""

        """Pulls in interim data file for processing."""
        workbook_file = self.dir_cls.processed_dir() + '\\' + \
            self.filename_cls.processed_filename()

        """Builds a dataframe with the following columns."""
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

        """Updates dataframe with a Disposition column."""
        processing_data.insert(loc=0, column='Disposition', value='')

        """Builds pandas writer object."""
        writer = pd.ExcelWriter(workbook_file, engine='xlsxwriter')

        """Sends dataframe for summary and uncategorized tab processing."""
        summary_df, un_categorized_df = \
            self.summary_and_un_categorized_sheet_processing(
                processing_data)

        """Writes out the Summary tab."""
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        self.writer_cls.write_to_pkl(self.dir_cls.raw_dir(),
                                     self.filename_cls.master_df_filename(),
                                     summary_df)

        """Writes out the Full-Dataset tab."""
        processing_data.to_excel(writer, sheet_name='Full-Dataset',
                                 index=False,
                                 header=self.env_cls.header_row_list())

        """Pickles the full dataset."""
        self.writer_cls.write_to_pkl(self.dir_cls.raw_dir(),
                                     self.filename_cls.
                                     full_dataset_df_filename(),
                                     processing_data)

        """A nested list of attributes used for spreadsheet tab creation."""
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
                    processing[1]].str.contains(processing[0], na=False)].\
                    to_excel(writer,
                             sheet_name=processing[2],
                             index=processing[3],
                             header=self.env_cls.header_row_list())
            if isinstance(processing[0], (int, list)):
                processing_data[processing_data[
                    processing[1]].isin(processing[0])]. \
                    to_excel(writer,
                             sheet_name=processing[2],
                             index=processing[3],
                             header=self.env_cls.header_row_list())

        # Uncategorized Sheet
        un_categorized_df.to_excel(
            writer, sheet_name='Filt-Uncategorized', index=False,
            header=self.env_cls.header_row_list())

        # Build dataset for _clear_vrf and _vrf_summaries_processing
        vrf_idx, vrf_dict, vrf_o_c_dict = \
            self._compiling_data(summary_df.values.tolist())

        def _clear_vrf(vrf_dictionary):
            """Builds and writes the "Clear VRF's" worksheet."""
            clear_vrf_df = pd.DataFrame(
                self._check_vrf_against_entire_db(vrf_dictionary))

            clear_vrf_df.to_excel(
                writer, sheet_name='Clear-VRF', index=False,
                header=["Clear VRF's"])

        def _vrf_summaries_processing(vrf_index, vrf_o_c_dictionary):
            """Builds and writes the "Conflicting VRF's" worksheet."""
            vrf_summaries_df = pd.DataFrame.from_dict(
                self._check_vrf_record_uncontested_vrfs(
                    vrf_o_c_dictionary, vrf_index)[0], orient='index')

            vrf_summaries_df.to_excel(
                writer, sheet_name='Filt-Conflicting-VRF', index=True,
                header=["Conflicting VRF's"], index_label='VRF #')

        def _build_free_space_tab(main_dataset):

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
            free_space_small_df = main_dataset['IPv4 Subnet'].unique()
            ipnetwork_addr = []
            for addr in free_space_small_df:
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
            for i in merged_free_space:
                if i.is_private():
                    private_free_space.append(i)
            # Convert to string repr
            free_space_list_of_strings = []
            for i in private_free_space:
                ip = i.__str__()
                split_subnet = ip.split('.')
                split_cidr = split_subnet[3].split('/')
                temp_subnet_list = (
                    ip, int(split_subnet[0]), int(split_subnet[1]),
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
                writer, sheet_name='Summary_Free_Space', index=False)
            self.writer_cls.write_to_pkl(
                self.dir_cls.raw_dir(),
                self.filename_cls.free_space_df_filename(),
                free_space_df)

        def non_confliction_data_processing(new_ip_data,
                                            no_conflict_df,
                                            sheetname):
            labels = no_conflict_df.columns.values.tolist()
            new_ip_data_df = pd.DataFrame(new_ip_data, columns=labels)
            cleaned_new_ip_data_df = new_ip_data_df.drop(
                new_ip_data_df.columns[17:],
                axis=1)
            cleaned_new_ip_data_df.to_excel(writer,
                                            sheet_name=sheetname,
                                            index=False)
            forecast_ip_df = pd.concat([new_ip_data_df, no_conflict_df],
                                       ignore_index=True)
            forecast_ip_df = forecast_ip_df.drop(
                forecast_ip_df.columns[17:],
                axis=1)
            forecast_ip_df = self.split_out_network(
                forecast_ip_df,
                'IPv4 Subnet')
            forecast_ip_df = self.sort_df_by_oct_list(forecast_ip_df)
            forecast_ip_df = forecast_ip_df.reset_index()
            del forecast_ip_df['index']
            forecast_ip_df['Index'] = forecast_ip_df.index + 10001
            forecast_overlaps, forecast_conflicts = \
                self._conflict_overlap_check(forecast_ip_df)
            self._update_df_conflict_overlap_data(forecast_overlaps,
                                                  forecast_conflicts,
                                                  forecast_ip_df)
            forecast_ip_df.to_pickle(self.dir_cls.raw_dir() + '/' +
                                     self.filename_cls.
                                     conflict_free_df_filename())
            #forecast_ip_df.to_excel(writer, sheet_name='Summary Forecast',
            #                        index=False)
            return forecast_ip_df

        def _confliction_data_processing(old_ip_data, no_conflict_df):
            labels = no_conflict_df.columns.values.tolist()
            old_ip_data_df = pd.DataFrame(old_ip_data, columns=labels)
            old_ip_data_df.to_excel(writer, sheet_name=
                                    'Conflict Forecast Updates',
                                    index=False)

        def _overlap_data_processing(old_ip_data, no_conflict_df):
            labels = no_conflict_df.columns.values.tolist()
            old_ip_data_df = pd.DataFrame(old_ip_data, columns=labels)
            old_ip_data_df.to_excel(writer, sheet_name=
                                    'Overlap Forecast Updates',
                                    index=False)

        def _summary_forecast(conflict, overlap, ipr_d):

            def get_free_space_dataset(free_space_dataset):
                # Logic for the free space initial compilation.
                free_apac_subnets = []
                free_emea_subnets = []
                free_latam_subnets = []
                free_na_subnets = []
                apac_subnet = netaddr.IPNetwork('10.224.0.0/12')
                emea_subnet = netaddr.IPNetwork('10.128.0.0/11')
                latam_subnet = netaddr.IPNetwork('10.240.0.0/13')
                na_subnet = netaddr.IPNetwork('10.192.0.0/11')
                region_subnet_list = [apac_subnet, emea_subnet, latam_subnet,
                                      na_subnet]
                free_region_subnet_list = [free_apac_subnets,
                                           free_emea_subnets,
                                           free_latam_subnets, free_na_subnets]
                for enum, region_subnet in enumerate(region_subnet_list):
                    for free_space_list in free_space_dataset:
                        if netaddr.IPNetwork(
                                free_space_list[0]) in region_subnet and \
                                        free_space_list[5] <= 22:
                            free_region_subnet_list[enum].append(
                                free_space_list)
                regional_dictionary = {
                    'EMEA': [emea_subnet, free_emea_subnets],
                    'NA': [na_subnet, free_na_subnets],
                    'APAC': [apac_subnet, free_apac_subnets],
                    'LATAM': [latam_subnet, free_latam_subnets]}
                return regional_dictionary

            def convert_df_to_nested_array(dataset):
                return dataset.values.tolist()

            def get_conflicted_data(master_dataset_df):
                conflicted_df = master_dataset_df[
                    (master_dataset_df['No Conflict'] == 'NO') &
                    (~master_dataset_df['DDI View'].
                     str.contains('HUB', na=False)) &
                    (~master_dataset_df['DDI View'].
                     str.contains('00555', na=False)) &
                    (~master_dataset_df['DDI View'].
                     str.contains('00324', na=False)) &
                    (master_dataset_df['Oc-1'] != 100)]
                non_conflict_df = master_dataset_df.drop(conflicted_df.index)
                conflict_idx = list(conflicted_df).index('No Conflict')
                iprd_idx = list(conflicted_df).index('IPR D')
                comment_idx = list(conflicted_df).index('Comment')
                region_idx = list(conflicted_df).index('RGN')
                cidr_idx = list(conflicted_df).index('/Cidr')
                disposition_idx = list(conflicted_df).index('Disposition')
                conflicted_lt = convert_df_to_nested_array(conflicted_df)
                return conflicted_lt, iprd_idx, conflict_idx, \
                    region_idx, cidr_idx, comment_idx, non_conflict_df, \
                    disposition_idx

            def get_overlapping_data(conflict_free_dataset_df, overlap_dict):
                labels = conflict_free_dataset_df.columns.values.tolist()
                overlapping_subnet =[]
                clean_data = []
                overlap_idx = list(conflict_free_dataset_df).\
                    index('Index')
                conflict_free_lt = convert_df_to_nested_array(
                    conflict_free_dataset_df)
                for subnet_row in conflict_free_lt:
                    if subnet_row[overlap_idx] in overlap_dict:
                        overlapping_subnet.append(subnet_row)
                    else:
                        clean_data.append(subnet_row)
                iprd_idx = list(conflict_free_dataset_df).index('IPR D')
                comment_idx = list(conflict_free_dataset_df).index('Comment')
                region_idx = list(conflict_free_dataset_df).index('RGN')
                cidr_idx = list(conflict_free_dataset_df).index('/Cidr')
                disposition_idx = list(conflict_free_dataset_df).index('Disposition')
                clean_data_df = pd.DataFrame(clean_data, columns=labels)
                return overlapping_subnet, iprd_idx, \
                       region_idx, cidr_idx, comment_idx, clean_data_df, \
                       disposition_idx

            def index_count_list_overlap_conflict(master_df):
                master_listed = master_df.values.tolist()
                index_count_list = []
                for idx_row in master_listed:
                    count = 0
                    for overlap in master_listed:
                        if str(idx_row[22]) in str(overlap[23]) or str(
                                idx_row[22]) in str(overlap[24]):
                            count += 1
                    if count:
                        index_count_list.append(idx_row[22])
                #index_count_list.sort(key=lambda x: x[1], reverse=True)
                return index_count_list

            def get_forecast_master_df():
                return self.reader_cls.read_from_pkl(
                    self.dir_cls.raw_dir(),
                    self.filename_cls.conflict_free_df_filename())

            def get_full_dataset_df():
                return self.reader_cls.read_from_pkl(
                    self.dir_cls.raw_dir(),
                    self.filename_cls.full_dataset_df_filename())

            def get_master_df():
                return self.reader_cls.read_from_pkl(
                    self.dir_cls.raw_dir(),
                    self.filename_cls.master_df_filename())

            def get_free_space_df():
                return self.reader_cls.read_from_pkl(
                    self.dir_cls.raw_dir(),
                    self.filename_cls.free_space_df_filename())

            def get_subnet_ratio(conflict_cidr):
                subnet_ratio = {ipr_index: 19, 17: 20, 18: 20, 19: 21, 20: 21,
                                21: 21, 22: 22, 23: 23, 24: 24}
                if conflict_cidr in subnet_ratio:
                    return subnet_ratio[conflict_cidr]
                else:
                    return 'Out of Range.'

            def get_new_subnet(new_cidr, region):

                def get_next_subnet():
                    return regional_free_space_dataset[region][1][0][0]

                def pop_get_next_subnet():
                    regional_free_space_dataset[region][1].pop(0)

                def update_regional_free_space_dataset_list(updated_list):
                    regional_free_space_dataset[region][2] = updated_list

                def cidr_merge_inuse_subnets(free_space_subnetted_list):
                    return netaddr.cidr_merge(free_space_subnetted_list)

                def region_subnets_in_use_dont_cover_needed_range():
                    regional_free_space_dataset[region][2].append(
                        get_next_subnet())
                    pop_get_next_subnet()

                def return_active_region_subnets_in_use():
                    if len(regional_free_space_dataset[region]) < 3:
                        regional_free_space_dataset[region].extend(
                            [[get_next_subnet()]])
                        pop_get_next_subnet()
                        return regional_free_space_dataset[region][2]
                    if len(regional_free_space_dataset[region]) == 3 and \
                            regional_free_space_dataset[region][2]:
                        return regional_free_space_dataset[region][2]
                    if len(regional_free_space_dataset[region]) == 3:
                        regional_free_space_dataset[region][2] = [
                            get_next_subnet()]
                        pop_get_next_subnet()
                        return regional_free_space_dataset[region][2]

                def new_subnet():
                    in_use_subnets = return_active_region_subnets_in_use()
                    if len(in_use_subnets) == 1:
                        temp_subnetted_list = list(
                            netaddr.IPNetwork(in_use_subnets[0]).subnet(
                                new_cidr))
                        if not temp_subnetted_list:
                            region_subnets_in_use_dont_cover_needed_range()
                            return 'Re-Run'
                        returning_subnet = temp_subnetted_list[0]
                        new_in_use_subnet_list = \
                            cidr_merge_inuse_subnets(temp_subnetted_list[1:])
                        update_regional_free_space_dataset_list(
                            new_in_use_subnet_list)
                        return returning_subnet
                    else:
                        for enum, subnet in enumerate(in_use_subnets):
                            if list(netaddr.IPNetwork(subnet).subnet(
                                    new_cidr)):
                                temp_subnetted_list = list(
                                    netaddr.IPNetwork(subnet).subnet(new_cidr))
                                if len(temp_subnetted_list) == 1:
                                    in_use_subnets.pop(enum)
                                    new_in_use_subnet_list = \
                                        cidr_merge_inuse_subnets(
                                            in_use_subnets)
                                    update_regional_free_space_dataset_list(
                                        new_in_use_subnet_list)
                                    return temp_subnetted_list[0]
                                elif len(temp_subnetted_list) > 1:
                                    returning_subnet = temp_subnetted_list.pop(
                                        0)
                                    in_use_subnets.pop(enum)
                                    new_in_use_subnet_list = \
                                        temp_subnetted_list + in_use_subnets
                                    update_regional_free_space_dataset_list(
                                        new_in_use_subnet_list)
                                    return returning_subnet
                        # If a no good subnet was not identified.
                        region_subnets_in_use_dont_cover_needed_range()
                        return 'Re-Run'

                return new_subnet()

            def clean_conflict(dirty_cidr, dirty_cidr_region):
                new_cidr = get_subnet_ratio(dirty_cidr)
                if not isinstance(new_cidr, int):
                    return False
                new_subnet = get_new_subnet(new_cidr,
                                            dirty_cidr_region).__str__()
                if new_subnet == 'Re-Run':
                    new_subnet = get_new_subnet(new_cidr,
                                                dirty_cidr_region).__str__()
                return new_subnet

            # Builds the conflict dataset
            if conflict:
                # Reads in master_df.pkl.
                master_ip_df = get_master_df()
                conflicted_list, ipr_index, conflict_index, region_index, \
                    cidr_index, comment_index, cleaned_data, \
                    disposition_index = \
                    get_conflicted_data(master_ip_df)
                # Reads in free_space_df.pkl
                regional_free_space_dataset = get_free_space_dataset(
                    convert_df_to_nested_array(get_free_space_df()))
            # Builds Overlap dataset
            if overlap:
                forecast_master_ip_df = get_forecast_master_df()
                overlapping = index_count_list_overlap_conflict(
                    forecast_master_ip_df)
                conflicted_list, ipr_index, region_index, \
                cidr_index, comment_index, cleaned_data, \
                disposition_index = get_overlapping_data(
                    forecast_master_ip_df, overlapping)
                regional_free_space_dataset = get_free_space_dataset(
                    convert_df_to_nested_array(get_free_space_df()))

            if full_dataset_ipr_d:
                conflicted_list = []
                cleaned_data = []
                master_ip_df = get_master_df()
                full_dataset_df = get_full_dataset_df()
                ipr_index = list(master_ip_df).index('IPR D')
                comment_index = list(master_ip_df).index('Comment')
                region_index = list(master_ip_df).index('RGN')
                cidr_index = list(master_ip_df).index('/Cidr')
                disposition_index = list(master_ip_df).index('Disposition')
                full_dataset_listed = convert_df_to_nested_array(
                    full_dataset_df)
                seperator = (', ')
                for full_dataset_list in full_dataset_listed:
                    if isinstance(full_dataset_list[ipr_index], float):
                        continue
                    if full_dataset_ipr_d in full_dataset_list[ipr_index]:
                        temp_list = full_dataset_list[ipr_index].split(', ')
                        temp_list.remove(full_dataset_ipr_d)
                        full_dataset_list[ipr_index] = seperator.join(
                            temp_list)
                        conflicted_list.append(full_dataset_list)
                regional_free_space_dataset = get_free_space_dataset(
                    convert_df_to_nested_array(get_free_space_df()))

            # Update old array with new array data and build new array
            # while at it.
            old_data = []
            new_data = []
            errored_data = []
            for dirty_subnet in conflicted_list:
                if 'nan' == dirty_subnet[region_index].__repr__():
                    errored_data.append(dirty_subnet)
                    continue
                new_subnet_record = clean_conflict(dirty_subnet[cidr_index],
                                                   dirty_subnet[region_index])
                if not new_subnet_record:
                    errored_data.append(dirty_subnet)
                    continue
                # List comprehension for cleaning up pandas conversion.
                dirty_subnet_for_record = \
                    ['' if 'nan' == x.__repr__() else x for x in dirty_subnet]
                new_ipr_record = dirty_subnet_for_record[:]
                new_ipr_record[1] = new_subnet_record
                # IPR D Update
                new_ipr_record[ipr_index] = 'assigned'
                new_ipr_record[disposition_index] = 'add'
                if dirty_subnet_for_record[ipr_index] and 'followup' not in \
                        dirty_subnet_for_record[ipr_index]:
                    dirty_subnet_for_record[ipr_index] = \
                        dirty_subnet_for_record[ipr_index] + ', followup'
                else:
                    dirty_subnet_for_record[ipr_index] = 'followup'
                # Comment Update
                if new_ipr_record[comment_index]:
                    new_ipr_record[comment_index] = \
                        new_ipr_record[comment_index] + \
                        ' | replacing ' + dirty_subnet[1] + " |"
                else:
                    new_ipr_record[comment_index] = \
                        '| replacing ' + dirty_subnet[1] + " |"
                if dirty_subnet_for_record[comment_index]:
                    dirty_subnet_for_record[comment_index] = \
                        dirty_subnet_for_record[comment_index] + \
                        ' | replaced by ' + new_subnet_record.__str__() + ' |'
                else:
                    dirty_subnet_for_record[comment_index] = \
                        '| replaced by ' + new_subnet_record.__str__() + ' |'
                old_data.append(dirty_subnet_for_record)
                new_data.append(new_ipr_record)
            return old_data, new_data, cleaned_data, errored_data

        _clear_vrf(vrf_dict)
        _vrf_summaries_processing(vrf_idx, vrf_o_c_dict)
        _build_free_space_tab(summary_df)
        # Conflict Updates
        if summary:
            old_ip_data, new_ip_data, non_conflicted_ip_df, conflict_errored = \
                _summary_forecast(True, False, False)
            self.writer_cls.write_to_csv_w(
                self.dir_cls.processed_dir(),
                self.filename_cls.conflict_error_filename(),
                conflict_errored)
            non_conflicted_df = non_confliction_data_processing(
                new_ip_data, non_conflicted_ip_df, 'Conflict Add Updates')
            _confliction_data_processing(old_ip_data, non_conflicted_ip_df)
            _build_free_space_tab(non_conflicted_df)
            # Overlap Updates
            old_ip_data, new_ip_data, non_overlapping_ip_df, overlap_errored = \
                _summary_forecast(False, True, False)
            self.writer_cls.write_to_csv_w(
                self.dir_cls.processed_dir(),
                self.filename_cls.overlap_error_filename(),
                overlap_errored)
            non_conflicted_df = non_confliction_data_processing(
                new_ip_data, non_overlapping_ip_df, 'Overlap Add Updates')
            non_conflicted_df.to_excel(writer, sheet_name='Summary Forecast',
                                       index=False)
            _overlap_data_processing(old_ip_data, non_conflicted_df)
        if full_dataset_ipr_d:
            old_ip_data, new_ip_data, non_ipr_d_df, ipr_d_errored = \
                _summary_forecast(False, False, full_dataset_ipr_d)
            new_ip_data = new_ip_data + old_ip_data
            self.writer_cls.write_to_csv_w(
                self.dir_cls.processed_dir(),
                self.filename_cls.overlap_error_filename(),
                ipr_d_errored)

            def _write_output(diff_list, output_file):
                """Write Output"""
                w_b = Workbook()
                w_s = w_b.active
                w_s.title = 'IPR_Diff'
                for row_indx, stuff in enumerate(diff_list):
                    if row_indx == 0:
                        continue
                    for col_indx, item in enumerate(stuff):
                        w_s.cell(row=row_indx + 1, column=col_indx + 1,
                                 value=item)
                w_b.save(output_file)

            output_file = os.path.join(self.dir_cls.processed_dir(),
                                       'Modded Data.xlsx')

            _write_output(new_ip_data, output_file)

        self._tweak_and_save_workbook(writer, summary)

