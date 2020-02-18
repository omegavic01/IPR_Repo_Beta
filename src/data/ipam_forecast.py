#!/usr/bin/python
import netaddr
import pandas as pd
from openpyxl import Workbook
from ipam_processed_processing import IpamDataProcessed
from builder import Writer


class IpamForecastProcessing(IpamDataProcessed):
    """Class built for IPR project to build out a forecast report."""
    def __init__(self):
        IpamDataProcessed.__init__(self)
        # Build Free IP Space Dictionary keyed by region.
        self.regional_free_space_dataset = \
            self.get_free_space_dataset(
                self.convert_df_to_nested_array(
                    self.get_free_space_df()
                )
            )

    @staticmethod
    def get_re_ip_df(master_df):
        """Method that builds a df filtered by the IPR D column by re-ip."""
        temp_df = master_df[master_df['IPR D'].str.contains(
            're-ip', na=False)]
        if not temp_df.empty:
            return temp_df
        else:
            return ''

    @staticmethod
    def get_followup_ip_df(master_df):
        """Method that builds a df filtered by the IPR D column by re-ip."""
        temp_df = master_df[master_df['IPR D'].str.contains(
            'followup', na=False)]
        if not temp_df.empty:
            return temp_df
        else:
            return ''

    @staticmethod
    def convert_df_to_nested_array(dataset):
        return dataset.values.tolist()

    @staticmethod
    def get_subnet_ratio(conflict_cidr):
        subnet_ratio = {16: 19, 17: 20, 18: 20, 19: 21, 20: 21,
                        21: 21, 22: 22, 23: 23, 24: 24, 25: 24}
        if conflict_cidr in subnet_ratio:
            return subnet_ratio[conflict_cidr]
        else:
            return 'Out of Range.'

    def get_free_space_df(self):
        return self.reader_cls.read_from_pkl(
            self.dir_cls.raw_dir(),
            self.filename_cls.free_space_df_filename())

    def get_free_space_dataset(self, free_space_dataset):
        # Logic for the free space initial compilation.
        free_apac_subnets = []
        free_emea_subnets = []
        free_latam_subnets = []
        free_na_subnets = []
        apac_subnet = netaddr.IPNetwork(self.env_cls.apac_subnet())
        emea_subnet = netaddr.IPNetwork(self.env_cls.emea_subnet())
        latam_subnet = netaddr.IPNetwork(self.env_cls.latam_subnet())
        na_subnet = netaddr.IPNetwork(self.env_cls.na_subnet())
        region_subnet_list = [apac_subnet, emea_subnet, latam_subnet,
                              na_subnet]
        free_region_subnet_list = [free_apac_subnets,
                                   free_emea_subnets,
                                   free_latam_subnets,
                                   free_na_subnets]
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

    def get_master_df(self):
        return self.reader_cls.read_from_pkl(
            self.dir_cls.raw_dir(),
            self.filename_cls.master_df_filename())

    def get_master_df_wo_re_ip_filename(self):
        return self.filename_cls.master_df_wo_re_ip_filename()

    def generate_new_df_from_filtered_df(
            self,
            source_df,
            pull_data_df,
            file_name):
        """
        Takes a subset of a df and returns the df with the subset removed.
        """
        # Concat's both DF's then drop's all duplicates.
        new_df = \
            pd.concat([source_df, pull_data_df]).drop_duplicates(keep=False)
        # Checks number of columns and then trims uneeded columns.
        if len(new_df.columns) > 22:
            new_df.drop(new_df.columns[22:], axis=1, inplace=True)
        new_df.reset_index(inplace=True)
        new_df.drop(['index'], axis=1, inplace=True)
        self.writer_cls.write_to_pkl(
            self.dir_cls.raw_dir(),
            file_name,
            new_df
        )
        return new_df

    def get_next_subnet(self, region):
        return self.regional_free_space_dataset[region][1][0][0]

    def pop_get_next_subnet(self, region):
        self.regional_free_space_dataset[region][1].pop(0)

    def update_regional_free_space_dataset_list(self, updated_list, region):
        self.regional_free_space_dataset[region][2] = updated_list

    def cidr_merge_inuse_subnets(self, free_space_subnetted_list):
        return netaddr.cidr_merge(free_space_subnetted_list)

    def region_subnets_in_use_dont_cover_needed_range(self, region):
        self.regional_free_space_dataset[region][2].append(
            self.get_next_subnet(region))
        self.pop_get_next_subnet(region)

    def return_active_region_subnets_in_use(self, region):
        if len(self.regional_free_space_dataset[region]) < 3:
            self.regional_free_space_dataset[region].extend(
                [[self.get_next_subnet(region)]])
            self.pop_get_next_subnet(region)
            return self.regional_free_space_dataset[region][2]
        if len(self.regional_free_space_dataset[region]) == 3 and \
                self.regional_free_space_dataset[region][2]:
            return self.regional_free_space_dataset[region][2]
        if len(self.regional_free_space_dataset[region]) == 3:
            self.regional_free_space_dataset[region][2] = [
                self.get_next_subnet(region)]
            self.pop_get_next_subnet(region)
            return self.regional_free_space_dataset[region][2]

    def get_new_subnet(self, new_cidr, region):
        in_use_subnets = self.return_active_region_subnets_in_use(region)
        if len(in_use_subnets) == 1:
            temp_subnetted_list = list(
                netaddr.IPNetwork(in_use_subnets[0]).subnet(new_cidr))
            if not temp_subnetted_list:
                self.region_subnets_in_use_dont_cover_needed_range(region)
                return 'Re-Run'
            returning_subnet = temp_subnetted_list[0]
            new_in_use_subnet_list = \
                self.cidr_merge_inuse_subnets(temp_subnetted_list[1:])
            self.update_regional_free_space_dataset_list(
                new_in_use_subnet_list, region)
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
                            self.cidr_merge_inuse_subnets(
                                in_use_subnets)
                        self.update_regional_free_space_dataset_list(
                            new_in_use_subnet_list, region)
                        return temp_subnetted_list[0]
                    elif len(temp_subnetted_list) > 1:
                        returning_subnet = temp_subnetted_list.pop(
                            0)
                        in_use_subnets.pop(enum)
                        new_in_use_subnet_list = \
                            temp_subnetted_list + in_use_subnets
                        self.update_regional_free_space_dataset_list(
                            new_in_use_subnet_list, region)
                        return returning_subnet
            # If a no good subnet was not identified.
            self.region_subnets_in_use_dont_cover_needed_range()
            return 'Re-Run'

    def clean_conflict(self, dirty_cidr, dirty_cidr_region):
        new_cidr = self.get_subnet_ratio(dirty_cidr)
        if not isinstance(new_cidr, int):
            return False

        new_subnet = self.get_new_subnet(
            new_cidr,
            dirty_cidr_region).__str__()

        if new_subnet == 'Re-Run':
            new_subnet = self.get_new_subnet(
                new_cidr,
                dirty_cidr_region).__str__()

        return new_subnet

    def forecast_core(self, new_ip_needed_df):
        old_data = []
        new_data = []
        errored_data = []
        ipr_index = list(new_ip_needed_df).index('IPR D')
        comment_index = list(new_ip_needed_df).index('Comment')
        region_index = list(new_ip_needed_df).index('RGN')
        cidr_index = list(new_ip_needed_df).index('/Cidr')
        disposition_index = list(new_ip_needed_df).index('Disposition')
        dataset_listed = self.convert_df_to_nested_array(
            new_ip_needed_df)
        for dirty_subnet in dataset_listed:
            if 'nan' == dirty_subnet[region_index].__repr__():
                errored_data.append(dirty_subnet)
                continue
            new_subnet_record = self.clean_conflict(
                dirty_subnet[cidr_index],
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
        return old_data, new_data, errored_data


# Instantiates Class
time_to_summarize = IpamForecastProcessing()
# Get's master_df
master_stuff = time_to_summarize.get_master_df()

# Pull's out IPR D: re-ip data from df.
re_ip_df = time_to_summarize.get_re_ip_df(master_stuff)
if not re_ip_df.empty:
    # Forecasts re-ip data
    re_ip_old, re_ip_new, re_ip_err = \
        time_to_summarize.forecast_core(re_ip_df)
    # Removes re_ip and followup lines from master_df and
    # creates a modified master_df.
    master_stuff = time_to_summarize.generate_new_df_from_filtered_df(
        master_stuff,
        re_ip_df,
        time_to_summarize.get_master_df_wo_re_ip_filename())

# Need to capture all followup lines then generate a new df wo followup lines.

if 2 == 2:
    pass
