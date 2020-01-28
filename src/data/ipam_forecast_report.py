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


class IpamForecastProcessing(BaseIpamProcessing):
    """Class built for IPR project to build out a forecast report."""
    def __init__(self):
        BaseIpamProcessing.__init__(self)

    def _summary_forecast(self, conflict, overlap, ipr_d):

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
        non_conflicted_df = _non_confliction_data_processing(
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
        non_conflicted_df = _non_confliction_data_processing(
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