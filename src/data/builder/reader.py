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
import os


class Reader:
    """Class to be used for reading specific types of files."""
    @staticmethod
    def read_from_pkl(file_dir, file_name):
        """
        Method that takes the arg's and reads a .pkl file.  Then returns
        the data opened.

        args:
            file_dir: path to files location
            file_name: name of file to be opened
        returns:
            -The data from the pickled file.
        """
        file = os.path.join(file_dir, file_name)
        with open(file, 'rb') as file_input:
            return pickle.load(file_input)

    @staticmethod
    def read_from_csv(file_dir, file_name):
        """
        Method that takes the arg's and reads a .csv file.  Then returns
        the data read.

        STILL IN DEVELOPMENT!

        args:
            file_dir: path to files location
            file_name: name of file to be opened
        returns:
            -The data from the .csv file.
        """
        return file_dir, file_name

    @staticmethod
    def read_from_xlsx(file_dir, file_name):
        """
        Method that takes the arg's and reads a .xlsx file.  Then returns
        the data read.

        STILL IN DEVELOPMENT!

        args:
            file_dir: path to files location
            file_name: name of file to be opened
        returns:
            -The data from the .xlsx file.
        """
        return file_dir, file_name
