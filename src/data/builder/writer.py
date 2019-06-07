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

import pickle


class Writer:

    @staticmethod
    def write_to_pkl(file_dir, file_name, data):
        with open(file_dir + "\\" + file_name, 'wb') as output:
            pickle.dump(data, output)

    @staticmethod
    def write_to_csv(file_dir, file_name, data):
        pass

    @staticmethod
    def write_to_xlsx(file_dir, file_name, data):
        pass
