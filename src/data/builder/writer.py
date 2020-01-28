#!/usr/bin/python
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
        with open(file, "w", newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerows(data)

    @staticmethod
    def write_to_csv_wb(file_dir, file_name, data):
        file = os.path.join(file_dir, file_name)
        with open(file, "wb", newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerows(data)

    @staticmethod
    def write_to_xlsx(file_dir, file_name, data):
        """STILL IN DEVELOPMENT!"""
        return file_dir, file_name, data
