#!/usr/bin/python
"""
Copyright 2007 HVictor
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
from ipaddr import IPv4Network


class Cgn(IPv4Network):
    """ipaddr module extension checking for carrier grade nats."""
    def is_cgn(self):
        """
        Test if the address is RFC 6598 CGN reserved.

         Returns:
             A boolean, True if the address is within the
             reserved CGN IPv4 Network range.
        """
        return self in IPv4Network('100.64.0.0/10')
