# !/usr/bin/env python
#  -*- coding: utf-8 -*-
# """Open and split a network notepad diagram
#    Then import each section into a subclass
#    Working with Network Notepad version 8.4.
# Importing each section as a Pandas Dataframe
# """

from itertools import groupby
import pandas as pd
import io
import os
from tabulate import tabulate  # for output for debugging

NL = os.linesep + " "  # for space indentation of each table entry when writing
scripts_list = ['Script_Objects_Tables', ' align', ' script', ' align', ' path', ' pen', ' brush', ' fill', ' draw', ' option']


def display_table(t):
    print(tabulate(t, headers='keys', tablefmt='psql'))


class NetworkNotepad:
    def __init__(self, path):
        self.path = path
        with open(path, encoding='utf8') as f:
            self.raw_pages = [list(grp) for key, grp in groupby(f, lambda x: x.startswith("Page ")) if not key]
        f.close()
        self.page = [Diagram(p) for p in self.raw_pages]
        self.page.insert(0, "OFFSET")  # junk at position zero to make page numbers line kup

    def get_pages(self):
        return {val.title.strip().replace('"', ''): idx for idx, val in enumerate(self.page[1:], start=1)}

    def write(self):
        pagenum = 2
        self.page.pop(0)  # remove offset before writing
        open(self.path, 'w').close()  # Clear file before append operations
        for p in self.page:
            p.write(self.path)
            with open(self.path, 'a', encoding='utf8') as f:
                if pagenum <= len(self.page):
                    f.write(f"\nPage {pagenum}\n\n")
                    pagenum += 1
            f.close()


class Diagram:
    def __init__(self, page):
        self.headers = {line.split(' ')[0]: line.rstrip('\n').split(' ') for line in page if
                        not line.startswith(' ')}
        # File info at top
        self.version = next(x for x in page if x.startswith('Version')).partition(' ')[2]
        self.title = next(x for x in page if x.startswith('Diagram_Title')).partition(' ')[2]
        self.note1 = next(x for x in page if x.startswith('Notes1')).partition(' ')[2]
        self.note2 = next(x for x in page if x.startswith('Notes2')).partition(' ')[2]

        # Page_Settings_Table
        self.page_settings_raw = [line for line in page if
                                  (line.startswith(' page_settings ') or
                                   line.startswith('Page_Settings_Table'))]
        # These don't need to be edited with python for now, just grab and save for writing file
        # Not messing with them because a couple headers are off.
        self.Link_Styles = ''.join(
            [line for line in page if (line.startswith(' define_link ') or line.startswith('Link_Styles_table'))])
        self.Shapes = ''.join(
            [line for line in page if (line.startswith(' define_shape ') or line.startswith('Shapes_Table'))])
        self.Colours = ''.join(
            [line for line in page if (line.startswith(' colours ') or line.startswith('Colours_Table'))])
        self.Text_Styles = ''.join(
            [line for line in page if (line.startswith(' text_style ') or line.startswith('Text_Styles_Table'))])
        self.Script_Objects_Tables = ''.join(
            [line for line in page if (line.startswith(tuple(scripts_list)))])

        # These do maybe need to get changed
        self.raw_Page_Settings = [line for line in page if
                                  (line.startswith(' page_settings ') or line.startswith('Page_Settings_Table'))]
        self.raw_Objects = [line for line in page if
                            (line.startswith(' object ') or line.startswith('Obj_Table') or line.startswith(
                                ' no_object'))]
        self.raw_Labels = [line for line in page if
                           (line.startswith(' label ') or line.startswith(' no_label') or line.startswith(
                               'Label_Table'))]
        self.raw_Links = [line for line in page if
                          (line.startswith(' link_object ') or line.startswith('Link_Table') or line.startswith(
                              ' no_link_object'))]
        # Links Table header missing last column in file

        # load to be changed into dataframes for easy searching/editing
        # TODO add converters or dtypes to import number columns as integers instead of floats
        # https://medium.com/analytics-vidhya/make-the-most-out-of-your-pandas-read-csv-1531c71893b5
        self.Page_Settings_Table = pd.read_csv(io.StringIO(''.join(self.raw_Page_Settings)), sep=' ')
        self.labels = pd.read_csv(io.StringIO(''.join(self.raw_Labels)), sep=' ', skipinitialspace=True)
        self.labels.index += 1
        # self.labels = self.labels.set_index('Index')
        # self.Link_Table = pd.read_csv(io.StringIO(''.join(self.raw_Links)),
        #                               delim_whitespace=True, usecols=self.headers['Link_Table'])
        self.Link_Table = pd.read_csv(io.StringIO(''.join(self.raw_Links)), sep=' ', skipinitialspace=True, usecols=self.headers['Link_Table'])
        self.Link_Table.index += 1
        # print(self.Link_Table)
        self.objects = pd.read_csv(io.StringIO(''.join(self.raw_Objects)), sep=' ', skipinitialspace=True)
        self.objects.index += 1

    def write(self, destination):
        with open(destination, 'a', encoding='utf-8', newline='\n') as f:
            f.write(f"Version {self.version}")  # Version 8.4
            f.write(f"Diagram_Title {self.title}")  # Diagram_Title ""
            f.write(f"Notes1 {self.note1}")  # Notes1
            f.write(f"Notes2 {self.note2}")  # Notes2
            self.Page_Settings_Table.to_csv(f, mode='a', sep=' ', index=False, line_terminator=NL)
            f.write('\n')  # To avoid leading Space on Colours Header  NN seems fine with blank lines
            f.write(self.Colours)
            f.write(self.Text_Styles)
            self.objects.to_csv(f, mode='a', sep=' ', index=False, line_terminator=NL)
            f.write('\n')  # To avoid leading Space on Label Header  NN seems fine with blank lines
            self.labels.to_csv(f, mode='a', sep=' ', index=False, line_terminator=NL,
                               header=self.headers['Label_Table'])
            f.write('\n')
            self.Link_Table.to_csv(f, mode='a', sep=' ', index=False, line_terminator=NL)
            f.write('\n')
            f.write(self.Link_Styles)
            f.write(self.Shapes)
            f.write(self.Script_Objects_Tables)
            f.close()

    def move_object(self, obj: int, x: int, y: int):
        """Move an object to give x,y coordinates"""
        self.objects.loc[self.objects['Index'] == obj, ['X']] = x
        self.objects.loc[self.objects['Index'] == obj, ['Y']] = y

    def get_object_as_dict(self, obj: int):
        selection = self.objects[self.objects['Index'] == obj]
        return selection.to_dict('records')[0]

    def list_objects(self):
        """List the numbers of all objects"""
        return self.objects[self.objects['Obj_Table'] == "object"]['Index'].tolist()

    def get_object_by_name(self, name: str):
        """Given an object Label, return a list of object numbers with that label"""
        num = self.labels[(self.labels['Text'] == name) & (self.labels['Type'] == 'object')]['Parent_Object'].tolist()
        if len(num) == 0:
            num = None
        elif len(num) == 1:
            num = num[0]
        return num

    def get_object_by_ip(self, ip: str):
        """Given an object ip Label, return a list of object numbers with that ip label"""
        num = self.labels[(self.labels['Text'] == ip) & (self.labels['Type'] == 'ip')]['Parent_Object'].tolist()
        if len(num) == 0:
            num = None
        elif len(num) == 1:
            num = num[0]
        return num

    def get_link(self, obj1: int, obj2: int):
        """Given two object numbers find all links between them and return a list of link numbers"""
        matches = self.Link_Table[((self.Link_Table['Obj1'] == obj1) &
                                   (self.Link_Table['Obj2'] == obj2)) |
                                  ((self.Link_Table['Obj1'] == obj2) &
                                   (self.Link_Table['Obj2'] == obj1))]['Index'].tolist()
        return matches

    def get_labels_by_object(self, Object_num: int):
        """Given an object number, return a df of labels assigned to that object"""
        lbls = self.labels[self.labels['Parent_Object'] == Object_num]
        return lbls


# TODO add enum for list selection of object type ([object, ip, ...])
    def add_label(self,  Text: str,
                  Parent_Object: int,
                  Type: str,
                  X: str = '!',
                  Y: str = '0',
                  Font_Name: str = "!",
                  Size: int = 14,
                  Bold: bool = False,
                  Italic: bool = False,
                  UL: bool = False,
                  ST: bool = False,
                  Colour: str = "&h0&",
                  Backgnd: str = "!",  # maybe bool
                  Locked: str = "!",  # maybe bool
                  Rotate: int = 0,
                  Ftranspcy: int = 255,
                  Btranspcy: int = 0,
                  Layer: int = 0,
                  Style: str = "!",
                  Parent_Link: int = 0,
                  Link_pos: int = 0,
                  Link_Seg: int = 0,
                  Xoffset: int = 0,
                  Yoffset: int = 0):
        """add a label"""
        Index = len(self.labels)+1
        new_label = {'Label_Table': "label",
                     'Index': Index,
                     'X': X,
                     'Y': Y,
                     'Text': Text,
                     'Font_Name': Font_Name,
                     'Size': Size,
                     'Bold': Bold,
                     'Italic': Italic,
                     'UL': UL,
                     'ST': ST,
                     'Colour': Colour,
                     'Parent_Object': Parent_Object,
                     'Type': Type,
                     'Backgnd': Backgnd,
                     'Locked': Locked,
                     'Rotate': Rotate,
                     'Ftranspcy': Ftranspcy,
                     'Btranspcy': Btranspcy,
                     'Layer': Layer,
                     'Style': Style,
                     'Parent_Link': Parent_Link,
                     'Link_pos': Link_pos,
                     'Link_Seg': Link_Seg,
                     'Xoffset': Xoffset,
                     'Yoffset': Yoffset}
        # append row to the dataframe
        self.labels = self.labels.append(new_label, ignore_index=True)
        return Index

    def add_object(self,
                   name: str,
                   ip: str,
                   Type: str = 'routerc2',
                   X: int = 1250,
                   Y: int = 150,
                   Float_text: str = '!',
                   Hyperlink: str = '!',
                   Parent: int = 0,
                   X_scale: int = 2,
                   Y_scale: int = 2,
                   Layer: int = 0,
                   Type_bits: int = 0,
                   Rotate: int = 0,
                   Rflip: int = 0,
                   Backgnd: bool = False,
                   Width: int = 0,
                   Height: int = 0,
                   Locked: bool = False,
                   Toolset: int = 0,
                   Var1: str = '!',
                   Var2: str = '!'):

        Index = len(self.objects) + 1
        # This code changes the way the labels are formatted depending on what type of object is created.
        print(Type)
        if Type == 'routerc1':
            Caption_Lbl = self.add_label(Text=name,
                                         Parent_Object=Index,
                                         Style='DeviceNameWhite',
                                         Type='object',
                                         X='0',
                                         Y='25',
                                         Font_Name='Microsoft Sans Serif')
            Addr_Lbl = self.add_label(Text=ip, Parent_Object=Index, Type='ip', X='0', Y='-44')
        elif Type == 'switch':
            Caption_Lbl: int = self.add_label(Text=name, Parent_Object=Index, Type='object', Style='DeviceNameWhite', X='0', Y='18')
            Addr_Lbl = self.add_label(Text=ip, Parent_Object=Index, Type='ip', X='0', Y='-44')
        elif Type == 'cloud5':
            Caption_Lbl: int = self.add_label(Text=name, Parent_Object=Index, Type='object', X='-10', Y='-12')
            Addr_Lbl = self.add_label(Text=ip, Parent_Object=Index, Type='ip', X='0', Y='12')
        else:
            Caption_Lbl = self.add_label(Text=name, Parent_Object=Index, Type='object')
            Addr_Lbl = self.add_label(Text=ip, Parent_Object=Index, Type='ip')
        # TODO Look into doing this with some kind of a switch statement that passes a dict into the add_label function or something like that

        new_object = {'Obj_Table': 'object',
                      'Index': Index,
                      'Type': Type,
                      'X': X,
                      'Y': Y,
                      'Caption_Lbl': Caption_Lbl,
                      'Float_text': Float_text,
                      'Hyperlink': Hyperlink,
                      'Parent': Parent,
                      'Addr_Lbl': Addr_Lbl,
                      'X_scale': X_scale,
                      'Y_scale': Y_scale,
                      'Layer': Layer,
                      'Type_bits': Type_bits,
                      'Rotate': Rotate,
                      'Rflip': Rflip,
                      'Backgnd': Backgnd,
                      'Width': Width,
                      'Height': Height,
                      'Locked': Locked,
                      'Toolset': Toolset,
                      'Var1': Var1,
                      'Var2': Var2}
        self.objects = self.objects.append(new_object, ignore_index=True)
        return Index

    def add_link(self,
                 Obj1: int,
                 Obj2: int,
                 name1: str,
                 name2: str,
                 ip1: str = '!',
                 ip2: str = '!',
                 Style: str = '10baseT',
                 # Hostname1_Lbl: int = 0,
                 # Hostname2_Lbl: int = 0,
                 # Addr1_Lbl: int = 0,
                 # Addr2_Lbl: int = 0,
                 Comment1: str = '!',
                 Comment2: str = '!',
                 Xoffset1: int = 0,
                 Yoffset1: int = 0,
                 Xoffset2: int = 0,
                 Yoffset2: int = 0,
                 Node_List: str = '!',
                 Align: bool = False,
                 Layer: int = 3
                 ):
        # TODO read link styles to list figure out a way to force options in Style field to only those in list when calling

        Index = len(self.Link_Table)+1
        Hostname1_Lbl = self.add_label(Text=name1, Parent_Object=Obj1, Type='!')
        Hostname2_Lbl = self.add_label(Text=name2, Parent_Object=Obj2, Type='!')
        Addr1_Lbl = self.add_label(Text=ip1, Parent_Object=Obj1, Type='ip')
        Addr2_Lbl = self.add_label(Text=ip2, Parent_Object=Obj2, Type='ip')
        new_link = {'Link_Table': 'link_object',
                    'Index': Index,
                    'Obj1': Obj1,
                    'Obj2': Obj2,
                    'Style': Style,
                    'Hostname1_Lbl': Hostname1_Lbl,
                    'Hostname2_Lbl': Hostname2_Lbl,
                    'Addr1_Lbl': Addr1_Lbl,
                    'Addr2_Lbl': Addr2_Lbl,
                    'Comment1': Comment1,
                    'Comment2': Comment2,
                    'Xoffset1': Xoffset1,
                    'Yoffset1': Yoffset1,
                    'Xoffset2': Xoffset2,
                    'Yoffset2': Yoffset2,
                    'Node_List': Node_List,
                    'Align': Align,
                    'Layer': Layer}

        self.Link_Table = self.Link_Table.append(new_link, ignore_index=True)
        return Index

