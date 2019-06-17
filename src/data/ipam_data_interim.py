import sys
from builder import DirectoryValues
from builder import DataFilenames
from builder import LoggingValues
from builder import Reader
from ipam_apirequest_calltypes_callfilenames import IpamCallFilenames
import pandas as pd
from collections import MutableMapping


dir_cls = DirectoryValues()
ipam_filenames_cls = IpamCallFilenames()
data_filenames_cls = DataFilenames()
reader_cls = Reader()

# Load Networks Pickled Data
networks = reader_cls.read_from_pkl(dir_cls.raw_dir(),
                                    ipam_filenames_cls.networks_filename())
networkcontainers = reader_cls.read_from_pkl(dir_cls.raw_dir(),
                                             ipam_filenames_cls.
                                             networkcontainers_filename())
all_nets = networks + networkcontainers
# Display Networks
#print(len(networks))


# code to convert ini_dict to flattened dictionary
# default seperater '_'
def convert_flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k

        if isinstance(v, MutableMapping):
            items.extend(convert_flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


network_flat_list_of_dict = [convert_flatten(all_nets[i])
                             for i in range(len(all_nets))]
#print(len(network_flat_list_of_dict))

# Panda networks | Splitting up octets from net_df['networks']
# Converting the string representation within the df to an integer.
net_flat_df = pd.DataFrame.from_dict(network_flat_list_of_dict)
net_flat_df['net_type'] = net_flat_df['_ref'].str.split('/', expand = True)[0]


new = net_flat_df['network'].str.split(".", expand=True)

# Need to turn into a loop to handle this
net_flat_df["oct1"] = new[0].astype(str).astype(int)
net_flat_df["oct2"] = new[1].astype(str).astype(int)
net_flat_df["oct3"] = new[2].astype(str).astype(int)
newer = new[3].str.split("/", expand=True)
net_flat_df["oct4"] = newer[0].astype(str).astype(int)
net_flat_df["/Cidr"] = newer[1].astype(str).astype(int)

# Sorting the oct's and /Cidr.
net_flat_df = net_flat_df.sort_values(["oct1", "oct2", "oct3", "oct4", "/Cidr"], ascending=[True, True, True, True, True])
# print(net_flat_df)

xlsx_file = dir_cls.interim_dir() + '\\' + \
            data_filenames_cls.ipam_dump_interim_xlsx()
pickle_file = dir_cls.interim_dir() + '\\' + \
              data_filenames_cls.ipam_dump_interim_pickle()
# Need to get saved in the right directory.
net_flat_df.to_excel(xlsx_file, index=False)
net_flat_df.to_pickle(pickle_file)
