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

import unittest
from builder import \
    EnvironmentValues, \
    DirectoryValues, \
    LoggingValues, \
    DataFileNames


class TestProjDataFileNames(unittest.TestCase):

    def setUp(self):
        """Testing IpamCallFilenames()"""
        self.ipam_data_filenames_cls = DataFileNames()

    def test_create_IpamCallFilenames_intance(self):
        self.ipam_data_filenames_cls = DataFileNames()

    def test_type_extensible_attributes_filename(self):
        self.assertIsInstance(self.ipam_data_filenames_cls.
                              extensible_attributes_filename(),
                              str)

    def test_eq_extensible_attributes_filename(self):
        self.assertEqual('extensible_attributes.pkl',
                         self.ipam_data_filenames_cls.
                         extensible_attributes_filename())

    def test_type_extensible_attributes_list_values_filename(self):
        self.assertIsInstance(self.ipam_data_filenames_cls.
                              extensible_attributes_list_values_filename(),
                              str)

    def test_eq_extensible_attributes_list_values_filename(self):
        self.assertEqual('extensible_attributes_list_values.pkl',
                         self.ipam_data_filenames_cls.
                         extensible_attributes_list_values_filename())

    def test_type_network_views_filename(self):
        self.assertIsInstance(self.ipam_data_filenames_cls.
                              network_views_filename(),
                              str)

    def test_eq_network_views_filename(self):
        self.assertEqual('network_views.pkl',
                         self.ipam_data_filenames_cls.network_views_filename())

    def test_type_networks_filename(self):
        self.assertIsInstance(self.ipam_data_filenames_cls.
                              networks_filename(),
                              str)

    def test_eq_networks_filename(self):
        self.assertEqual('networks.pkl',
                         self.ipam_data_filenames_cls.networks_filename())

    def test_type_networkcontainers_filename(self):
        self.assertIsInstance(self.ipam_data_filenames_cls.
                              networkcontainers_filename(),
                              str)

    def test_eq_networkcontainers_filename(self):
        self.assertEqual('networkcontainers.pkl',
                         self.ipam_data_filenames_cls.
                         networkcontainers_filename())


class TestProjEnvVariables(unittest.TestCase):

    def setUp(self):
        self.env_cls = EnvironmentValues()

    def test_type_of_env_cls_payload_url(self):
        self.assertIsInstance(self.env_cls.payload_url(), str)

    def test_type_of_env_cls_payload_username(self):
        self.assertIsInstance(self.env_cls.payload_username(), str)

    def test_type_of_env_cls_payload_password(self):
        self.assertIsInstance(self.env_cls.payload_password(), str)

    def test_type_of_env_cls_header_row(self):
        self.assertIsInstance(self.env_cls.header_row(), list)


class TestProjDirVariables(unittest.TestCase):

    def setUp(self):
        self.dir_cls = DirectoryValues()

    def test_type_of_dir_cls_interim_dir(self):
        self.assertIsInstance(self.dir_cls.interim_dir(), str)

    def test_type_of_dir_cls_processed_dir(self):
        self.assertIsInstance(self.dir_cls.processed_dir(), str)

    def test_type_of_dir_cls_raw_dri(self):
        self.assertIsInstance(self.dir_cls.raw_dir(), str)

    def test_type_of_dir_cls_reports_dir(self):
        self.assertIsInstance(self.dir_cls.reports_dir(), str)


if __name__ == '__main__':
    unittest.main()
