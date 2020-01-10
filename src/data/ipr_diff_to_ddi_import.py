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
import os
import time
import json
import pickle
import csv
import socket
import struct
import re
import logging
from xlrd import open_workbook
import requests
from dotenv import find_dotenv, load_dotenv
from builder import DataFileNames, DirectoryValues
from builder import Writer, Reader
from agency_vrf_view_libs import ReadLibraries


def cidr_to_netmask(cidr):
    """
    Function that takes a two digit network mask and converts to a subnet mask.

    Return Value:
        -- netmask
    """
    net_bits = cidr
    host_bits = 32 - int(net_bits)
    netmask = socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))
    return netmask


def _write_output_for_add_csv(data, file):
    """
    This function writes out a .csv file for an import type: add.
    """
    ea_index = _get_ea_index()
    with open(file, 'w', encoding='utf-8', newline='') as csvfile:
        file_write = csv.writer(csvfile, delimiter='\t')
        for stuff in data:
            if 'networkcontainer' in stuff:
                # Initial Row fields built
                if stuff[16] == 'DDI':
                    stuff[16] = ''
                temp_data = [stuff[14],
                             stuff[1].split('/')[0],
                             stuff[1].split('/')[1],
                             stuff[15]]
                temp_header = ['header-networkcontainer',
                               'address*',
                               'netmask*',
                               'network_view']
                # Check for comments
                if stuff[12]:
                    if '\n' in stuff[12]:
                        temp_data.append(
                            stuff[12].replace('\n', ',').strip(','))
                        temp_header.append('comment')
                    else:
                        temp_data.append(stuff[12])
                        temp_header.append('comment')
                # Check for EA's
                for key in ea_index.keys():
                    if key in ['Datacenter', 'IPR Designation'] and \
                            ',' in stuff[ea_index[key]]:
                        items = stuff[ea_index[key]].split(',')
                        for item in items:
                            temp_header.append('EA-'+key)
                            temp_header.append('EAInherited-'+key)
                            temp_data.append(item.strip())
                            temp_data.append('OVERRIDE')
                        continue
                    if stuff[ea_index[key]]:
                        temp_header.append('EA-'+key)
                        temp_header.append('EAInherited-'+key)
                        temp_data.append(stuff[ea_index[key]].strip())
                        temp_data.append('OVERRIDE')
                # Write Header Row on new line.
                file_write.writerow(temp_header)
                # Write data Row on new line.
                file_write.writerow(temp_data)
            if 'network' in stuff:
                # Initial Row fields built
                if stuff[16] == 'DDI':
                    stuff[16] = ''
                temp_data = [stuff[14],
                             stuff[1].split('/')[0],
                             cidr_to_netmask(stuff[1].
                                             split('/')[1]),
                             stuff[15]]
                temp_header = ['header-network',
                               'address*',
                               'netmask*',
                               'network_view']
                # Check for comments
                if stuff[12]:
                    if '\n' in stuff[12]:
                        temp_data.append(stuff[12].replace('\n', ',').strip(','))
                        temp_header.append('comment')
                    else:
                        temp_data.append(stuff[12])
                        temp_header.append('comment')
                # Check for EA's
                for key in ea_index.keys():
                    if key in ['Datacenter', 'IPR Designation'] and \
                                    ',' in stuff[ea_index[key]]:
                        items = stuff[ea_index[key]].split(',')
                        for item in items:
                            temp_header.append('EA-'+key)
                            temp_header.append('EAInherited-'+key)
                            temp_data.append(item.strip())
                            temp_data.append('OVERRIDE')
                        continue
                    if stuff[ea_index[key]]:
                        temp_header.append('EA-'+key)
                        temp_header.append('EAInherited-'+key)
                        temp_data.append(stuff[ea_index[key]])
                        temp_data.append('OVERRIDE')
                # Write Header Row on new line.
                file_write.writerow(temp_header)
                # Write data Row on new line.
                file_write.writerow(temp_data)


def _write_output_for_merge_csv(data, file):
    """
    This function writes out a .csv file for an import type: merge.
    """
    with open(file, 'w', encoding='utf-8', newline='') as csvfile:
        file_write = csv.writer(csvfile, delimiter='\t')
        for stuff in data:
            if 'network' in stuff:
                for item in stuff[3].keys():
                    if item == 'comment':
                        file_write.writerow(['header-network',
                                             'address*',
                                             'netmask*',
                                             'network_view',
                                             'comment'])
                        file_write.writerow([stuff[2],
                                             stuff[1].split('/')[0],
                                             cidr_to_netmask(stuff[1].
                                                             split('/')[1]),
                                             stuff[0],
                                             stuff[3]['comment']])
                    if item != 'comment':
                        file_write.writerow(['header-network',
                                             'address*',
                                             'netmask*',
                                             'network_view',
                                             'EA-' + item,
                                             'EAInherited-' + item])
                        file_write.writerow([stuff[2],
                                             stuff[1].split('/')[0],
                                             cidr_to_netmask(stuff[1].
                                                             split('/')[1]),
                                             stuff[0],
                                             stuff[3][item],
                                             'OVERRIDE'])
            if 'networkcontainer' in stuff:
                for item in stuff[3].keys():
                    if item == 'comment':
                        file_write.writerow(['header-networkcontainer',
                                             'address*',
                                             'netmask*',
                                             'network_view',
                                             'comment'])
                        file_write.writerow([stuff[2],
                                             stuff[1].split('/')[0],
                                             stuff[1].split('/')[1],
                                             stuff[0],
                                             stuff[3]['comment']])
                    if item != 'comment':
                        file_write.writerow(['header-networkcontainer',
                                             'address*',
                                             'netmask*',
                                             'network_view',
                                             'EA-' + item,
                                             'EAInherited-' + item])
                        file_write.writerow([stuff[2],
                                             stuff[1].split('/')[0],
                                             stuff[1].split('/')[1],
                                             stuff[0],
                                             stuff[3][item],
                                             'OVERRIDE'])


def _write_output_for_merge_disposition_csv(data, file):
    """
    This function writes out a .csv file for an import type: merge.
    """
    with open(file, 'w', encoding='utf-8', newline='') as csvfile:
        file_write = csv.writer(csvfile, delimiter='\t')
        for stuff in data:
            if 'network' in stuff:
                file_write.writerow(['header-network',
                                     'address*',
                                     'netmask*',
                                     'network_view',
                                     'EA-IPR Designation',
                                     'EAInherited-IPR Designation'])
                file_write.writerow([stuff[2],
                                     stuff[1].split('/')[0],
                                     cidr_to_netmask(stuff[1].
                                                     split('/')[1]),
                                     stuff[0],
                                     stuff[3],
                                     'OVERRIDE'])
            if 'networkcontainer' in stuff:
                file_write.writerow(['header-networkcontainer',
                                     'address*',
                                     'netmask*',
                                     'network_view',
                                     'EA-IPR Designation',
                                     'EAInherited-IPR Designation'])
                file_write.writerow([stuff[2],
                                     stuff[1].split('/')[0],
                                     stuff[1].split('/')[1],
                                     stuff[0],
                                     stuff[3],
                                     'OVERRIDE'])


def _write_output_for_delete_csv(data, file):
    """
    This function writes out a .csv file for an import type: delete.
    """
    with open(file, 'w', encoding='utf-8', newline='') as csvfile:
        file_write = csv.writer(csvfile, delimiter='\t')
        for stuff in data:
            if 'network' in stuff:
                file_write.writerow(['header-network',
                                     'address*',
                                     'netmask*',
                                     'network_view'])
                file_write.writerow([stuff[2],
                                     stuff[1].split('/')[0],
                                     cidr_to_netmask(stuff[1].
                                                     split('/')[1]),
                                     stuff[0]])
            if 'networkcontainer' in stuff:
                file_write.writerow(['header-networkcontainer',
                                     'address*',
                                     'netmask*',
                                     'network_view'])
                file_write.writerow([stuff[2],
                                     stuff[1].split('/')[0],
                                     stuff[1].split('/')[1],
                                     stuff[0]])


def _write_output_for_override_csv(data, file):
    """
    This function writes out a csv file for an import type: override.
    """
    ea_index = _get_ea_index()
    with open(file, 'w', encoding='utf-8', newline='') as csvfile:
        file_write = csv.writer(csvfile, delimiter='\t')
        for stuff in data:
            if 'network' in stuff:
                for item in stuff[3].keys():
                    if item == 'comment':
                        file_write.writerow(['header-network',
                                             'address*',
                                             'netmask*',
                                             'network_view',
                                             'comment'])
                        file_write.writerow([stuff[2],
                                             stuff[1].split('/')[0],
                                             cidr_to_netmask(stuff[1].
                                                             split('/')[1]),
                                             stuff[0],
                                             stuff[3]['comment']])
                    if item != 'comment':
                        if item in ['Datacenter', 'IPR Designation'] and \
                                        ',' in stuff[3][item]:
                            temp_data = [stuff[2],
                                         stuff[1].split('/')[0],
                                         cidr_to_netmask(stuff[1].
                                                         split('/')[1]),
                                         stuff[0]]
                            temp_header = ['header-network',
                                           'address*',
                                           'netmask*',
                                           'network_view']
                            items = stuff[3][item].split(',')
                            for it in items:
                                temp_header.append('EA-' + item)
                                temp_header.append('EAInherited-' + item)
                                temp_data.append(it.strip())
                                temp_data.append('OVERRIDE')
                            # Write Header Row on new line.
                            file_write.writerow(temp_header)
                            # Write data Row on new line.
                            file_write.writerow(temp_data)
                        else:
                            file_write.writerow(['header-network',
                                                 'address*',
                                                 'netmask*',
                                                 'network_view',
                                                 'EA-' + item,
                                                 'EAInherited-' + item])
                            file_write.writerow([stuff[2],
                                                 stuff[1].split('/')[0],
                                                 cidr_to_netmask(stuff[1].
                                                                 split('/')[1]),
                                                 stuff[0],
                                                 stuff[3][item],
                                                 'OVERRIDE'])
            if 'networkcontainer' in stuff:
                for item in stuff[3].keys():
                    if item == 'comment':
                        file_write.writerow(['header-networkcontainer',
                                             'address*',
                                             'netmask*',
                                             'network_view',
                                             'comment'])
                        file_write.writerow([stuff[2],
                                             stuff[1].split('/')[0],
                                             stuff[1].split('/')[1],
                                             stuff[0],
                                             stuff[3]['comment']])
                    if item != 'comment':
                        if item in ['Datacenter', 'IPR Designation'] and \
                                        ',' in stuff[3][item]:
                            temp_data = [stuff[2],
                                         stuff[1].split('/')[0],
                                         stuff[1].split('/')[1],
                                         stuff[0]]
                            temp_header = ['header-networkcontainer',
                                           'address*',
                                           'netmask*',
                                           'network_view']
                            items = stuff[3][item].split(',')
                            for it in items:
                                temp_header.append('EA-' + item)
                                temp_header.append('EAInherited-' + item)
                                temp_data.append(it.strip())
                                temp_data.append('OVERRIDE')
                            # Write Header Row on new line.
                            file_write.writerow(temp_header)
                            # Write data Row on new line.
                            file_write.writerow(temp_data)
                        else:
                            file_write.writerow(['header-networkcontainer',
                                                 'address*',
                                                 'netmask*',
                                                 'network_view',
                                                 'EA-' + item,
                                                 'EAInherited-' + item])
                            file_write.writerow([stuff[2],
                                                 stuff[1].split('/')[0],
                                                 stuff[1].split('/')[1],
                                                 stuff[0],
                                                 stuff[3][item],
                                                 'OVERRIDE'])


def _write_output_for_override_blanks_csv(data, file):
    """
    This function writes out a csv file for an import type: override.
    """
    with open(file, 'w', encoding='utf-8', newline='') as csvfile:
        file_write = csv.writer(csvfile, delimiter='\t')
        for stuff in data:
            if 'network' in stuff:
                for item in stuff[3].keys():
                    if item == 'comment':
                        file_write.writerow(['header-network',
                                             'address*',
                                             'netmask*',
                                             'comment',
                                             'network_view'])
                        file_write.writerow([stuff[2],
                                             stuff[1].split('/')[0],
                                             cidr_to_netmask(stuff[1].
                                                             split('/')[1]),
                                             stuff[3]['comment'],
                                             stuff[0]])
                    if item != 'comment':
                        file_write.writerow(['header-network',
                                             'address*',
                                             'netmask*',
                                             'EA-' + item,
                                             'EAInherited-' + item,
                                             'network_view'])
                        file_write.writerow([stuff[2],
                                             stuff[1].split('/')[0],
                                             cidr_to_netmask(stuff[1].
                                                             split('/')[1]),
                                             stuff[3][item],
                                             'OVERRIDE',
                                             stuff[0]])
            if 'networkcontainer' in stuff:
                for item in stuff[3].keys():
                    if item == 'comment':
                        file_write.writerow(['header-networkcontainer',
                                             'address*',
                                             'netmask*',
                                             'comment',
                                             'network_view'])
                        file_write.writerow([stuff[2],
                                             stuff[1].split('/')[0],
                                             stuff[1].split('/')[1],
                                             stuff[3]['comment'],
                                             stuff[0]])
                    if item != 'comment':
                        file_write.writerow(['header-networkcontainer',
                                             'address*',
                                             'netmask*',
                                             'EA-' + item,
                                             'EAInherited-' + item,
                                             'network_view'])
                        file_write.writerow([stuff[2],
                                             stuff[1].split('/')[0],
                                             stuff[1].split('/')[1],
                                             stuff[3][item],
                                             'OVERRIDE',
                                             stuff[0]])


def _get_view_index(views, ddi_data):
    """
    Takes a compiled list of views and assigns an index in a dictionary as
    indexed by the list of ddi data returned.
    """
    views_index_temp = {}
    for view in views:
        for enum, ddi_line in enumerate(ddi_data):
            if view == ddi_line[0]['network_view']:
                temp_dict = {view: enum}
                views_index_temp.update(temp_dict)
    return views_index_temp


def _get_ea_index():
    """
    Manually build index table for the ea att's.  The index number is
    the value associated to the ea from the update data.  If an EA has been
    renamed in IB.  An update will be required here. If an EA has had its name
    added to Master an update will be required here. Final output is a dict.
    """
    ea_index_temp = {'Address': 5, 'Agency': 10, 'City': 4, 'Country': 3,
                     'Datacenter': 7, 'Division': 8, 'Interface Name': 13,
                     'Region_List': 2, 'Requester Email': 9, 'Site': 6,
                     'VLAN Description': 11, 'IPR Designation': 16}
    return ea_index_temp


def _get_rekey_ddi_data(ddi_data):
    """
    Takes a list of lists of dict's and converts to a list of dict's, of
    dicts.  As well as rekey's the dict's with the network address.
    """
    for enum, item in enumerate(ddi_data):
        ddi_data[enum] = dict((d['network'],
                               dict(d, index=index))
                              for (index, d) in enumerate(item))
    return ddi_data


def _get_ea_listed_values(ea_raw_data):
    """Parses raw ipam data and returns the values in listed format."""
    ea_list_values_dict = {}
    for ea in ea_raw_data:
        if ea['type'] == 'ENUM' and ea['name'] in \
                ['Datacenter', 'IPR Designation']:
            ea_list_values_dict[ea['name']] = []
            for list_value in ea['list_values']:
                ea_list_values_dict[ea['name']].append(list_value['value'])
    return ea_list_values_dict


def _get_diff_data(views_index, src_data, ea_index, ddi_data, ddi_views):
    """
    This function creates two separate dict's for overlap or merge imports
    based on how DDI handles imports.

    Output List Format:
        -- Ex_List = ['Network_View', 'Network', 'DDI_Type', Dict]
    Return Arguments:
        -- import_merge - data set to go through a merge import process.
        -- import_delete - data set to go through a delete import process.
        -- import_override - data set to go through an override import
        -- import_override_to_blank - data set to go through an override import
    """

    def _add_and_del():
        """Handles the add's and del import's."""
        del_list = ['del']
        for add_or_del_row in src_data:
            # Add Check.
            if 'add' in add_or_del_row[0]:
                if add_or_del_row[15] in ddi_views and \
                                add_or_del_row[15] not in views_index:
                    import_add.append(add_or_del_row)
                    continue
                if add_or_del_row[1] in \
                        ddi_data[views_index[add_or_del_row[15]]]:
                    add_or_del_row[16] = 'Found in ipam database.'
                    errored_list.append(add_or_del_row)
                    continue
                else:
                    import_add.append(add_or_del_row)
                    continue

            # delete check
            if add_or_del_row[0] in del_list and add_or_del_row[1] in \
                    ddi_data[views_index[add_or_del_row[15]]]:
                import_delete.append([add_or_del_row[15],
                                      add_or_del_row[1],
                                      add_or_del_row[14]])
                continue
            elif add_or_del_row[0] in del_list and add_or_del_row[1] not in \
                    ddi_data[views_index[add_or_del_row[15]]]:
                add_or_del_row[16] = 'Missing network in ipam db.'
                errored_list.append(add_or_del_row)
                continue
            unused_list.append(add_or_del_row)
        if errored_list:
            write.write_to_csv_w(dir_cls.reports_dir(),
                                 filenames_cls.
                                 errored_import_add_and_del_configs(),
                                 errored_list)

    def _ea_in_disposition_col0_and_empty_ipr_d_col():
        """Disposition col0 check and an empty ipr disposition column."""
        for disposition_row in unused_list:
            # Check disposition
            ddi_index = views_index[disposition_row[15]]
            # Checks disposition column value and checks for IPR D value.
            # If no IPR D in extattrs dict stores the src data for updates.
            if disposition_row[1] not in ddi_data[ddi_index]:
                continue
            if disposition_row[0] in ea_listed_values['IPR Designation'] and \
                    'IPR Designation' not in \
                    ddi_data[ddi_index][disposition_row[1]]['extattrs']:
                import_merge_disposition.append(
                    [disposition_row[15],
                     disposition_row[1],
                     disposition_row[14],
                     disposition_row[0]])

    def _comment_check():
        """Function for checking ipam comment attribute."""
        for comment_row in unused_list:
            ddi_index = views_index[comment_row[15]]
            # Checks for empty src value and empty ddi data value.
            # Continues if True.
            if comment_row[1] not in ddi_data[ddi_index]:
                continue
            if 'comment' not in ddi_data[ddi_index][comment_row[1]]\
                    and comment_row[12] == '':
                continue
            # Checks a non-empty src value and updates if an
            # empty ddi data value.
            if 'comment' not in ddi_data[ddi_index][comment_row[1]] and \
                    comment_row[12] != '':
                import_merge.append([comment_row[15],
                                     comment_row[1],
                                     comment_row[14],
                                     {'comment': comment_row[12]}])
                continue
            # Checks diff against src value and a populated value in the
            # ddi data and replaces with src value.
            if comment_row[12] != \
                    ddi_data[ddi_index][comment_row[1]]['comment']:
                import_override.append([comment_row[15],
                                        comment_row[1],
                                        comment_row[14],
                                        {'comment': comment_row[12]}])
                continue

    def _non_listed_ea_columns_check():
        """Checks non-listable ea columns."""
        for ea_row in unused_list:
            # dup Check in disposition
            ddi_index = views_index[ea_row[15]]
            for key, value in ea_index.items():
                # ea attributes that could be listed.
                if ea_row[1] not in ddi_data[ddi_index]:
                    continue
                if key == 'Datacenter' or key == 'IPR Designation':
                    continue
                # Checks for empty src value and empty ddi data value.
                # Continues if True.
                if key not in ddi_data[ddi_index][ea_row[1]]['extattrs'] and \
                        ea_row[value] in ['', 'DDI']:
                    continue
                # Checks a non-empty src value and updates if an
                # empty ddi data value.
                if key not in ddi_data[ddi_index][ea_row[1]]['extattrs'] \
                        and ea_row[value] not in ['', 'DDI']:
                    import_merge.append([ea_row[15],
                                         ea_row[1],
                                         ea_row[14],
                                         {key: ea_row[value]}])
                    continue
                # Checks diff against src value and a populated value in the
                # ddi data and replaces with src value.
                if ea_row[value] != \
                        ddi_data[ddi_index][
                            ea_row[1]]['extattrs'][key]['value']:
                    import_override.append([ea_row[15],
                                            ea_row[1],
                                            ea_row[14],
                                            {key: ea_row[value]}])
                    continue

    def _listed_ea_column_check():
        """Checks non-listable ea columns."""

        def diff(li1, li2):
            return list(set(li1) - set(li2))

        for ea_row in unused_list:
            ddi_index = views_index[ea_row[15]]
            # This check is performed in
            # _ea_in_disposition_col0_and_empty_ipr_d_col
            if ea_row[1] not in ddi_data[ddi_index]:
                continue
            if ea_row[0] in ea_listed_values['IPR Designation'] and \
                    'IPR Designation' not in \
                    ddi_data[ddi_index][ea_row[1]]['extattrs']:
                continue
            # Processing listable columns.
            for key, value in ea_index.items():
                # Skip's unused keys.
                if key not in ['Datacenter', 'IPR Designation']:
                    continue
                # Check for blank column and blank source column.
                if key not in ddi_data[ddi_index][ea_row[1]]['extattrs'] and \
                        ea_row[value] in ['', 'DDI']:
                    continue
                # Check Disposition col, check for comma not in IPR D col
                # value, check value in IPR D col to ea ipr d attribute list,
                # check IPR D col value eq ddi value.
                # On not listed IPR D values.
                if key in ea_listed_values:
                    ipr_temp_list = []
                    ipam_temp_list = []
                    # Building list for diff's against DDI data.
                    if ea_row[0] in ea_listed_values[key]:
                        ipr_temp_list.append(ea_row[0])
                    # Extend list if listed values in IPR D column.
                    if ',' in ea_row[ea_index[key]]:
                        ipr_temp_list.extend([x.strip()
                                              for x in ea_row[ea_index[key]].
                                              split(',')
                                              if x.strip() in
                                              ea_listed_values[key]])
                    # Append list if non-listed values in IPR D column.
                    if ',' not in ea_row[ea_index[key]] and \
                            ea_row[ea_index[key]] in \
                            ea_listed_values[key]:
                        ipr_temp_list.append(ea_row[ea_index[key]])
                    # Remove blank elements from list.
                    ipr_temp_list = [x for x in ipr_temp_list if x]

                    # Building DDI list for diff against the IPR D Columns
                    if isinstance(ddi_data[ddi_index][
                                      ea_row[1]]['extattrs'][
                                          key]['value'], list):
                        ipam_temp_list.extend(ddi_data[ddi_index][
                                                  ea_row[1]]['extattrs'][
                                                  key]['value'])
                    else:
                        ipam_temp_list.append(ddi_data[ddi_index][
                                                  ea_row[1]]['extattrs'][
                                                  key]['value'])
                    # Check for diff between listed sets.
                    in_ipam_not_ipr = diff(ipam_temp_list, ipr_temp_list)
                    in_ipr_not_ipam = diff(ipr_temp_list, ipam_temp_list)
                    if in_ipam_not_ipr or in_ipr_not_ipam:
                        if len(ipr_temp_list) > 1:
                            import_override.append([ea_row[15].strip(),
                                                    ea_row[1].strip(),
                                                    ea_row[14].strip(),
                                                    {key: ','.join(
                                                        ipr_temp_list)}])
                        else:
                            import_override.append([ea_row[15].strip(),
                                                    ea_row[1].strip(),
                                                    ea_row[14].strip(),
                                                    {key: ipr_temp_list[0]}])
                        continue

    # Local scope variables.
    import_add = []
    import_delete = []
    import_merge = []
    import_override = []
    import_merge_disposition = []
    unused_list = []
    errored_list = []
    # EA Listed (ENUM) attribute values.
    ea_listed_values_raw = reader_cls.\
        read_from_pkl(dir_cls.raw_dir(),
                      filenames_cls.
                      extensible_attributes_list_values_filename())
    ea_listed_values = _get_ea_listed_values(ea_listed_values_raw)
    _add_and_del()
    _ea_in_disposition_col0_and_empty_ipr_d_col()
    _comment_check()
    _non_listed_ea_columns_check()
    _listed_ea_column_check()
    return import_add, \
        import_delete, \
        import_merge_disposition, \
        import_merge, \
        import_override


def api_call_network_views(view, logger):
    """
    DDI api call for networks within the 'view' value .  Returns the utf-8
    decoded with a json load.

        Return Variables:
        -- none
    """
    trynetwork = 3
    rnet = None
    for iview in range(trynetwork):
        try:
            rnet = requests.get(PAYLOAD['url'] + "network?_return_fields="
                                                 "extattrs,comment,network,"
                                                 "network_view,utilization&"
                                                 "network_view=" + view,
                                "_max_results=-5000",
                                auth=(PAYLOAD['username'],
                                      PAYLOAD['password']),
                                verify=False)
            break
        except requests.exceptions.ConnectionError as nerrt:
            if iview < trynetwork - 1:
                logger.warning('Container View Retry #%s ,$%s', view, iview)
                time.sleep(5)
                continue
            else:
                logger.info('Timeout Error for container view: %s, %s, %s',
                            view, iview, nerrt)
                return []
    return json.loads(rnet.content.decode('utf-8'))


def api_call_networkcontainer_views(view, logger):
    """
    DDI api call for network containers within the 'view' value.  Returns
    the utf-8 decoded with a json load.

        Return Variables:
        -- none
    """
    trynetworkview = 3
    rnetcont = None
    for inview in range(trynetworkview):
        try:
            rnetcont = requests.get(PAYLOAD['url'] + "networkcontainer?"
                                                     "_return_fields=extattrs,"
                                                     "comment,utilization,"
                                                     "network,network_view"
                                                     "&network_view=" +
                                    view, "_max_results=-5000",
                                    auth=(PAYLOAD['username'],
                                          PAYLOAD['password']),
                                    verify=False)
            break
        except requests.exceptions.ConnectionError as cerrt:
            if inview < trynetworkview - 1:
                logger.warning('Container View Retry #%s ,$%s', view, inview)
                time.sleep(5)
                continue
            else:
                logger.info('Timeout Error for container view: %s, %s, %s',
                            view, inview, cerrt)
                return []
    return json.loads(rnetcont.content.decode('utf-8'))


def get_ea_attributes(path, logger):
    """
    Queries DDI for the Extensible Attributes and then extracts the data.
    Also the first attempt at connecting to IPAM.  Built in some error
    checking to report on status of connectivity.

        Output Data:
        -- ea_data.pkl
    """
    reattrib = None
    try:
        reattrib = requests.get(PAYLOAD['url'] + "extensibleattributedef?",
                                auth=(PAYLOAD['username'],
                                      PAYLOAD['password']),
                                verify=False)
        reattrib.raise_for_status()
    except requests.exceptions.ConnectionError as eaerrt:
        logger.error("Can't reach IPAM! Check your VPN or Local Access, %s",
                     eaerrt)
        exit()
    except requests.exceptions.HTTPError as eahrrt:
        logger.error("Check your credentials! %s", eahrrt)
        exit()

    rutfeattrib = reattrib.content.decode('utf-8')
    rjsoneattrib = json.loads(rutfeattrib)
    eattl = []
    for att in rjsoneattrib:
        for key, value in att.items():
            if key == 'name':
                eattl.append(value)
    eattl.sort()
    pickle.dump(eattl, open(path, "wb"))


def get_ddi_ip_data(net_views, ea_path, ddi_path, logger):
    """
    Takes in the following arguments and queries IPAM by each network view.

        Output:
        ddi_data.pkl
    """
    # Pull down fresh copy of ea-att's
    logger.info("Getting EA Attributes from DDI.")
    get_ea_attributes(ea_path, logger)

    # Pull down fresh copy of view data
    ddi_data = []
    for view in net_views:
        if not view:
            continue
        logger.info("Getting data for view: %s", view)
        ddijsonnet = api_call_network_views(view, logger)
        ddijsonnetcont = api_call_networkcontainer_views(view, logger)
        if isinstance(ddijsonnet, dict) and isinstance(ddijsonnetcont, dict):
            continue
        if ddijsonnet and ddijsonnetcont:
            ddijson = ddijsonnet + ddijsonnetcont
            ddi_data.append(ddijson)
        elif ddijsonnet:
            ddi_data.append(ddijsonnet)
        elif ddijsonnetcont:
            ddi_data.append(ddijsonnetcont)
        else:
            continue
    pickle.dump(ddi_data, open(ddi_path, "wb"))
    logger.info('Change func needddiapicall to False to build import sheets.')
    exit()


def _get_ddi_views():
    ddi_views = []
    raw_ddi_views = reader_cls.read_from_pkl(dir_cls.raw_dir(),
                                             filenames_cls.
                                             network_views_filename())
    for ddi_dict in raw_ddi_views:
        ddi_views.append(ddi_dict['name'])
    return ddi_views


def _get_views(data_lists):
    """Builds a set list of views from within src_ws"""
    views = []
    for data_list in data_lists:
        views.append(data_list[15])
    return list(set(views))


def main():
    """
    NEEDS UPDATING!!!
    Doc: This script takes the updates made to the master sheet.  Checks and
        converts the data generated from "ipr_ddi_to_ddi_diff.py" into a
        format that can be used for import into DDI.
    Process:
        1. ddi_api_call: is set to False.  If you need to query DDI for new
            network view data you will need to change this to True.  Once the
            data is stored you can change back to False in order avoid the
            query phase of this script.
        2. The data from DDI will be pulled in for comparison with the diff
            data pulled in.  From here this script will convert the data into
            import format for DDI.
        3. Once data is converted the spreadsheet will be created with data
            updated as needed.
    Output Files:
        -- Merge Import.csv
        -- Override Import.csv
        -- Override to Delete Cells Import.csv
    """
    logger = logging.getLogger('ipr_diff_to_ddi_import.py')
    logger.info('Beginning of Script')
    logger.info('Building Paths and File names')

    # Build Directories
    raw_data_path = os.path.join(PROJECT_DIR, 'data', 'raw')
    processed_data_path = os.path.join(PROJECT_DIR, 'data', 'processed')
    reports_data_path = os.path.join(PROJECT_DIR, 'reports')

    # Build File and File path.
    src_file = os.path.join(processed_data_path,
                            'IP 20190829 20200109 Diff.xlsx')
    ea_data_file = os.path.join(raw_data_path, 'ea_data.pkl')
    ddi_data_file = os.path.join(raw_data_path, 'ddi_data.pkl')
    add_file = os.path.join(reports_data_path, 'Add Import.csv')
    merge_file = os.path.join(reports_data_path, 'Merge Import.csv')
    disposition_file = os.path.join(reports_data_path,
                                    'Merge Disposition Import.csv')
    delete_file = os.path.join(reports_data_path, 'Delete Import.csv')
    override_file = os.path.join(reports_data_path, 'Override Import.csv')

    vrf_to_view = read_lib_cls.read_vrf_to_view()
    agencies = read_lib_cls.read_agency_list()

    logger.info('Loading Data from source file')
    src_wb = open_workbook(src_file)
    src_ws = src_wb.sheet_by_index(0)

    def clean_data(data):
        """Build listed dataset from worksheet."""
        vrf_regex = re.compile(r"((\w{1}\d{3})\-(\d{2})\-(\w{2})\-(\w{2}))")
        src_list = []
        not_properly_built = []
        for row in range(data.nrows):
            # Ignore header row.
            if row == 0:
                continue
            # Ignore blank row.
            cleaning_data = data.row_values(row)
            if cleaning_data[1].strip() == '' and \
                    cleaning_data[15].strip() == '':
                continue
            # Capture lines that do not have a view listed. Sometimes add
            # dispostions do not have a view listed.  This will help populated.
            if cleaning_data[1] and not cleaning_data[15]:
                if cleaning_data[0].lower() == 'add':
                    # Checks vlan desc for vrf.
                    def _find_vrf_in_vlan_desc(find_vrf):
                        # Reference vrf_regex for VRF Regex Expression.
                        finding_vrf = find_vrf[11].split(',')
                        for potential_vrf in finding_vrf:
                            if vrf_regex.match(potential_vrf):
                                return potential_vrf
                    found_vrf = _find_vrf_in_vlan_desc(cleaning_data)
                    if found_vrf in vrf_to_view:
                        cleaning_data[15] = \
                            vrf_to_view[found_vrf]
                    else:
                        cleaning_data[16] = 'VRF Not Found'
                        not_properly_built.append(cleaning_data)
                        continue
                    if cleaning_data[10] and cleaning_data[10] \
                            in agencies:
                        cleaning_data[14] = 'networkcontainer'
                        src_list.append(cleaning_data)
                    else:
                        cleaning_data[10] = ''
                        cleaning_data[14] = 'networkcontainer'
                        src_list.append(cleaning_data)
                    continue
                cleaning_data[16] = 'Missing View.'
                not_properly_built.append(cleaning_data)
                continue
            src_list.append(cleaning_data)

        # Clean's src_list values.
        # Removes errored agencies.
        for enum, row in enumerate(src_list):
            if row[10] in agencies:
                continue
            else:
                src_list[enum][10] = ''
        # Revmoes tab's that may have been incorrectly inserted.
        src_list = [[item.replace('\t', '') for item in row
                     if isinstance(item, str)]
                    for row in src_list]
        src_list = [[item.replace('\n', ', ') for item in row
                     if isinstance(item, str)]
                    for row in src_list]
        src_list = [[item.replace(', ,', ', ') for item in row
                     if isinstance(item, str)]
                    for row in src_list]
        src_list = [[item.strip() for item in row
                     if isinstance(item, str)]
                    for row in src_list]
        for enum, row in enumerate(src_list):
            row[0] = row[0].lower()
            src_list[enum] = row
        return src_list, not_properly_built

    src_data, errored_lines = clean_data(src_ws)
    if errored_lines:
        write.write_to_csv_w(dir_cls.reports_dir(),
                             filenames_cls.errored_import_configs(),
                             errored_lines)

    logger.info('Compiling source file list of views.')
    ddi_views = _get_ddi_views()
    views = _get_views(src_data)

    # Update to True if a fresh set of data is needed from ddi.
    ddi_api_call = False
    if ddi_api_call:
        logger.info('ddi_api_call has been set to True.  Querying DDI.')
        get_ddi_ip_data(views, ea_data_file, ddi_data_file, logger)

    # Open DDI data compiled from ddi_api_call.
    with open(ddi_data_file, 'rb') as file_in:
        ddi_data = pickle.load(file_in)
    # Build data extensions for later processing.
    views_index = _get_view_index(views, ddi_data)
    ddi_data = _get_rekey_ddi_data(ddi_data)
    ea_index = _get_ea_index()

    # Building data sets for in preparation for writing.
    add, delete, disposition, merge, override = \
        _get_diff_data(views_index, src_data, ea_index, ddi_data, ddi_views)

    # Send data off to be written.
    logger.info('Writing Data.  Please refer to the reports dir.')
    if add:
        _write_output_for_add_csv(add, add_file)
    if merge:
        _write_output_for_merge_csv(merge, merge_file)
    if delete:
        _write_output_for_delete_csv(delete, delete_file)
    if override:
        _write_output_for_override_csv(override, override_file)
    if disposition:
        _write_output_for_merge_disposition_csv(disposition, disposition_file)


if __name__ == '__main__':
    # getting root directory
    PROJECT_DIR = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    # setup logger
    LOG_FMT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=LOG_FMT)

    # find .env automatically by walking up directories until it's found
    DOTENV_PATH = find_dotenv()

    # load up the entries as environment variables
    load_dotenv(DOTENV_PATH)

    # PAYLOAD for login to IPAM
    PAYLOAD = {
        'url': os.environ.get("DDI_URL"),
        'username': os.environ.get("DDI_USERNAME"),
        'password': os.environ.get("DDI_PASSWORD")
    }
    write = Writer()
    dir_cls = DirectoryValues()
    filenames_cls = DataFileNames()
    read_lib_cls = ReadLibraries()
    reader_cls = Reader()

    main()
