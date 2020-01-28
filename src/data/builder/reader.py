#!/usr/bin/python
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
