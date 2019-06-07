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


class Reader:

    @staticmethod
    def read_from_pkl(file_dir, file_name):
        with open(file_dir + "\\" + file_name, 'rb') as input:
            return pickle.load(input)

    @staticmethod
    def read_from_csv(file_dir, file_name):
        pass

    @staticmethod
    def read_from_xlsx(file_dir, file_name):
        pass