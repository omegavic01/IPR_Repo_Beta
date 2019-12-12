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

import pickle
import csv
import os


class Writer:
    """Class used to write data to specific types of files."""
    @staticmethod
    def write_to_pkl(file_dir, file_name, data):
        """
        Method that takes the arg's and writes a .pkl file.

        args:
            file_dir: path to files location
            file_name: name of file to be opened
        """
        file = os.path.join(file_dir, file_name)
        with open(file, 'wb') as output:
            pickle.dump(data, output)

    @staticmethod
    def write_to_csv_w(file_dir, file_name, data):
        file = os.path.join(file_dir, file_name)
        with open(file, "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerows(data)

    @staticmethod
    def write_to_csv_wb(file_dir, file_name, data):
        file = os.path.join(file_dir, file_name)
        with open(file, "wb", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerows(data)

    @staticmethod
    def write_to_xlsx(file_dir, file_name, data):
        """STILL IN DEVELOPMENT!"""
        return file_dir, file_name, data
