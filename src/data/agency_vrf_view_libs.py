#!/usr/bin/python
import os
from xlrd import open_workbook
import paramiko
from builder import EnvironmentValues
from builder import DirectoryValues
from builder import DataFileNames
from builder import Writer
from builder import Reader


class _LibraryBase:
    def __init__(self):
        self.env_cls = EnvironmentValues()
        self.dir_cls = DirectoryValues()
        self.filenames_cls = DataFileNames()
        self.write_cls = Writer()
        self.reader_cls = Reader()
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    @staticmethod
    def _isint(value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    def get_command(self, command):
        """Construct for ssh call to Tody Cools."""
        self.client.connect(
            self.env_cls.tody_cools(),
            username=self.env_cls.tacacs_username(),
            password=self.env_cls.tacacs_password())

        return self.client.exec_command(command)


class TodyCoolsCall(_LibraryBase):
    """
    Tody Cools Call for whois .*

    Data Received from the whois .* call:
    720California_WIRELESS=D375-01-VR-AT
    Access=D133-01-VR-AT
    Adelphi=D140-01-VR-AT
    """
    def whois_dict_from_stdout(self, raw_data):
        """Whois data processing."""
        data = {}
        for line in raw_data:
            if line.strip('\n'):
                data.update(
                    {line.strip('\n').split('=')[1]:
                     line.strip('\n').split('=')[0]}
                )
        self.client.close()
        self.write_cls.write_to_pkl(
            self.dir_cls.raw_dir(),
            self.filenames_cls.vrf_to_agency_filename(),
            data)

    def run_whois(self):
        """Performs whois call and processing."""
        stdin, stdout, stderr = self.get_command('whois .*')
        self.whois_dict_from_stdout(stdout)


class BuildLibraries(_LibraryBase):
    """Class for libraries to be used."""
    def run_build_libraries(self):
        """Instantiate Classes."""
        read_lib_cls = ReadLibraries()
        # Run build_vrf_and_view_mappings.
        ipam_network_views = read_lib_cls.read_network_views()
        vrf_to_agency_dict = read_lib_cls.read_whois()
        self.build_vrf_and_view_mappings(
            ipam_network_views,
            vrf_to_agency_dict)
        # Run build_ipam_agency_list.
        self.build_ipam_agency_list()
        # Run build_global_address_mapping.
        self.build_global_address_mapping()

    def build_ipam_agency_list(self):
        """
        Method that builds a list of all the agencies in the ipam
        agency ea attribute.
        """
        # Load the pickled Extensible Attributes List Values
        extensible_attributes_list_values = self.reader_cls.read_from_pkl(
            self.dir_cls.raw_dir(),
            self.filenames_cls.extensible_attributes_list_values_filename())
        ipam_agency_list = []
        # Display Extensible Attribute List Values
        for dictionary in extensible_attributes_list_values:
            if dictionary['name'] == 'Agency':
                for value in dictionary['list_values']:
                    ipam_agency_list.append(value['value'])
        # Write library:
        self.write_cls.write_to_pkl(
            self.dir_cls.raw_dir(),
            self.filenames_cls.ipam_agency_list_filename(),
            ipam_agency_list)

    def build_vrf_and_view_mappings(self, network_views, vrf_to_agency_dict):
        """Vrf to View mappings method."""
        view_to_vrf_dict = {}
        vrf_to_view_dict = {}
        # First checking for 3 digit numbers matching vrf to views where the
        # view does not have wan in the name.
        for item in network_views:
            for key in vrf_to_agency_dict.keys():
                if item['name'].split('-')[0][-3:] in key and \
                        self._isint(item['name'].split('-')[0][-3:]) and \
                        item['name'].split('-')[1] != 'WAN':
                    view_to_vrf_dict.update({item['name']: key})
                    vrf_to_view_dict.update({key: item['name']})
        # Second check is for 3 digit numbers matching vrf to views where the
        # view does have wan in the name if the vrf did not find a match in
        # the previous for loop.
        for key in vrf_to_agency_dict.keys():
            if key not in vrf_to_view_dict.keys():
                for view in network_views:
                    if key.split('-')[0][-3:] in view['name'] and \
                        self._isint(key.split('-')[0][-3:]) and \
                            view['name'].split('-')[1] == 'WAN':
                            view_to_vrf_dict.update({view['name']: key})
                            vrf_to_view_dict.update({key: view['name']})

        self.write_cls.write_to_pkl(
            self.dir_cls.raw_dir(),
            self.filenames_cls.view_to_vrf_lib(),
            view_to_vrf_dict)
        self.write_cls.write_to_pkl(
            self.dir_cls.raw_dir(),
            self.filenames_cls.vrf_to_view_lib(),
            vrf_to_view_dict)

    def build_global_address_mapping(self):
        """Builds global address mapping."""
        addr_file = os.path.join(
            self.dir_cls.raw_dir(),
            self.filenames_cls.src_global_addresses())
        addr_wb = open_workbook(addr_file)
        addr_ws = addr_wb.sheet_by_index(1)
        addr_data = []
        for enum in range(addr_ws.nrows):
            addr_data.append(addr_ws.row_values(enum))

        addr_data = {
            addr_line[0].strip(): {
                'site_name': addr_line[1],
                'city': addr_line[2],
                'country': addr_line[3],
                'region': addr_line[4],
                'country_code': addr_line[5]
            }
            for addr_line in addr_data if addr_line != addr_data[0]
        }

        self.write_cls.write_to_pkl(
            self.dir_cls.raw_dir(),
            self.filenames_cls.global_addresses_lib(),
            addr_data)


class ReadLibraries(_LibraryBase):
    """Reader class for BuildLibraries and TodyCools class objects."""
    def read_whois(self):
        """Reads in who is data from TodyCools."""
        return self.reader_cls.read_from_pkl(
            self.dir_cls.raw_dir(),
            self.filenames_cls.vrf_to_agency_filename())

    def read_agency_list(self):
        """Reads in who is data from TodyCools."""
        return self.reader_cls.read_from_pkl(
            self.dir_cls.raw_dir(),
            self.filenames_cls.ipam_agency_list_filename())

    def read_vrf_to_agency_dict(self):
        """Reads in vrf to agency dictionary."""
        return self.reader_cls.read_from_pkl(
            self.dir_cls.raw_dir(),
            self.filenames_cls.vrf_to_agency_filename())

    def read_network_views(self):
        """Reads in network view raw ipam data."""
        return self.reader_cls.read_from_pkl(
            self.dir_cls.raw_dir(),
            self.filenames_cls.network_views_filename())

    def read_view_to_vrf(self):
        """Reads in view to vrf dictionary."""
        return self.reader_cls.read_from_pkl(
            self.dir_cls.raw_dir(),
            self.filenames_cls.view_to_vrf_lib())

    def read_vrf_to_view(self):
        """Reads in vrf to view dictionary."""
        return self.reader_cls.read_from_pkl(
            self.dir_cls.raw_dir(),
            self.filenames_cls.vrf_to_view_lib())

    def read_global_address_lib(self):
        """Reads in global address pickled library."""
        return self.reader_cls.read_from_pkl(
            self.dir_cls.raw_dir(),
            self.filenames_cls.global_addresses_lib())
