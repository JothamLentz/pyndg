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
    [x_text, y_text] = easygui.multenterbox(msg='Desired Dimensions (0 means unchanged)',
                                  title='Enter Dimensions',
                                  fields=['X Scale', 'Y Scale'],
                                  values=[0, 0])
    x_size = float(x_text)
    y_size = float(y_text)
    ndg.page[pages[p]].bulk_resize(object_nums, x_scale=x_size, y_scale=y_size)
    ndg.write()
    print('Complete.  Re-open diagram')