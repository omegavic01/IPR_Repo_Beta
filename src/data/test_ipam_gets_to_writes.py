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

from ipam_gets_to_writes import IpamGetsToWrite
import unittest


class TestIpamGetsToWrite(unittest.TestCase):

    def setUp(self):
        self.gets_to_writes_cls = IpamGetsToWrite()

    def test_return_network_views(self):
        self.assertIsInstance(self.gets_to_writes_cls.
                              return_network_views(),
                              list)


if __name__ == '__main__':
    unittest.main()
