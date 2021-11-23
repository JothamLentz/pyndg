#!/usr/bin/env python
#  -*- coding: utf-8 -*-
#"""write cdp neighbor info into a network notepad diagram.
#
# Start by grabbing from csv file created with cdp_aggregator
#
#    Standard folder is c:\users\<user>\Cisco-CLI-Analyzer_Session_Logs\neighbors
#
#"""
# REWRITE input format to use Batfish link file format
# REWRITING to use pyndg class instead of too many Regex in progress JCL

import csv
import os
import easygui
import shutil
import pyndg as pyndg
from CLI_Analyzer.devices import getMgmtIP # find IP used by cisco cli analyzer to manage device

home = os.path.expanduser("~")
defaultPath = os.path.join(home, 'Cisco-CLI-Analyzer_Session_Logs/neighbors/*.csv')
csvFilePath = easygui.fileopenbox(msg='CSV neighbor file',
                             title='CSV Dir',
                             default= defaultPath,
                             filetypes=['*.csv'])
# mapDir = os.path.abspath('C:/Users/joe/Documents/NetworkNotepadDiagrams')
# mapFile = os.path.join(mapDir, 'cdp_mapper_L2.ndg')  # TODO prompt for this
# if not os.path.exists(mapFile):
#     shutil.copy(os.path.join(mapDir, 'Templates/_Template_.ndg'), mapFile)
mapFilePath = easygui.fileopenbox(msg='Network Notepad Diagram File',
                                  title='Map File',
                                  default=home,
                                  filetypes=['*.ndg'])

ndg = pyndg.NetworkNotepad(mapFilePath)
pages = ndg.get_pages()
p = pages['L2']

with open(csvFilePath, 'r') as csvfile:
    linksreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in linksreader:
        devices = [cell.split(';')[0] for cell in row]
        print(f'devices: {devices}')
        ports = [cell.split(';')[1] for cell in row]
        print(f'ports: {ports}')
        mgmtA = getMgmtIP(devices[0])
        mgmtB = getMgmtIP(devices[1])
    # check if both seen devices exist in map file and if not add them
        objectA_num = ndg.page[p].get_object_by_name(name=devices[0])
        if not objectA_num:
            objectA_num = ndg.page[p].add_object(name=devices[0], ip=mgmtA, Type='switch')
        objectB_num = ndg.page[p].get_object_by_name(name=devices[1])
        if not objectB_num:
            objectB_num = ndg.page[p].add_object(name=devices[1], ip=mgmtB, Type='switch')

        # check if link exists either direction, if not create it
        link_num = ndg.page[p].get_link(objectA_num, objectB_num)
        print(ndg.page[p].Link_Table.loc[link_num])
        if not link_num:
            link_num = ndg.page[p].add_link(Obj1=objectA_num,
                                            Obj2=objectB_num,
                                            name1=ports[0].replace(" ", ""),
                                            name2=ports[1].replace(" ", ""))
ndg.write()