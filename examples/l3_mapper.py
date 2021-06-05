# !/usr/bin/env python
#  -*- coding: utf-8 -*-
# """Grab All L3_Interfaces from config files in a folder and add them to a Network Notepad Diagram
#
#    Standard folder is c:\users\<user>\Cisco-CLI-Analyzer_Session_Logs
#
# """


from ciscoconfparse import CiscoConfParse  #
from ciscoconfparse.ccp_util import IPv4Obj  # http://www.pennington.net/py/ciscoconfparse/api_ccp_util.html#ccp_util.IPv4Obj
import os
import shutil
import re
import sys
import easygui
import pyndg as pyndg
# from CLI_Analyzer.devices import getMgmtIP

# TODO set layers for all objects: hosts1, networks1, links3. (almost done)
# TODO add hyperlink to Network Notepad file format
# TODO Get X, Y for host object and place network like 200 below it when adding new network.
# TODO define Link styles more appropriate for L3 in template.  Mgmt, Routing, VPN
# TODO look into python regex verbose, python reg script?
# TODO when adding Networks check if interface begins with Vlan.  If yes place in name. Else just use subnet:description
# TODO  above is predicated on checking address entry of network, NOT name
# TODO modify create date when copying template
# TODO Check running config for routing protocols, bgp neighbors, OSPF areas, EIGRP AS, etc


if __name__ == "__main__":
    home = os.path.expanduser("~")
    # get folders
    cfgDir = easygui.diropenbox(msg="Configuration Folder", title="Browse to desired config folder", default=home)
    mapDir = easygui.diropenbox(msg="Map Folder", title="Browse to desired map folder", default=home)
    os.chdir(cfgDir)
    configFiles = [fileName for fileName in os.listdir(cfgDir) if fileName.startswith("running-config") & fileName.endswith(".txt")]

    for cfgFile in configFiles:

        l3_intfs = {}

        # create CiscoConfParse object
        confparse = CiscoConfParse(cfgFile)

        if confparse.has_line_with(r'domain.name'):
            domain_Name_cmd = confparse.find_objects(r"^ip domain.name .*|^domain-name .*")  # gets ASAs also
            *command, domainName = str.split(domain_Name_cmd[0].text)
            domainName = str.lower(domainName)
        else:
            domainName = "noDomain"

        mapFile = os.path.join(mapDir, domainName + '.ndg')

        if confparse.has_line_with(r'hostname'):
            hostName_cmd = confparse.find_objects(r"^hostname|^switchname")
            *command, hostName = str.split(hostName_cmd[0].text)
            # hostName = str.lower(hostName)
        else:
            hostName = "noHostname"

        # get all interface commands from the configuration
        # [0-9] to avoid "ip address dhcp"
        l3_intf_cmds = confparse.find_objects_w_child(parentspec=r"^interface ", childspec=r"^\s+ip address [0-9]")
        no_shut_intf_cmds = confparse.find_objects_wo_child(parentspec=r"^interface ", childspec=r"^\sshutdown$")
        up_l3_intf_cmds = list(set(l3_intf_cmds).intersection(no_shut_intf_cmds))
        print(f'found {len(up_l3_intf_cmds)} up L3 interfaces')
        if len(up_l3_intf_cmds) == 1:
            objectType = 'switch'
        else:
            objectType = 'routerc1'

        # iterate over the resulting IOSCfgLine objects
        for interface_cmd in up_l3_intf_cmds:
            # get the interface name (remove the interface command from the configuration line)
            intf_name = interface_cmd.text[len("interface "):]
            l3_intfs[intf_name] = {}

            # search for the description command, if not set use "NOT SET" as value
            l3_intfs[intf_name]["description"] = "NOT SET"
            for cmd in interface_cmd.re_search_children(r"^\s+description "):
                l3_intfs[intf_name]["description"] = cmd.text.strip()[len("description "):]

            # extract IP addresses if defined
            # IOS: ip address 10.0.255.5 255.255.255.0
            # NEXUS:   ip address 10.0.255.27/29
            # This horrendous regex matches either format hope I don't need to add another format
            IPv4_REGEX = r"ip\saddress\s((?:(?:[0-9]{1,3}\.){3}[0-9]{1,3}\s(?:[0-9]{1,3}\.){3}[0-9]{1,3})|(?:(?:[0-9]{1,3}\.){3}[0-9]{1,3}\/[0-9]{1,2}))"
            for cmd in interface_cmd.re_search_children(IPv4_REGEX):
                ipv4_addr = interface_cmd.re_match_iter_typed(IPv4_REGEX, result_type=IPv4Obj)
                l3_intfs[intf_name].update({
                    "ipv4": ipv4_addr
                })

        if not os.path.exists(mapFile):
            shutil.copy(os.path.join(mapDir, 'Templates\\_Template.ndg'), mapFile)
            # TODO set original date in copied template file

        print(f'map file: {mapFile}')
        ndg = pyndg.NetworkNotepad(mapFile)
        pages = ndg.get_pages()
        p = pages['L3']

        # this only works if the title in the template is label number 3
        if ndg.page[p].labels.loc[3, "Text"] == 'Title':
            ndg.page[p].labels.at[3, "Text"] = domainName

        host_object_num = ndg.page[p].get_object_by_name(hostName)
        if not host_object_num:
            # Use last interface name alphabetically as management IP, correct manually if wrong
            mgmtInt = sorted(l3_intfs.keys(), reverse=True)[0]
            mgmtIP = l3_intfs[mgmtInt]['ipv4'].ip
            print(l3_intfs)
            print(mgmtIP)
            host_object_num = ndg.page[p].add_object(name=hostName,
                                                     ip=mgmtIP,
                                                     Type=objectType)

        for intf in l3_intfs:
            if l3_intfs[intf]['ipv4'].prefixlen != 32:
                if l3_intfs[intf]['ipv4'].prefixlen > 28:
                    net_type = "L3_Transit_int"
                else:
                    net_type = "cloud5"
                network = str(l3_intfs[intf]['ipv4'].network)
                # check if there is already a network object created
                net_object_num = ndg.page[p].get_object_by_ip(network)
                if not net_object_num:
                    net_object_num = ndg.page[p].add_object(name='Network', ip=network, Type=net_type, Y=750)

                link_num = ndg.page[p].get_link(host_object_num, net_object_num)
                if not link_num:
                    ndg.page[p].add_link(Obj1=host_object_num,
                                         Obj2=net_object_num,
                                         name1=intf,
                                         ip1=l3_intfs[intf]["ipv4"].ip,
                                         Comment1=l3_intfs[intf]["description"],
                                         name2="",
                                         ip2="")

        ndg.write()
