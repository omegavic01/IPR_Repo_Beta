from ipam_gets_to_writes import IpamGetsToWrite
from ipam_apirequest_calltypes_callfilenames import IpamApiRequest, \
    IpamCallTypes
from ipam_data_interim import IpamDataInterim
from ipam_data_processed import IpamDataProcessed
from builder import DirectoryValues
from builder import DataFileNames


"""What would you like to do?  Set to true or false based on what you would
like to do.
Option 1: Call ipam and pickle the data.
Option 2: Good place to call a single network view.  Set breakpoint to use for
          debugging.
Option 3: Takes in the networks and networkconatiners pickle files and bounces
            it through the ipam_data_interim script.
"""

"""If you want to gather all the ipam data and pickle the data.
Option 1.
"""
gather_current_ipam_data = False
if gather_current_ipam_data:
    # Call IPAM data and Write to .pkl file.
    ip_data = IpamGetsToWrite()
    ip_data.get_extensible_attributes()
    ip_data.get_extensible_attributes_list_values()
    ip_data.get_network_views()
    ip_data.get_networks()
    ip_data.get_networkcontainers()

"""Good place to debug network data from a network view.
Option 2.
"""
gather_network_data_for_a_network_view = False
if gather_network_data_for_a_network_view:
    # Call Ipam data.
    ipam_api_request_cls = IpamApiRequest()
    ipam_call_type_cls = IpamCallTypes()
    data_returned = ipam_api_request_cls.ipam_api_request(
        ipam_call_type_cls.networks('00324-CDS'))

"""Run Ipam Data Interim.  This takes the data from the lastime
gather_current_ipam_data was run.  Then compiles the networks and 
networkcontainers into a .xlsx and .pickle file in the interim dir.
This data is expected to be processed by other scripts
"""
run_ipam_data_interim = True
if run_ipam_data_interim:
    data_filenames_cls = DataFileNames()
    ipam_interim = IpamDataInterim()
    ipam_interim.run_ipam_interim(
        data_filenames_cls.ipam_dump_interim_xlsx(),
        data_filenames_cls.ipam_dump_interim_pickle())

run_ipam_data_processed = True
if run_ipam_data_processed:
    filenames_cls = DataFileNames()
    dir_cls = DirectoryValues()
    ipam_processed = IpamDataProcessed()
    ipam_processed.run_ipam_processed(
        ipam_processed.load_pickle_file(
            dir_cls.interim_dir(),
            filenames_cls.ipam_dump_interim_pickle()))
