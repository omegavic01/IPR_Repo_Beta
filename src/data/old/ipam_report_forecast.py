"""

OLD DATA FOR REFERENCE!!

"""
from builder import EnvironmentValues, DirectoryValues, LoggingValues, DataFileNames
from builder import Writer
from builder import Reader
from ipam_apirequest_calltypes import IpamCallTypes, IpamApiRequest
import pandas as pd
from tabulate import tabulate
import functools
from collections import MutableMapping
import netaddr

# Initialize Classes
dir_cls = DirectoryValues()
env_cls = EnvironmentValues()
filename_cls = DataFileNames
reader_cls = Reader()


def _summary_forecast():
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
        free_region_subnet_list = [free_apac_subnets, free_emea_subnets,
                                   free_latam_subnets, free_na_subnets]
        for enum, region_subnet in enumerate(region_subnet_list):
            for free_space_list in free_space_dataset:
                if netaddr.IPNetwork(free_space_list[0]) in region_subnet and \
                                free_space_list[5] <= 22:
                    free_region_subnet_list[enum].append(free_space_list)
        regional_dictionary = {'EMEA': [emea_subnet, free_emea_subnets],
                               'NA': [na_subnet, free_na_subnets],
                               'APAC': [apac_subnet, free_apac_subnets],
                               'LATAM': [latam_subnet, free_latam_subnets]}
        return regional_dictionary

    def convert_df_to_nested_array(dataset):
        return dataset.values.tolist()

    def get_conflicted_data(master_dataset_df):
        conflicted_df = master_dataset_df[
            master_dataset_df['No Conflict'].str.contains('NO')]
        conflict_idx = list(conflicted_df).index('No Conflict')
        iprd_idx = list(conflicted_df).index('IPR D')
        comment_idx = list(conflicted_df).index('Comment')
        region_idx = list(conflicted_df).index('RGN')
        cidr_idx = list(conflicted_df).index('/Cidr')
        conflicted_lt = convert_df_to_nested_array(conflicted_df)
        return conflicted_lt, iprd_idx, conflict_idx, \
            region_idx, cidr_idx, comment_idx

    def get_master_df():
        return reader_cls.read_from_pkl(dir_cls.raw_dir(),
                                        filename_cls.master_df_filename())

    def get_free_space_df():
        return reader_cls.read_from_pkl(dir_cls.raw_dir(),
                                        filename_cls.free_space_df_filename())

    def get_subnet_ratio(conflict_cidr):
        subnet_ratio = {ipr_index: 19, 17: 20, 18: 20, 19: 21, 20: 21, 21: 21, 22: 22}
        if conflict_cidr in subnet_ratio:
            return subnet_ratio[conflict_cidr]
        if 24 >= conflict_cidr > 22:
            return int(subnet_ratio[22])
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
            regional_free_space_dataset[region][2].append(get_next_subnet())
            pop_get_next_subnet()

        def return_active_region_subnets_in_use():
            if len(regional_free_space_dataset[region]) < 3:
                regional_free_space_dataset[region].extend([[get_next_subnet()]])
                pop_get_next_subnet()
                return regional_free_space_dataset[region][2]
            if len(regional_free_space_dataset[region]) == 3 and \
                    regional_free_space_dataset[region][2]:
                return regional_free_space_dataset[region][2]
            if len(regional_free_space_dataset[region]) == 3:
                regional_free_space_dataset[region][2] = [get_next_subnet()]
                pop_get_next_subnet()
                return regional_free_space_dataset[region][2]

        def new_subnet():
            in_use_subnets = return_active_region_subnets_in_use()
            if len(in_use_subnets) == 1:
                temp_subnetted_list = list(
                    netaddr.IPNetwork(in_use_subnets[0]).subnet(new_cidr))
                if not temp_subnetted_list:
                    region_subnets_in_use_dont_cover_needed_range()
                    return 'Re-Run'
                returning_subnet = temp_subnetted_list[0]
                new_in_use_subnet_list = \
                    cidr_merge_inuse_subnets(temp_subnetted_list[1:])
                update_regional_free_space_dataset_list(new_in_use_subnet_list)
                return returning_subnet
            else:
                for enum, subnet in enumerate(in_use_subnets):
                    if list(netaddr.IPNetwork(subnet).subnet(new_cidr)):
                        temp_subnetted_list = list(
                            netaddr.IPNetwork(subnet).subnet(new_cidr))
                        if len(temp_subnetted_list) == 1:
                            in_use_subnets.pop(enum)
                            new_in_use_subnet_list = cidr_merge_inuse_subnets(
                                in_use_subnets)
                            update_regional_free_space_dataset_list(
                                new_in_use_subnet_list)
                            return temp_subnetted_list[0]
                        elif len(temp_subnetted_list) > 1:
                            returning_subnet = temp_subnetted_list.pop(0)
                            in_use_subnets.pop(enum)
                            new_in_use_subnet_list = temp_subnetted_list + \
                                in_use_subnets
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
        new_subnet = get_new_subnet(new_cidr, dirty_cidr_region).__str__()
        if new_subnet == 'Re-Run':
            new_subnet = get_new_subnet(new_cidr, dirty_cidr_region).__str__()
        return new_subnet

    # Reads in master_df.pkl.
    master_df = get_master_df()
    # Builds the conflict dataset
    conflicted_list, ipr_index, conflict_index, \
        region_index, cidr_index, comment_index = \
        get_conflicted_data(master_df)
    # Reads in free_space_df.pkl
    regional_free_space_dataset = get_free_space_dataset(
        convert_df_to_nested_array(get_free_space_df()))
    # Update old array with new array data and build new array while at it.
    # print(regional_free_space_dataset)
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
        if new_ipr_record[ipr_index]:
            new_ipr_record[ipr_index] = \
                new_ipr_record[ipr_index] + ', followup'
        else:
            new_ipr_record[ipr_index] = 'followup'
        if dirty_subnet_for_record[ipr_index]:
            dirty_subnet_for_record[ipr_index] = \
                dirty_subnet_for_record[ipr_index] + ', assigned'
        else:
            dirty_subnet_for_record[ipr_index] = 'assigned'
        # Comment Update
        if new_ipr_record[comment_index]:
            new_ipr_record[comment_index] = \
                new_ipr_record[comment_index] + \
                ' | replacing ' + dirty_subnet[1]
        else:
            new_ipr_record[comment_index] = \
                'replacing ' + dirty_subnet[1]
        if dirty_subnet_for_record[comment_index]:
            dirty_subnet_for_record[comment_index] = \
                dirty_subnet_for_record[comment_index] + \
                ' | replaced by ' + new_subnet_record.__str__()
        else:
            dirty_subnet_for_record[comment_index] = \
                'replaced by ' + new_subnet_record.__str__()
        old_data.append(dirty_subnet_for_record)
        new_data.append(new_ipr_record)
    print('Your Mom')


_summary_forecast()
