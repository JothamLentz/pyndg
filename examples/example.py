# !/usr/bin/env python
#  -*- coding: utf-8 -*-
# """Quick example utilizing NetworkNotepad class
#    to open a a diagram file and add a couple of objects
#    to the first page
# """
from cfgMgmt.backup import bk
import pyndg as pyndg

if __name__ == "__main__":
    """For testing"""
    filePath = '/NetworkNotepad/demo.ndg'
    bk(filePath)
    ndg = pyndg.NetworkNotepad(filePath)
    # print(dia.raw_pages[1])

    # display_table(ndg.page[0].labels)

    o1 = ndg.page[1].add_object(name="ice", ip="1.1.1.1", Type='switch')
    o2 = ndg.page[1].add_object(name="cicle", ip="2.2.2.2", Type='Multilayer switch')
    ndg.page[1].add_link(Obj1=o1, Obj2=o2, name1="Gi0/0", name2="Te1/0/1", ip1="3.3.3.1", ip2="3.3.3.2")

    linkage = ndg.page[1].get_link(19,20)
    print(linkage)

    ndg.write()