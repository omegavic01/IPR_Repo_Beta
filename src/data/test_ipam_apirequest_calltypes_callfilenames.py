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
import json
from ipam_apirequest_calltypes_callfilenames import IpamCallFilenames
from ipam_apirequest_calltypes_callfilenames import IpamCallTypes
from ipam_apirequest_calltypes_callfilenames import IpamApiRequest


class TestIpamCallFilenames(unittest.TestCase):

    def setUp(self):
        """Testing IpamCallFilenames()"""
        self.ipam_call_filenames_cls = IpamCallFilenames()

    def test_create_IpamCallFilenames_intance(self):
        self.ipam_call_filenames_cls = IpamCallFilenames()

    def test_type_extensible_attributes_filename(self):
        self.assertIsInstance(self.ipam_call_filenames_cls.
                              extensible_attributes_filename(),
                              str)

    def test_eq_extensible_attributes_filename(self):
        self.assertEqual('extensible_attributes.pkl',
                         self.ipam_call_filenames_cls.
                         extensible_attributes_filename())

    def test_type_extensible_attributes_list_values_filename(self):
        self.assertIsInstance(self.ipam_call_filenames_cls.
                              extensible_attributes_list_values_filename(),
                              str)

    def test_eq_extensible_attributes_list_values_filename(self):
        self.assertEqual('extensible_attributes_list_values.pkl',
                         self.ipam_call_filenames_cls.
                         extensible_attributes_list_values_filename())

    def test_type_network_views_filename(self):
        self.assertIsInstance(self.ipam_call_filenames_cls.
                              network_views_filename(),
                              str)

    def test_eq_network_views_filename(self):
        self.assertEqual('network_views.pkl',
                         self.ipam_call_filenames_cls.network_views_filename())

    def test_type_networks_filename(self):
        self.assertIsInstance(self.ipam_call_filenames_cls.
                              networks_filename(),
                              str)

    def test_eq_networks_filename(self):
        self.assertEqual('networks.pkl',
                         self.ipam_call_filenames_cls.networks_filename())

    def test_type_networkcontainers_filename(self):
        self.assertIsInstance(self.ipam_call_filenames_cls.
                              networkcontainers_filename(),
                              str)

    def test_eq_networkcontainers_filename(self):
        self.assertEqual('networkcontainers.pkl',
                         self.ipam_call_filenames_cls.
                         networkcontainers_filename())


class TestIpamCallTypes(unittest.TestCase):

    def setUp(self):
        """Testing IpamCallTypes"""
        self.ipam_call_types_cls = IpamCallTypes()

    def test_create_IpamCallTypes_instance(self):
        self.ipam_call_types_cls = IpamCallTypes()

    def test_type_extensible_attributes(self):
        self.assertIsInstance(self.ipam_call_types_cls.
                              extensible_attributes(),
                              str)

    def test_eq_extensible_attributes(self):
        self.assertEqual('extensibleattributedef?',
                         self.ipam_call_types_cls.extensible_attributes())

    def test_type_extensible_attributes_list_values(self):
        self.assertIsInstance(self.ipam_call_types_cls.
                              extensible_attributes_list_values(),
                              str)

    def test_eq_extensible_attributes_list_values(self):
        self.assertEqual(
            "extensibleattributedef?"
            "_return_fields="
            "list_values,"
            "comment,"
            "name,"
            "type",
            self.ipam_call_types_cls.extensible_attributes_list_values())

    def test_type_network_views(self):
        self.assertIsInstance(self.ipam_call_types_cls.
                              network_views(),
                              str)

    def test_eq_network_views(self):
        self.assertEqual('networkview?',
                         self.ipam_call_types_cls.network_views())

    def test_type_network(self):
        self.assertIsInstance(self.ipam_call_types_cls.
                              networks('default'),
                              str)

    def test_eq_network(self):
        self.assertEqual(
            "network?"
            "_return_fields="
            "extattrs,"
            "comment,"
            "network,"
            "network_view,"
            "utilization&"
            "network_view=default"
            "&_max_results=-5000",
            self.ipam_call_types_cls.networks('default'))

    def test_type_networkcontainers(self):
        self.assertIsInstance(self.ipam_call_types_cls.
                              networkcontainers('default'),
                              str)

    def test_eq_networkcontainers(self):
        self.assertEqual(
            "networkcontainer?"
            "_return_fields="
            "extattrs,"
            "comment,"
            "network,"
            "network_view,"
            "utilization&"
            "network_view=default"
            "&_max_results=-5000",
            self.ipam_call_types_cls.networkcontainers('default'))


class TestIpamApiRequestExtensibleAttributes(unittest.TestCase):

    def setUp(self):
        """Testing apirequest with extensible_attributes()"""
        self.ipam_api_request_cls = IpamApiRequest()
        self.ipam_call_types_cls = IpamCallTypes()
        self.api_request_extensible_attributes = \
            self.ipam_api_request_cls.ipam_api_request(
                self.ipam_call_types_cls.extensible_attributes())

    def test_create_IpamApiRequest_instance(self):
        self.ipam_api_request_cls = IpamApiRequest()

    def test_create_IpamCallTypes_instance(self):
        self.ipam_call_types_cls = IpamCallTypes()

    def test_eq_extensible_attributes(self):
        self.assertEqual('extensibleattributedef?',
                         self.ipam_call_types_cls.extensible_attributes())

    def test_return_api_request_extensible_attributes(self):
        """Built multiple assertions to keep api calls to one."""
        self.assertIsInstance(self.api_request_extensible_attributes.
                              content,
                              bytes)
        self.assertIsInstance(self.api_request_extensible_attributes.
                              text,
                              str)
        self.assertIsInstance(json.loads(self.
                                         api_request_extensible_attributes.
                                         text),
                              list)
        self.assertIsInstance(json.loads(self.
                                         api_request_extensible_attributes.
                                         text)[0],
                              dict)
        self.assertIsInstance(self.ipam_api_request_cls.loads_as_json(
            self.api_request_extensible_attributes.text),
                              list)
        self.assertIsInstance(self.ipam_api_request_cls.loads_as_json(
            self.api_request_extensible_attributes.text)[0],
                              dict)
        self.assertEqual(200,
                         self.api_request_extensible_attributes.status_code)
        self.assertEqual(None, self.api_request_extensible_attributes.encoding)
        self.assertEqual(False,
                         self.api_request_extensible_attributes.is_redirect)
        self.assertEqual(False,
                         self.api_request_extensible_attributes.
                         is_permanent_redirect)
        self.assertEqual(self.api_request_extensible_attributes.text,
                         self.api_request_extensible_attributes.content.
                         decode('utf-8'))


class TestIpamApiRequestExtensibleAttributesListValues(unittest.TestCase):

    def setUp(self):
        """Testing apirequest with extensible_attributes_list_values()"""
        self.ipam_api_request_cls = IpamApiRequest()
        self.ipam_call_types_cls = IpamCallTypes()
        self.api_request_extensible_attributes_list_values = \
            self.ipam_api_request_cls.ipam_api_request(
                self.ipam_call_types_cls.extensible_attributes_list_values())

    def test_create_IpamApiRequest_instance(self):
        self.ipam_api_request_cls = IpamApiRequest()

    def test_create_IpamCallTypes_instance(self):
        self.ipam_call_types_cls = IpamCallTypes()

    def test_eq_extensible_attributes_list_values(self):
        self.assertEqual(
            "extensibleattributedef?"
            "_return_fields="
            "list_values,"
            "comment,"
            "name,"
            "type",
            self.ipam_call_types_cls.extensible_attributes_list_values())

    def test_return_api_request_extensible_attributes_list_values(self):
        """Built multiple assertions to keep api calls to one."""
        self.assertIsInstance(
            self.api_request_extensible_attributes_list_values.content,
            bytes)
        self.assertIsInstance(
            self.api_request_extensible_attributes_list_values.text,
            str)
        self.assertIsInstance(json.loads(
            self.api_request_extensible_attributes_list_values.text),
                              list)
        self.assertIsInstance(json.loads(
            self.api_request_extensible_attributes_list_values.text)[0],
                              dict)
        self.assertIsInstance(self.ipam_api_request_cls.loads_as_json(
            self.api_request_extensible_attributes_list_values.text),
                              list)
        self.assertIsInstance(self.ipam_api_request_cls.loads_as_json(
            self.api_request_extensible_attributes_list_values.text)[0],
                              dict)
        self.assertEqual(200,
                         self.api_request_extensible_attributes_list_values.
                         status_code)
        self.assertEqual(None,
                         self.api_request_extensible_attributes_list_values.
                         encoding)
        self.assertEqual(False,
                         self.api_request_extensible_attributes_list_values.
                         is_redirect)
        self.assertEqual(False,
                         self.api_request_extensible_attributes_list_values.
                         is_permanent_redirect)
        self.assertEqual(
            self.api_request_extensible_attributes_list_values.text,
            self.api_request_extensible_attributes_list_values.content.
            decode('utf-8'))


class TestIpamApiRequestNetworkViews(unittest.TestCase):

    def setUp(self):
        """Testing apirequest with network_views()"""
        self.ipam_api_request_cls = IpamApiRequest()
        self.ipam_call_types_cls = IpamCallTypes()
        self.api_request_network_views = \
            self.ipam_api_request_cls.ipam_api_request(
                self.ipam_call_types_cls.network_views())

    def test_create_IpamApiRequest_instance(self):
        self.ipam_api_request_cls = IpamApiRequest()

    def test_create_IpamCallTypes_instance(self):
        self.ipam_call_types_cls = IpamCallTypes()

    def test_eq_network_views(self):
        self.assertEqual('networkview?',
                         self.ipam_call_types_cls.network_views())

    def test_return_api_request_network_views(self):
        """Built multiple assertions to keep api calls to one."""
        self.assertIsInstance(
            self.api_request_network_views.content,
            bytes)
        self.assertIsInstance(
            self.api_request_network_views.text,
            str)
        self.assertIsInstance(json.loads(
            self.api_request_network_views.text),
            list)
        self.assertIsInstance(json.loads(
            self.api_request_network_views.text)[0],
                              dict)
        self.assertIsInstance(self.ipam_api_request_cls.loads_as_json(
            self.api_request_network_views.text),
            list)
        self.assertIsInstance(self.ipam_api_request_cls.loads_as_json(
            self.api_request_network_views.text)[0],
                              dict)
        self.assertEqual(200, self.api_request_network_views.status_code)
        self.assertEqual(None, self.api_request_network_views.encoding)
        self.assertEqual(False, self.api_request_network_views.is_redirect)
        self.assertEqual(False, self.api_request_network_views.
                         is_permanent_redirect)
        self.assertEqual(self.api_request_network_views.text,
                         self.api_request_network_views.
                         content.decode('utf-8'))


class TestIpamApiRequestNetworks(unittest.TestCase):

    def setUp(self):
        """Testing apirequest with networks()"""
        self.ipam_api_request_cls = IpamApiRequest()
        self.ipam_call_types_cls = IpamCallTypes()
        self.api_request_networks = \
            self.ipam_api_request_cls.ipam_api_request(
                self.ipam_call_types_cls.networks('default'))

    def test_create_IpamApiRequest_instance(self):
        self.ipam_api_request_cls = IpamApiRequest()

    def test_create_IpamCallTypes_instance(self):
        self.ipam_call_types_cls = IpamCallTypes()

    def test_eq_network(self):
        self.assertEqual(
            "network?"
            "_return_fields="
            "extattrs,"
            "comment,"
            "network,"
            "network_view,"
            "utilization&"
            "network_view=default"
            "&_max_results=-5000",
            self.ipam_call_types_cls.networks('default'))

    def test_return_api_request_networks(self):
        """Built multiple assertions to keep api calls to one."""
        self.assertIsInstance(
            self.api_request_networks.content,
            bytes)
        self.assertIsInstance(
            self.api_request_networks.text,
            str)
        self.assertIsInstance(json.loads(
            self.api_request_networks.text),
            list)
        with self.assertRaises(IndexError):
            self.assertIsInstance(json.loads(
                self.api_request_networks.text)[0])
        self.assertIsInstance(self.ipam_api_request_cls.loads_as_json(
            self.api_request_networks.text),
            list)
        with self.assertRaises(IndexError):
            self.ipam_api_request_cls.loads_as_json(
                self.api_request_networks.text)[0]
        self.assertEqual(200, self.api_request_networks.status_code)
        self.assertEqual(None, self.api_request_networks.encoding)
        self.assertEqual(False, self.api_request_networks.is_redirect)
        self.assertEqual(False, self.api_request_networks.
                         is_permanent_redirect)
        self.assertEqual(self.api_request_networks.text,
                         self.api_request_networks.content.decode('utf-8'))


class TestIpamApiRequestNetworkcontainers(unittest.TestCase):

    def setUp(self):
        """Testing apirequest with networks()"""
        self.ipam_api_request_cls = IpamApiRequest()
        self.ipam_call_types_cls = IpamCallTypes()
        self.api_request_networks = \
            self.ipam_api_request_cls.ipam_api_request(
                self.ipam_call_types_cls.networkcontainers('default'))

    def test_create_IpamApiRequest_instance(self):
        self.ipam_api_request_cls = IpamApiRequest()

    def test_create_IpamCallTypes_instance(self):
        self.ipam_call_types_cls = IpamCallTypes()

    def test_eq_networkcontainers(self):
        self.assertEqual(
            "networkcontainer?"
            "_return_fields="
            "extattrs,"
            "comment,"
            "network,"
            "network_view,"
            "utilization&"
            "network_view=default"
            "&_max_results=-5000",
            self.ipam_call_types_cls.networkcontainers('default'))

    def test_return_api_request_networkcontainers(self):
        """Built multiple assertions to keep api calls to one."""
        self.assertIsInstance(
            self.api_request_networks.content,
            bytes)
        self.assertIsInstance(
            self.api_request_networks.text,
            str)
        self.assertIsInstance(json.loads(
            self.api_request_networks.text),
            list)
        with self.assertRaises(IndexError):
            self.assertIsInstance(json.loads(
                self.api_request_networks.text)[0])
        self.assertIsInstance(self.ipam_api_request_cls.loads_as_json(
            self.api_request_networks.text),
            list)
        with self.assertRaises(IndexError):
            self.ipam_api_request_cls.loads_as_json(
                self.api_request_networks.text)[0]
        self.assertEqual(200, self.api_request_networks.status_code)
        self.assertEqual(None, self.api_request_networks.encoding)
        self.assertEqual(False, self.api_request_networks.is_redirect)
        self.assertEqual(False, self.api_request_networks.
                         is_permanent_redirect)
        self.assertEqual(self.api_request_networks.text,
                         self.api_request_networks.content.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
