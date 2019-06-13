from ipam_gets_to_writes import IpamGetsToWrite
import unittest


class Test_IpamGetsToWrite(unittest.TestCase):

    def setUp(self):
        self.gets_to_writes_cls = IpamGetsToWrite()

    def test_return_network_views(self):
        self.assertIsInstance(self.gets_to_writes_cls.
                              return_network_views(),
                              list)


if __name__ == '__main__':
    unittest.main()