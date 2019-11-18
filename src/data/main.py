"""
Grouping of functions with a True/False tag.  Allows for the separation of the
main components of the scripts.  Which will compile and generate the reports
needed for IPR.

WIP: Update so these groupings can be coupled with either a website or
desktop application.  For external party use.

"""
from ipam_gets_to_writes import IpamGetsToWrite
from ipam_apirequest_calltypes import IpamApiRequest, IpamCallTypes
from ipam_data_processing import IpamDataInterim, IpamDataProcessed
from ipam_reports import IpamReports
from builder import DirectoryValues, DataFileNames, Reader


"""
This grouping calls and pickles the IB data via IB's web api.

Example Notebook: IPR_Data_Notebook.ipynb (Not in gitHub yet...) has examples 
of the below functions.

"""
gather_current_ipam_data = True
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
run_ipam_data_processing_interim = True
if run_ipam_data_processing_interim:
    data_filenames_cls = DataFileNames()
    ipam_interim = IpamDataInterim()
    raw_data = ipam_interim.get_raw_data_networks_networkcontainers()
    ipam_interim.run_ipam_interim(
        raw_data,
        data_filenames_cls.ipam_dump_interim_xlsx(),
        data_filenames_cls.ipam_dump_interim_panda(),
        data_filenames_cls.ipam_dump_interim_dicted())


"""
This grouping takes the interim data set and processes the data to be used for 
the reporting function listed below this group.

WIP: "summary" statement and "full_dataset_ipr_d" keywords shown in the
ipam_processing.run_ipam_processing().

Example Notebook: ipam_data_processed.ipynb (Not in gitHub yet...)

"""
run_ipam_data_processing_processed = True
if run_ipam_data_processing_processed:
    data_filenames_cls = DataFileNames()
    dir_cls = DirectoryValues()
    ipam_processing = IpamDataProcessed()
    read = Reader()
    interim_dir = dir_cls.interim_dir()
    ipam_processing.run_ipam_processing(
        read.read_from_pkl(dir_cls.interim_dir(),
                           data_filenames_cls.ipam_dump_interim_panda()),
        summary=False,
        full_dataset_ipr_d=False)


"""
This grouping is for the final reports that are generated for production use.

WIP: generate_forecast_percent_report() (This function at the moment is only
    duplicating ipam_reports.generate_percent_report().)  Looking to create
    and finalize this report for internal use.

"""
run_ipam_reports = True
if run_ipam_reports:
    ipam_reports = IpamReports()
    ipam_reports.generate_ipam_to_ipr_report()
    ipam_reports.generate_percent_report()
    ipam_reports.generate_forecast_percent_report()


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
        ipam_call_type_cls.networks('00324-CDS'))
