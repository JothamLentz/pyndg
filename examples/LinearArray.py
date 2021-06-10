# !/usr/bin/env python
#  -*- coding: utf-8 -*-
# """Grab a list of object numbers from the clipboard, then on a map page, array them in a vertical or horizontal line
#
# """
import os
import easygui
import pyndg as pyndg

if __name__ == "__main__":
    easygui.msgbox(msg="Copy objects into clipboard, save and close Network Notepad before Continuing")
    object_nums = pyndg.get_objects_from_clipboard()
    home = os.path.expanduser("~")
    # get diagram
    mapFile = easygui.fileopenbox(msg="Map File", title="Browse to desired map file", default=home)
    print(f'map file: {mapFile}')
    ndg = pyndg.NetworkNotepad(mapFile)
    pages = ndg.get_pages()
    p = easygui.choicebox(msg='Select page of diagram', title="Diagram Page", choices=pages.keys())
    vert = easygui.boolbox(msg='Direction', choices=['Vertical', 'Horizontal'])
    interval = easygui.integerbox(msg='Spacing between objects',
                                  title='Interval',
                                  default=50,
                                  lowerbound=1,
                                  upperbound=500)
    ndg.page[pages[p]].array_move(object_nums, vertical=vert, spacing=interval)
    ndg.write()
    print('Complete.  Re-open diagram')

