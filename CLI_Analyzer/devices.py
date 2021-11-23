# !/usr/bin/env python
#  -*- coding: utf-8 -*-
# """Working with Cisco CLI Analyzer device file
#
#
#
# """
import sys
import os
import json


def getMgmtIP(deviceHostname):
    home = os.path.expanduser("~")
    devicesFile = os.path.join(home, '.ciscoSA\\devices.json')
    with open(devicesFile, 'r') as f:
        devicesList = json.load(f)
    ip = ['!']
    for device in devicesList:
        try:
            if device["deviceHostname"] == deviceHostname:
                ip.append(device["hostname"])
        except KeyError:
            pass
            # some devices don't have hostnames set
        except:
            print("Unexpected error:", sys.exc_info()[0])
    return ip[-1]