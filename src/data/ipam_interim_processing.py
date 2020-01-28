#!/usr/bin/python
import time
import pandas as pd
from ipam_base_processing import BaseIpamProcessing


class IpamDataInterim(BaseIpamProcessing):
    """
    Class to read in networks and networkcontainers to then be smashed,
    mangled, and spit out into a .pickle and_or .xlsx file

    To Write to xlsx when calling the method run_ipam_interim (default=False):
        write_to_xlsx=True
    """

    def run_ipam_interim(self, write_to_xlsx=False):
        """
        Method that runs through all of the interim processing steps.  Then
        writes the panda dataframe to excel and to a pickle file.
        """
        self._logger.info('Starting the interim process for the raw data.')
        start = time.perf_counter()
        output_data = \
            self.ea_ipr_designation_processing(
                self.ea_datacenter_processing(
                    self.panda_processing_of_flattened_data(
                        self._flatten_data(
                            self.get_raw_data_networks_networkcontainers()
                        )
                    )
                )
            )

        if write_to_xlsx:
            output_data.to_excel(self.dir_cls.interim_dir() + '\\' +
                                 self.filename_cls.ipam_dump_interim_xlsx())

        output_data.to_pickle(self.dir_cls.interim_dir() + '\\' +
                              self.filename_cls.ipam_dump_interim_panda())
        self.writer_cls.write_to_pkl(
            self.dir_cls.interim_dir(),
            self.filename_cls.ipam_dump_interim_dicted(),
            output_data.to_dict())

        end = time.perf_counter()
        time_taken = end - start
        self._logger.info('Interim processed the data in %2f seconds',
                          time_taken)
        self._logger.info('Finished the interim processing step.')

    def get_raw_data_networks_networkcontainers(self):
        """
        Gets the network and networkcontainer data.  Returns the two
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
        """
        Processes the ea_datacenter column.  To be have any lists converted
        to strings and seperated by a ;.
        """
        ea_value = 'extattrs_Datacenter_value'
        dc_data = [data[ea_value].to_dict()]
        updater_dcdata = self.get_listed_values(dc_data)
        return self.put_listed_values(updater_dcdata, data, ea_value)

    def ea_ipr_designation_processing(self, data):
        """
        Processes the ea_ipr_designation column.  To convert any lists to
        strings and seperated by a ;.
        """
        ea_value = 'extattrs_IPR Designation_value'
        dc_data = [data[ea_value].to_dict()]
        updater_dcdata = self.get_listed_values(dc_data)
        return self.put_listed_values(updater_dcdata, data, ea_value)

    def panda_processing_of_flattened_data(self, raw_nets):
        """
        Turns the returned flat dict into a panda dataframe.

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
        net_flat_df = self.split_out_network(net_flat_df, 'network')

        # Further processesing Line 3.
        network_col = net_flat_df['network'].str.split("/", expand=True)
        net_flat_df['IP Subnet'] = network_col[0].astype(str)
        net_flat_df['IP Cidr'] = network_col[1].astype(str).astype(int)

        # Further processing Line 4.
        net_flat_df = self.sort_df_by_oct_list(net_flat_df)

        # Further processing Line 5.
        net_flat_df = self.reindex_df(net_flat_df)
        return net_flat_df
