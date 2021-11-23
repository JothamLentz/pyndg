# !/usr/bin/env python
#  -*- coding: utf-8 -*-
# """Grab a list of object numbers from the clipboard, then on a map page, resize them in the x or y direction or both
#
# """

import os
import easygui
import pyndg as pyndg

if __name__ == "__main__":
    easygui.msgbox(msg="Copy objects you would like to resize into clipboard, save and close Network Notepad before Continuing")
    object_nums = pyndg.get_objects_from_clipboard()
    home = os.path.expanduser("~")
    # get diagram
    mapFile = easygui.fileopenbox(msg="Map File", title="Browse to desired map file", default=home)
    print(f'map file: {mapFile}')
    ndg = pyndg.NetworkNotepad(mapFile)
    pages = ndg.get_pages()
    p = easygui.choicebox(msg='Select page of diagram', title="Diagram Page", choices=pages.keys())
    new_type = easygui.enterbox(msg='New type for all selected objects)',
                                title='New Type')
    for obj in object_nums:
        ndg.page[pages[p]].retype_object(obj, new_type=new_type)
    ndg.write()
    print('Complete.  Re-open diagram')