from builder import DirectoryValues
from builder import DataFileNames
from builder import Reader
import pandas as pd
from collections import MutableMapping


class IpamDataInterim:
    """Class to read in networks and networkcontainers to then be smashed,
    mangled, and spit out into a .pickle and .xlsx file

    """

    def __init__(self):
        self.dir_cls = DirectoryValues()
        self.ipam_filenames_cls = DataFileNames()
        self.reader_cls = Reader()

        # Load Networks Pickled Data
        self.networks = self.reader_cls.read_from_pkl(self.dir_cls.raw_dir(),
                                                      self.ipam_filenames_cls.
                                                      networks_filename())
        self.networkcontainers = self.reader_cls.read_from_pkl(
            self.dir_cls.raw_dir(),
            self.ipam_filenames_cls.networkcontainers_filename())
        self.all_nets = self.networks + self.networkcontainers

    def run_ipam_interim(self, xlsx, pickle):
        flattened_dict_data = self.flatten_data(self.all_nets)
        output_data = self.panda_processing_of_flattened_data(
            flattened_dict_data)
        output_data.to_excel(self.dir_cls.interim_dir() + '\\' + xlsx)
        output_data.to_pickle(self.dir_cls.interim_dir() + '\\' + pickle)

    def _convert_flatten(self, data, parent_key='', sep='_'):
        """Method to convert input of nested dict's to a flattened dict

        default seperater '_'

        """
        items = []
        for k, v in data.items():
            new_key = parent_key + sep + k if parent_key else k

            if isinstance(v, MutableMapping):
                items.extend(self._convert_flatten(
                    v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def flatten_data(self, data_to_be_flattened):
        """Method to flatten the requested data."""
        return [self._convert_flatten(data_to_be_flattened[i])
                for i in range(len(data_to_be_flattened))]

    def panda_processing_of_flattened_data(self, all_nets):
        """Turns the returned flat dict into a panda dataframe.

        Further processing:

        1. Add 'net_type' column.
        2. Add oct1, oct2, oct3, oct4, and /Cidr columns.
        3. Add oct1, oct2, oct3, oct4, and /Cidr columns.
        4. Sorting Data via line 2 values.
        5. Return Indexed data starting at 10000
        """

        net_flat_df = pd.DataFrame.from_dict(self.flatten_data(all_nets))

        # Further processing Line 1.
        net_flat_df['net_type'] = net_flat_df['_ref'].str.split(
            '/', expand=True)[0]

        # Further processing Line 2.
        oct_list = ['oct1', 'oct2', 'oct3', 'oct4', '/Cidr']
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

