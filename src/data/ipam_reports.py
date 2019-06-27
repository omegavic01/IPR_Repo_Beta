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
from collections import MutableMapping
from collections import OrderedDict
import pandas as pd
import logging
import time
import shutil, os
import xlsxwriter
from datetime import datetime
from builder import DirectoryValues
from builder import DataFileNames
from builder import EnvironmentValues
from builder import LoggingValues
from builder import Reader
from builder import Writer


class IpamReports:

    @staticmethod
    def _get_file_date(file):
        """Returns creation date of file."""
        date_str = time.ctime(os.path.getmtime(file))
        datetime_object = datetime.strptime(date_str, '%a %b %d %H:%M:%S %Y')
        return datetime_object.strftime('%Y-%m-%d')

    @staticmethod
    def _get_new_file_name_with_date_added(date, file_name):
        """Will work on xlsx extension files only."""
        date += '.xlsx'
        return file_name[:-5] + '-' + date

    @staticmethod
    def _create_ipam_report(processed_file, report_file):
        shutil.copy(processed_file, report_file)

    def generate_reports(self):
        # Build needed classe data
        data_filename_cls = DataFileNames()
        dir_cls = DirectoryValues()
        process_dir = dir_cls.processed_dir()
        reports_dir = dir_cls.reports_dir()
        ipam_filename = data_filename_cls.processed_filename()
        ipam_to_ipr_xlsx = process_dir + '\\' + ipam_filename
        date = self._get_file_date(ipam_to_ipr_xlsx)
        reports_ipam_filename = \
            self._get_new_file_name_with_date_added(date, ipam_filename)
        reports_ipam_to_ipr_xlsx = reports_dir + '\\' + reports_ipam_filename
        self._create_ipam_report(ipam_to_ipr_xlsx, reports_ipam_to_ipr_xlsx)



