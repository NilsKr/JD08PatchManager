#    Copyright (C) 2023 Nils Kronert
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#    https://github.com/NilsKr/JD08PatchManager

#    This viewer uses information derived from JD-08.hpp as present in:
#    JDTools - Patch conversion utility for Roland JD-800 / JD-990
#    2022 by Johannes Schultz
#    License: BSD 3-clause
#    https://github.com/sagamusix/JDTools


import tkinter as tk
import tkinter.font as tkFont
import sys
import os

from tkinter import *
from tkinter import ttk
from tkinter import Frame 
from preferences import Preferences

def debug(msg):
    pass
    #print(msg)

def getIndent(line):
    indent = line.find(line.strip())
    #sprint(f'Indent = {indent}')
    return indent
    
class PatchDiffViewer(Frame):
    def __init__(self, parent, preferences):
        super().__init__(parent)

        self.prefs = preferences
        self.tree = None
        self.lines = None

        debug("readStructs")
        self.structs = readStructs("JD-08.patchdef")

        debug("Structures found:")
        for i, key in enumerate(self.structs):
            s = self.structs[key]
            debug(s.name)
            for f in s.fields:
                if f.count == 1:
                    debug(f"  {f.type} {f.name}")
                else:
                    debug(f"  {f.type} {f.name}[{f.count}]")

        self.chkDiffOnly = tk.IntVar()
        self.chkDiffOnly.set(self.prefs.getValue("DiffsOnly", "0"))

        self.chkShowUnknown = tk.IntVar()
        self.chkShowUnknown.set(self.prefs.getValue("ShowUnknown", "0"))

        self.chkShowPrecomputed = tk.IntVar()
        self.chkShowPrecomputed.set(self.prefs.getValue("ShowPrecomputed", "0"))

        self._setup_widgets()
        self._build_tree()

    def _filterChanged(self):
        debug(f"diffOnly={self.chkDiffOnly.get()}, showUnknown={self.chkShowUnknown.get()},showPrecomputed={self.chkShowPrecomputed.get()}")
        self.prefs.setValue("DiffsOnly", str(self.chkDiffOnly.get()))
        self.prefs.setValue("ShowUnknown", str(self.chkShowUnknown.get()))
        self.prefs.setValue("ShowPrecomputed", str(self.chkShowPrecomputed.get()))
        self.prefs.save()
        self.setPatches(self.leftPatch, self.rightPatch)

    def _setup_widgets(self):
        optionsFrame = Frame(self)
        optionsFrame.pack(fill=X)
        c1 = tk.Checkbutton(optionsFrame, text='Show differences only',variable=self.chkDiffOnly, onvalue=1, offvalue=0, command=self._filterChanged)
        c1.pack(side = 'left')
        c2 = tk.Checkbutton(optionsFrame, text='Show "unknown" fields',variable=self.chkShowUnknown, onvalue=1, offvalue=0, command=self._filterChanged)
        c2.pack(side = 'left')
        c3 = tk.Checkbutton(optionsFrame, text='Show precomputed sections',variable=self.chkShowPrecomputed, onvalue=1, offvalue=0, command=self._filterChanged)
        c3.pack(side = 'left')

        container = Frame(self)
        container.pack(fill='both', expand=True)
        # create a treeview with dual scrollbars
        self.tree = ttk.Treeview(container, columns=patch_header, show="tree headings")
        vsb = ttk.Scrollbar(container, orient="vertical",
            command=self.tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal",
            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set,
            xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=container)
        vsb.grid(column=1, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

    def _open_children(self, parent):
        self.tree.item(parent, open=True)  # open parent
        for child in self.tree.get_children(parent):
            self._open_children(child)    # recursively open children

    def _autosizeColumns(self):
        for col in patch_header:
            self.tree.heading(col, text=col, anchor=CENTER)
            # adjust the column's width to the header string
            self.tree.column(col, anchor=CENTER,
                width= 20 + tkFont.Font().measure(col.title()))

    def _build_tree(self):
        self.tree.column("#0", minwidth = 200)
        self.tree.heading("#0", text="Parameter", anchor=W)
        
        self._autosizeColumns()

    def populate(self, lines):
        self.lines = lines
        for child in self.tree.get_children(''):
            self.tree.delete(child)

        n = 0
        parentNdx = 0
        curIndent = 0
        stack = []
        for line in lines:
            #print(f'Inserting line {n}')
            fields = line.split('\t')
            indent = getIndent(fields[0])
            if indent > curIndent:
                debug("indent")
                stack.append(parentNdx)
                parentNdx = n
                curIndent = indent
            elif indent < curIndent:
                while indent < curIndent:
                    debug("unindent")
                    parentNdx = stack.pop()
                    curIndent -= 2 # Assuming 2 spaces per level of indentation. TODO
            
            item = ( fields[1], fields[2] )
            if parentNdx == 0:
                self.tree.insert('', 'end', text=fields[0].strip(), iid = n, values=item)
            else:
                self.tree.insert(parentNdx - 1, 'end', text=fields[0].strip(), iid = n, values=item)
            n += 1
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                #print(f'ix={ix}, val={val}')
                col_w = tkFont.Font().measure(val)
                if self.tree.column(patch_header[ix],width=None)<col_w:
                    self.tree.column(patch_header[ix], width=col_w)
        self._open_children('')
        self._autosizeColumns()

    def setPatches(self, leftPatch, rightPatch):
        self.leftPatch  = leftPatch
        self.rightPatch = rightPatch
        
        if leftPatch == None and rightPatch == None:
            self.populate(["Nothing to show\tn.a.\tn.a."])
            return
        ndx = 0
        result = []
        debug(f"dumpStruct diffOnly={self.chkDiffOnly.get()} showUnknown={self.chkShowUnknown.get()} showPrecomputed={self.chkShowPrecomputed.get()}")
        ndx = dumpStruct(leftPatch, rightPatch, ndx, "Patch", "PatchVST", "", self.chkDiffOnly.get(), 
                         self.chkShowUnknown.get(), self.chkShowPrecomputed.get(), self.structs, result)
        self.populate(result)

patch_header = ['Left list', 'Right list']
patch_dump = [
  'Item1\ta\ta',' Item2\ta\ta','  Item3\ta\ta','  Item3b\tb\tb',' Item4\ta\ta','Item5\ta\ta'
]

class FieldDef():
    def __init__(self, fieldType, fieldName, count, comment):
        self.type = fieldType
        self.name = fieldName
        self.count = count
        self.comment = comment

    def __repr__(self): 
        if self.count == 1:
            return self.type + " " + self.name + self.comment
        return self.type + " " + self.name + "[" + str(self.count) + "]" + self.comment

class Struct():
    def __init__(self, structName):
        self.name = structName
        self.fields = []

    def __repr__(self): 
        return "struct " + self.name + " " + str(self.fields)   
        
    def addField(self, fieldType, fieldName, count, comment):
        self.fields.append(FieldDef(fieldType, fieldName, count, comment))
        
def readStruct(lines, ndx, structs, namespace):
    line = lines[ndx].strip()
    p = line.find(" ")
    structName = line[p+1:].strip()
    newStruct = Struct(namespace + structName)
    structs[namespace + structName] = newStruct
    ndx += 1
    while ndx < len(lines):
        line = lines[ndx].strip()
        ndx += 1
        
        p = line.find("//")
        if p == -1:
            comment = ""
        else:
            comment = " " + line[p:]
            line = line[:p].strip()
       
        if line == "":
            continue
        if line == "{":
            continue
        if line == "}": # End of structure
            return ndx

        if line.find("struct ") > -1:
            ndx = readStruct(lines, ndx - 1, structs, structName + "::")
            continue
            
        if line.find("std::array") > -1:
            p = line.find("<")
            q = line.find(",")
            fieldType = line[p+1:q].strip()
            p = line.find(">")
            count = int(line[q+1:p].strip())
            debug(f'count={count}')
            fieldName = line[p+1:].strip()
        else:
            p = line.find(" ")
            fieldType = line[:p].strip()
            fieldName = line[p+1:].strip()
            count = 1
        if not (fieldType == "uint8_t" or fieldType == "uint16le" or fieldType == "char"):
            if fieldType.find("::") == -1 and structName != "":
                debug(f'fieldType={fieldType} structName={structName}')
                fieldType = structName + "::" + fieldType
        newStruct.addField(fieldType, fieldName, count, comment)
            
    return ndx

def readStructs(fileName):
    structs = {}
    if not os.path.exists(fileName):
        print("File not found: " + fileName)
    else:
        file = open(fileName, 'r')
        lines = file.readlines()
        file.close()
        print(f'{len(lines)} lines')
        ndx = 0
        while ndx < len(lines):
            line = lines[ndx].strip()
            if line.find("struct ") > -1:
                debug(line)
                ndx = readStruct(lines, ndx, structs, "")
            else:
                ndx += 1
    return structs

def hexValue(data, ndx, count):
    result = ""
    while count > 8:
        debug(count)
        result += data[ndx:ndx + 8].hex() + "\n"
        count -= 8
        ndx += 8
    if count > 0:
        result += data[ndx:ndx + count].hex() 
    debug("done")
    return result

def addValue(result, field, value, rightValue, indent, showUnknown, diffOnly):
    if field.name.find("unknown") > -1 and not showUnknown:
        return
    if value == rightValue and diffOnly:
        return

    if rightValue == None:
        result.append(f"{indent}{field.name}{field.comment}\t{value}\t{value}")
    else:
        result.append(f"{indent}{field.name}{field.comment}\t{value}\t{rightValue}")

def dumpStruct(leftData, rightData, ndx, fieldName, structName, indent, diffOnly, showUnknown, showPrecomputed, structs, result):
    try:
        structure = structs[structName]
    except KeyError: # Couldn't find namespace::structname -> search for structname only
        try:
            structure = structs[structName[structName.find("::") + 2:]]
        except KeyError: # Still not found is an error condition
            print("Cannot find struct " + structName)
            return -1

    result.append(indent + fieldName + "\t \t ")
    indent += "  "
    
    if rightData == None:
        diffOnly = False

    for field in structure.fields:
        debug(f"dumping field {field.name} {field.type} {field.count}")
        leftValue = ""
        rightValue = ""
        if field.type == "uint16le":
            if field.count > 1:
                print("Cannot read arrays of uint16le yet")
                return -1
            if not leftData == None:
                leftValue = int(leftData[ndx]) + int(leftData[ndx+1]) * 256 
            if not rightData == None:
                rightValue = int(rightData[ndx]) + int(rightData[ndx+1]) * 256 
            ndx += 2 # skip additional byte

            addValue(result, field, leftValue, rightValue, indent, showUnknown, diffOnly)
        elif field.type == "uint8_t" or field.type == "char":
            if field.type == "uint8_t":
                if leftData != None:
                    if field.count == 1:
                        leftValue = leftData[ndx]
                    else:
                        leftValue = hexValue(leftData, ndx, field.count)
                if rightData != None:
                    if field.count == 1:
                        rightValue = rightData[ndx]
                    else:
                        rightValue = hexValue(rightData, ndx, field.count)
            else:
                if leftData != None:
                    leftValue = "'" + leftData[ndx:ndx + field.count].decode("UTF-8") + "'"
                if rightData != None:
                    rightValue = "'" + rightData[ndx:ndx + field.count].decode("UTF-8") + "'"
            ndx += field.count
                
            addValue(result, field, leftValue, rightValue, indent, showUnknown, diffOnly)
        else:
            for i in range(field.count):
                structValues = []
                if field.count > 1: # Array
                    debug("Array!")
                    ndx = dumpStruct(leftData, rightData, ndx, field.name + "[" + str(i) + "]", field.type, indent, diffOnly, showUnknown, showPrecomputed, structs, structValues)
                else:
                    ndx = dumpStruct(leftData, rightData, ndx, field.name, field.type, indent, diffOnly, showUnknown, showPrecomputed, structs, structValues)
                if showPrecomputed == 1 or field.name.find("Precomputed") == -1:
                    if len(structValues) > 1:
                        result.extend(structValues)
    return ndx

