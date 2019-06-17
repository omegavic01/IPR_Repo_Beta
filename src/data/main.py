from ipam_gets_to_writes import IpamGetsToWrite
from ipam_apirequest_calltypes_callfilenames import IpamApiRequest, \
    IpamCallTypes


"""What would you like to do?  Set to true or false based on what you would
like to do.
Option 1: Call ipam and pickle the data.
Option 2: Good place to call a single network view.  Set breakpoint to use for
          debugging.
"""

"""If you want to gather all the ipam data and pickle the data.
Option 1.
"""
gather_current_ipam_data = True
if gather_current_ipam_data:
    # Call IPAM data and Write to .pkl file.
    ip_data = IpamGetsToWrite()
#    ip_data.get_extensible_attributes()
#    ip_data.get_extensible_attributes_list_values()
#    ip_data.get_network_views()
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

gather_fill_me_in = False