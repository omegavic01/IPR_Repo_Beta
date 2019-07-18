from ipam_gets_to_writes import IpamGetsToWrite
from ipam_apirequest_calltypes import IpamApiRequest, IpamCallTypes
from ipam_data_processing import IpamDataInterim, IpamDataProcessed
from ipam_reports import IpamReports
from builder import DirectoryValues
from builder import DataFileNames
from builder import Reader


"""What would you like to do?  Set to true or false based on what you would
like to do.
Option 1: Call ipam and pickle the data.

Option 2: Takes in the networks and networkconatiners pickle files and bounces
            it through the ipam_data_interim script.
Option 3: Good place to call a single network view.  Set breakpoint to use for
          debugging.
"""

"""If you want to gather all the ipam data and pickle the data.
Option 1.
"""
gather_current_ipam_data = True
if gather_current_ipam_data:
    ip_data = IpamGetsToWrite()
    #ip_data.get_extensible_attributes()
    ip_data.get_extensible_attributes_list_values()
    #ip_data.get_network_views()
    #ip_data.get_networks()
    #ip_data.get_networkcontainers()

"""Run Ipam Data Interim.  This takes the data from the lastime
gather_current_ipam_data was run.  Then compiles the networks and 
networkcontainers into a .xlsx and .pickle file in the interim dir.
This data is expected to be processed by other scripts
"""
run_ipam_data_processing_interim = False
if run_ipam_data_processing_interim:
    data_filenames_cls = DataFileNames()
    ipam_interim = IpamDataInterim()
    raw_data = ipam_interim.get_raw_data_networks_networkcontainers()
    ipam_interim.run_ipam_interim(
        raw_data,
        data_filenames_cls.ipam_dump_interim_xlsx(),
        data_filenames_cls.ipam_dump_interim_panda(),
        data_filenames_cls.ipam_dump_interim_dicted())


run_ipam_data_processing_processed = False
if run_ipam_data_processing_processed:
    data_filenames_cls = DataFileNames()
    dir_cls = DirectoryValues()
    ipam_processing = IpamDataProcessed()
    read = Reader()
    interim_dir = dir_cls.interim_dir()
    ipam_processing.run_ipam_processing(
        read.read_from_pkl(dir_cls.interim_dir(),
                           data_filenames_cls.ipam_dump_interim_panda()))


run_ipam_reports = True
if run_ipam_reports:
    ipam_reports = IpamReports()
    ipam_reports.generate_ipam_to_ipr_report()
    ipam_reports.generate_percent_report()

"""Good place to debug network data from a network view.
"""
gather_network_data_for_a_network_view = False
if gather_network_data_for_a_network_view:
    # Call Ipam data.
    ipam_api_request_cls = IpamApiRequest()
    ipam_call_type_cls = IpamCallTypes()
    data_returned = ipam_api_request_cls.ipam_api_request(
        ipam_call_type_cls.networks('00324-CDS'))


