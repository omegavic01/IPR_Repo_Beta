from ipam_gets_to_writes import IpamGetsToWrite


"""What would you like to do?  Set to true or false based on what you would
like to do.
"""

gather_current_ipam_data = True

if gather_current_ipam_data:
    # Call IPAM data and Write to .pkl file.
    ip_data = IpamGetsToWrite()
#    ip_data.get_extensible_attributes()
    ip_data.get_extensible_attributes_list_values()
#    ip_data.get_network_views()
#    ip_data.get_networks()
#    ip_data.get_networkcontainers()

