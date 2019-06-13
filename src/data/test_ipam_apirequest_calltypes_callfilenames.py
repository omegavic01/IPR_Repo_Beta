import unittest
import json
from ipam_apirequest_calltypes_callfilenames import IpamCallFilenames
from ipam_apirequest_calltypes_callfilenames import IpamCallTypes
from ipam_apirequest_calltypes_callfilenames import IpamApiRequest


class TestIpamCallFilenames(unittest.TestCase):

    def setUp(self):
        self.ipam_call_filenames_cls = IpamCallFilenames()

    def test_type_extensible_attributes_filename(self):
        self.assertIsInstance(self.ipam_call_filenames_cls.
                              extensible_attributes_filename(),
                              str)

    def test_eq_extensible_attributes_filename(self):
        self.assertTrue(self.ipam_call_filenames_cls.
                        extensible_attributes_filename() ==
                        'extensible_attributes.pkl')

    def test_type_extensible_attributes_list_values_filename(self):
        self.assertIsInstance(self.ipam_call_filenames_cls.
                              extensible_attributes_list_values_filename(),
                              str)

    def test_eq_extensible_attributes_list_values_filename(self):
        self.assertTrue(self.ipam_call_filenames_cls.
                        extensible_attributes_list_values_filename() ==
                        'extensible_attributes_list_values.pkl')

    def test_type_network_views_filename(self):
        self.assertIsInstance(self.ipam_call_filenames_cls.
                              network_views_filename(),
                              str)

    def test_eq_network_views_filename(self):
        self.assertTrue(self.ipam_call_filenames_cls.
                        network_views_filename() ==
                        'network_views.pkl')

    def test_type_networks_filename(self):
        self.assertIsInstance(self.ipam_call_filenames_cls.
                              networks_filename(),
                              str)

    def test_eq_networks_filename(self):
        self.assertTrue(self.ipam_call_filenames_cls.
                        networks_filename() ==
                        'networks.pkl')

    def test_type_networkcontainers_filename(self):
        self.assertIsInstance(self.ipam_call_filenames_cls.
                              networkcontainers_filename(),
                              str)

    def test_eq_networkcontainers_filename(self):
        self.assertTrue(self.ipam_call_filenames_cls.
                        networkcontainers_filename() ==
                        'networkcontainers.pkl')


class TestIpamCallTypes(unittest.TestCase):

    def setUp(self):
        self.ipam_call_types_cls = IpamCallTypes()

    def test_type_extensible_attributes(self):
        self.assertIsInstance(self.ipam_call_types_cls.
                              extensible_attributes(),
                              str)

    def test_eq_extensible_attributes(self):
        self.assertTrue(self.ipam_call_types_cls.extensible_attributes() ==
                        'extensibleattributedef?')

    def test_type_extensible_attributes_list_values(self):
        self.assertIsInstance(self.ipam_call_types_cls.
                              extensible_attributes_list_values(),
                              str)

    def test_eq_extensible_attributes_list_values(self):
        self.assertTrue(self.ipam_call_types_cls.
                        extensible_attributes_list_values() ==
                        "extensibleattributedef?"
                        "_return_fields="
                        "list_values,"
                        "comment,"
                        "name,"
                        "type")

    def test_type_network_views(self):
        self.assertIsInstance(self.ipam_call_types_cls.
                              network_views(),
                              str)

    def test_eq_network_views(self):
        self.assertTrue(self.ipam_call_types_cls.
                        network_views() ==
                        'networkview?')

    def test_type_network(self):
        self.assertIsInstance(self.ipam_call_types_cls.
                              networks('default'),
                              str)

    def test_eq_network(self):
        self.assertTrue(self.ipam_call_types_cls.
                        networks('default') ==
                        "network?"
                        "_return_fields="
                        "extattrs,"
                        "comment,"
                        "network,"
                        "network_view,"
                        "utilization&"
                        "network_view=default"
                        "&_max_results=-5000")

    def test_type_networkcontainers(self):
        self.assertIsInstance(self.ipam_call_types_cls.
                              networkcontainers('default'),
                              str)

    def test_eq_networkcontainers(self):
        self.assertTrue(self.ipam_call_types_cls.
                        networkcontainers('default') ==
                        "networkcontainer?"
                        "_return_fields="
                        "extattrs,"
                        "comment,"
                        "network,"
                        "network_view,"
                        "utilization&"
                        "network_view=default"
                        "&_max_results=-5000")


class TestIpamApiRequest(unittest.TestCase):

    def setUp(self):
        """Testing apirequest with .extensible_attributes()"""
        self.ipam_api_request_cls = IpamApiRequest()
        self.ipam_call_types_cls = IpamCallTypes()
        self.api_request_extensible_attributes = self.ipam_api_request_cls. \
            ipam_api_request(
                                self.ipam_call_types_cls.
                                extensible_attributes())

    def test_return_api_request_extensible_attributes(self):
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
        self.assertIsInstance(self.ipam_api_request_cls.load_as_json(self.
                                                                     api_request_extensible_attributes.
                                                                     text),
                              list)
        self.assertIsInstance(self.ipam_api_request_cls.load_as_json(self.
                                                                     api_request_extensible_attributes.
                                                                     text)[0],
                              dict)
        self.assertTrue(self.api_request_extensible_attributes.status_code ==
                        200)
        self.assertTrue(self.api_request_extensible_attributes.encoding is
                        None)
        self.assertTrue(self.api_request_extensible_attributes.is_redirect is
                        False)
        self.assertTrue(self.api_request_extensible_attributes.
                        is_permanent_redirect is
                        False)
        self.assertTrue(self.api_request_extensible_attributes.text ==
                        self.api_request_extensible_attributes.
                        content.
                        decode('utf-8'))


if __name__ == '__main__':
    unittest.main()

