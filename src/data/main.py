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
from ipam_gets_to_writes import IpamGetsToWrite
from ipam_apirequest_calltypes import IpamApiRequest, IpamCallTypes
from ipam_processed_processing import IpamDataProcessed
from ipam_interim_processing import IpamDataInterim
from ipam_reports import IpamReports
import time

"""
Grouping of functions with a True/False tag.  Allows for the separation of the
main components of the scripts.  Which will compile and generate the reports
needed for IPR.

WIP: Update so these groupings can be coupled with either a website or
desktop application.  For external party use.
"""

gather_current_ipam_data = True
run_ipam_data_processing_interim = True
run_ipam_data_processing_processed = True
run_ipam_reports = True

start_time = time.perf_counter()

"""
This grouping calls and pickles the IB data via IB's web api.

Example Notebook: IPR_Data_Notebook.ipynb (Not in gitHub yet...) has examples 
of the below functions.
"""
if gather_current_ipam_data:
    ip_data = IpamGetsToWrite()
    ip_data.get_extensible_attributes()
    ip_data.get_extensible_attributes_list_values()
    ip_data.get_network_views()
    ip_data.get_networks()
    ip_data.get_networkcontainers()


"""
This grouping takes the raw data gathered from the above set of commands. Then 
builds out the interim data sets used by the processing set of commands listed 
below this subgroup.

Example Notebook: Builder Notebook.ipynb (Not in gitHub yet...) has examples
of the calls that the below functions perform.
"""
if run_ipam_data_processing_interim:
    ipam_interim = IpamDataInterim()
    ipam_interim.run_ipam_interim(write_to_xlsx=False)

"""
This grouping takes the interim data set and processes the data to be used for 
the reporting function listed below this group.

Example Notebook: ipam_data_processed.ipynb (Not in gitHub yet...)
"""
if run_ipam_data_processing_processed:
    ipam_processing = IpamDataProcessed()
    ipam_processing.run_ipam_processing()

"""
This grouping is for the final reports that are generated for production use.
"""
if run_ipam_reports:
    ipam_reports = IpamReports()
    ipam_reports.generate_ipam_to_ipr_report()
    ipam_reports.generate_percent_report()
    ipam_reports.generate_forecast_percent_report()

end_time = time.perf_counter()
print(end_time - start_time)

"""
Good place to debug network data from a network view.  This is not to be used 
for the main report generation.

****For Debug Use Only****

Recommend to disable the above group of functions if you plan on debugging 
here.
"""
gather_network_data_for_a_network_view = False
if gather_network_data_for_a_network_view:
    # Call Ipam data.
    ipam_api_request_cls = IpamApiRequest()
    ipam_call_type_cls = IpamCallTypes()
    data_returned = ipam_api_request_cls.ipam_api_request(
        ipam_call_type_cls.networks('view_name'))
