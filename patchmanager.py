#    This program allows merging of JD-08 patches from one .svd file to another.
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

from tkinter import *
from tkinter import ttk
from tkinter import messagebox 
from tkinter import filedialog
from tkinter import simpledialog
import sys
import os

VERSION = "1.0.1"
ctrlPressed = False

def keyup(e):
    global ctrlPressed
    if e.keycode == 17:
        ctrlPressed = False
    
def keydown(e):
    global ctrlPressed
    if e.keycode == 17:
        ctrlPressed = True

def getSaveAsName(fileName):

    saveAsName = filedialog.asksaveasfile(initialfile = os.path.basename(fileName), 
                    initialdir = os.path.dirname(fileName),
                    defaultextension=".svd",filetypes = (("JD-08 backup files", "*.svd"),
                                                         ("all files", "*.*")))
    return saveAsName

def getFileSize(fileName):
    try:
        if not os.path.exists(fileName):
            return -1;
        file_size = os.path.getsize(fileName)
        print(f"File size of {fileName} in Bytes is {file_size}")
        return file_size
    except FileNotFoundError:
        print("File not found.")
    except OSError:
        print("OS error occurred.")    

def getProperty(propertyName, defaultValue):
    if (os.path.exists(PatchFile.CONFIGFILE)):
        file = open(PatchFile.CONFIGFILE, 'r')
        lines = file.readlines()
        file.close()
        for line in lines:
            p = line.find("#")
            if p > -1:
                line = line[0:p] # Remove comment
            arr = line.split("=", 2)
            if len(arr) > 1:
                prop = arr[0].strip()
                if prop == propertyName:
                    value = arr[1].strip()
                    print(f"Found {prop}={value}")
                    return value
     
    print(f"Value not found for {propertyName}. Returning default {defaultValue}")
    return defaultValue
    
def setProperty(propertyName, newValue):
    if (os.path.exists(PatchFile.CONFIGFILE)):
        file = open(PatchFile.CONFIGFILE, 'r')
        lines = file.readlines()
        file.close()
        
        changed = False
        for i in range(len(lines)):
            line = lines[i]
            p = line.find("#")
            comment = ""
            if p > -1:
                comment = line[p:]
                line = line[0:p] # Remove comment
            arr = line.split("=", 2)
            if len(arr) > 1:
                prop = arr[0].strip()
                if prop == propertyName:
                    value = arr[1].strip()
                    print(f"Found {prop}={value}")
                    lines[i] = propertyName + "=" + newValue + comment
                    changed = True
                    break
    else: # File not found: create new one            
        lines = []
        lines.append(propertyName + "=" + newValue)
        
    file = open(PatchFile.CONFIGFILE, 'w')
    file.writelines(lines)
    file.close()
    print("Configuration written")
    
class App(Tk):
    def onBeforeExit(self):
        if self.leftFile.canClose():
            if self.rightFile.canClose():
                self.destroy()

    def __init__(self, title, size, *args):
        path1 = None
        path2 = None
        if len(args) > 1:
            path1 = args[1]
        if len(args) > 2:
            path2 = args[2]
        
        # main setup
        super().__init__()
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.minsize(size[0],size[1])

        self.bind("<KeyPress>", keydown)
        self.bind("<KeyRelease>", keyup)

        self.style = ttk.Style(self)

        # widgets 
        self.leftFile = PatchFile(self, path1)
        self.rightFile = PatchFile(self, path2)
        self.leftFile.otherFile = self.rightFile
        self.rightFile.otherFile = self.leftFile
        self.buttons = ButtonBar(self, self.leftFile, self.rightFile)

        self.columnconfigure((0,2), weight = 10, uniform = 'a')
        self.columnconfigure((1), weight = 2, uniform = 'a')
        self.rowconfigure((0), weight = 1, uniform = 'a')
        
        self.leftFile.grid(row = 0, column = 0, sticky = 'nswe', padx = 4, pady = 4)
        self.buttons.grid(row = 0, column = 1, sticky = 'nswe', padx = 4, pady = 4)
        self.rightFile.grid(row = 0, column = 2, sticky = 'nswe', padx = 4, pady = 4)

        self.protocol("WM_DELETE_WINDOW", self.onBeforeExit)

        # run 
        self.mainloop()

class PatchFile(Frame):
    CONFIGFILE = "patchmanager.cfg"
    
    def canClose(self):
        if self.data == None or self.data == self.orig:
            return True

        answer = messagebox.askyesnocancel("WARNING", f"The following file is not saved. Save?\n\n{self.fileName}", default='cancel')
        if answer == None:
            return False
        if answer:
            self.onSave()
        return True

    def setFileName(self, fileName):
        self.fileName = fileName
        curdir = os.path.dirname(fileName)
        self.fileNameVar.set(os.path.basename(fileName) + " (" + curdir + ")")
    
    def tryFile(self, fileName):
        data = self.loadFile(fileName)
        if data == None:
            return;

        self.setFileName(fileName)

        self.data = data
        self.orig = data[:]

        self.populateList()
        
        self.updateButtons()
    
    def __init__(self, parent, preloadFileName):
        super().__init__(parent)

        self.data = None
        self.orig = None
        self.cursel = None
        self.preloadFileName = preloadFileName

        self.create_widgets()

    def onBrowse(self):
        if not self.canClose():
            return
        
        defaultDir = getProperty("defaultdir", ".")
        fileName = filedialog.askopenfilename(initialdir = defaultDir,
              title = "Select a JD-08 backup File",
              filetypes = (("JD-08 backup files", "*.svd"),
                           ("all files", "*.*")))
        if fileName == "":
            return
        curdir = os.path.dirname(fileName)
        if curdir != defaultDir:
            setProperty("defaultdir", curdir)

        self.tryFile(fileName)
    
    def updateButtons(self):
        renameState = "disabled"
        if self.data == None:
            revertState = btnState = "disabled"
        else:
            if self.cursel != None:
                renameState = "normal"
                
            if self.data == self.orig:
                btnState = "disabled"
            else:   
                btnState = "normal"
                
            if self.cursel == None:
                revertState = "disabled"
            else:   
                if self.getPatch(self.cursel[0]) == self.getOriginalPatch(self.cursel[0]):
                    revertState = "disabled"
                else:   
                    revertState = "normal"

        self.btnSave.configure(state=btnState)
        self.btnRevert.configure(state=revertState)
        self.btnRename.configure(state=renameState)
        self.btnRevertAll.configure(state=btnState)

    def onSave(self):
        global ctrlPressed
        if self.data != None:
            if ctrlPressed:
                ctrlPressed = False # This gets stuck sometimes due to the save as dialog, so we reset it here
                saveAsName = getSaveAsName(self.fileName)
                if saveAsName != None:
                    saveAsName = saveAsName.name
            else:
                saveAsName = self.fileName
            
            if saveAsName == None:
                return

            f = open(saveAsName, mode="wb")
            f.write(self.data)
            f.close()    
            
            if saveAsName == self.fileName:
                self.orig = self.data[:]
            else:
                self.setFileName(saveAsName)
            self.onRevertAll()
            
    def onRevert(self):
        if self.data != None:
            ndx = self.cursel[0]
            self.updatePatch(ndx, self.getOriginalPatch(ndx))
    def onRename(self):
        if self.cursel[0] != None:
            newName = simpledialog.askstring(title="Rename",
                                  prompt="Rename patch to:", 
                                  initialvalue=self.getPatchName(self.data, self.cursel[0]))

            if newName != None:
                self.setPatchName(self.data, self.cursel[0], newName)
    def onRevertAll(self):
        if self.data != None:
            self.data = self.orig[:]
            temp = self.cursel
            for i in range(256):
                self.updatePatch(i, self.getOriginalPatch(i))
            self.setSelection(temp[0])
    def onPatchDblclick(self, event):
        if not (self.data == None or self.otherFile.data == None):
            self.otherFile.copyPatchFrom(self)
    def onPatchClick(self, event):
        if not (self.data == None or self.otherFile.data == None):
            self.cursel = self.patchList.curselection()
        self.updateButtons()
    def onKeyUp(self, e):
        if e.keycode == 113: # F2
            self.onRename()

    def create_widgets(self):

        # create the widgets 
        fileFrame = Frame(self)
        label = Label(fileFrame, text = "JD-08 backup file", anchor="w")
        self.fileNameVar = StringVar()
        self.fileName = fileName = Entry(fileFrame, text=self.fileNameVar, state="readonly")
        btnBrowse = Button(fileFrame, text = '...', command = self.onBrowse)
        
        listFrame = Frame(self)
        scrollFrame = LabelFrame(listFrame)

        scrollBar = Scrollbar(scrollFrame)#, orientation = 'vertical', width = 20)

        # exportselection=False below allows the listbox to show the selected item when the focus is elsewhere
        self.patchList = patchList = Listbox(listFrame, yscrollcommand = scrollBar.set, exportselection=False) 
        patchList.insert(1, "Browse for .svd file to display")
        patchList.bind('<Double-1>', self.onPatchDblclick)
        patchList.bind('<ButtonRelease-1>', self.onPatchClick)
        patchList.bind('<KeyRelease>', self.onKeyUp)
        scrollBar.config(command = patchList.yview)    

        self.buttonFrame  = buttonFrame  = Frame(self)
        buttonFrame.columnconfigure((0,1,2,3,4), weight = 1, uniform = 'buttonFrame ')
        self.btnSave      = btnSave      = Button(buttonFrame, text = 'Save', command= self.onSave)
        self.btnRevert    = btnRevert    = Button(buttonFrame, text = 'Revert patch', command= self.onRevert)
        self.btnRename    = btnRename    = Button(buttonFrame, text = 'Rename patch', command= self.onRename)
        self.btnRevertAll = btnRevertAll = Button(buttonFrame, text = 'Revert all', command= self.onRevertAll)

        fileFrame.place(relx=0, x=0, relwidth=1, width = 0, height=40, rely=0, y=10, anchor='nw')

        label.place(x=10, y=10, relwidth=1, height = 20, anchor='w')
        fileName.place(relx=0, x=10, relwidth=1, width = -44, height = 20, rely=0, y=20, anchor='nw')
        btnBrowse.place(relx=1, x=-4, width=20, height = 20, rely=0, y=20, anchor='ne')

        listFrame.place(relx=0, x=0, relwidth=1, width=0, relheight=1, height=-100, rely=0, y=56, anchor='nw')
        patchList.place(relx=0, x=10, relwidth=1, width=-44, relheight=1, rely=0, y=0, anchor='nw')
        scrollFrame.place(relx=1, x=-4, width=20, relheight=1, rely=0, y=0, anchor='ne')
        scrollBar.place(relwidth = 1, relheight = 1)
        
        buttonFrame.place(relx=0, x=0, relwidth=1, width = 0, height=40, rely=1, y=-40, anchor='nw')
        btnRevertAll.pack(side = 'right', padx = 3, pady = 1)
        btnRevert.pack(side = 'right', padx = 3, pady = 1)
        btnRename.pack(side = 'right', padx = 3, pady = 1)
        btnSave.pack(side = 'right', padx = 3, pady = 1)
        
        if self.preloadFileName != None:
            self.tryFile(self.preloadFileName)
        self.updateButtons()

    def getPatchOffset(self, data, index):
        # TODO: determine if section offset in header is what it is expected to be
        return 0x168260 + 16 + index * 0x800 # 16 is the size of the patch section metadata
    
    def getPatch(self, index):
        offs = self.getPatchOffset(self.data, index)
        return self.data[offs:offs + 0x0800]

    def getOriginalPatch(self, index):
        offs = self.getPatchOffset(self.orig, index)
        return self.orig[offs:offs + 0x0800]

    def setPatch(self, index, data):
        offs = self.getPatchOffset(self.data, index)
        for i in range(len(data)):
            self.data[offs + i] = data[i]

    def updatePatch(self, toIndex, newPatch):
        self.setPatch(toIndex, newPatch)
        self.patchList.delete(toIndex)
        newLabel = str(toIndex).rjust(3, '0') + " " + self.getPatchName(self.data, toIndex)
        origPatch = self.getOriginalPatch(toIndex)
        if origPatch != newPatch:
            newLabel += " (was : " + self.getPatchName(self.orig, toIndex) + ")"
        self.patchList.insert(toIndex, newLabel)
        toIndex += 1
        if toIndex == 256:
            toIndex = 0
        self.setSelection(toIndex)
        self.updateButtons()
        
    def copyPatchFrom(self, src):
        if src.cursel == None or self.cursel == None:
            return
        fromIndex = src.cursel[0]
        toIndex   = self.cursel[0]
        newPatch  = src.getPatch(fromIndex)
        self.updatePatch(toIndex, newPatch)
            
    def setSelection(self, toIndex):
        self.patchList.selection_clear(0, END)
        self.patchList.select_set(toIndex)
        self.patchList.see(toIndex)
        self.cursel = self.patchList.curselection()
        self.updateButtons()

    def getPatchName(self, data, index):
        offs = self.getPatchOffset(data, index)
        patchName = data[offs + 16:offs + 32]
        return patchName.decode("UTF-8").strip()

    def setPatchName(self, data, index, newName):
        if len(newName) == 0:
            messagebox.showerror("Value required", "The patch name cannot be empty")
            return
        if len(newName) >  16:
            messagebox.showwarning("Value truncated", "The patch name will be truncated to 16 characters")
            newName = newName[0:16]
        if len(newName) < 16:
            newName = newName.ljust(16, ' ')
            
        offs = self.getPatchOffset(data, index)
        arr = bytearray()
        arr.extend(newName.encode())
        data[offs + 16:offs + 32] = arr
        self.updatePatch(index, self.getPatch(index))
        
    def populateList(self):
        data = self.data
        self.patchList.delete(0,END)
        for i in range(256):
            self.patchList.insert('end', str(i).rjust(3, '0') + " " + self.getPatchName(data, i))
        self.cursel = None
        self.updateButtons()
    
    def loadFile(self, fileName):
        n = getFileSize(fileName)
        if n == -1:
            messagebox.showerror("Invalid file", f"The file '{fileName}' does not exist")
            return None;
        if n < 0x001E8800:
            messagebox.showerror("Invalid file", f"The file '{fileName}' is invalid")
            return None;

        f = open(fileName, mode="rb")
        data = f.read()
        f.close()    

        data = bytearray(data) # Convert from bytes() to bytearray() because we want to be able to change the data
        if b"N\0SVD5" != data[0:6]:
            messagebox.showerror("Invalid file", f"The file '{fileName}' is invalid (header should be 'N.SVD5' but is {data[0:6]})")
            return None;
        
        return data;
        

class ButtonBar(Frame):
    def __init__(self, parent, leftList1, rightList1):
        super().__init__(parent)

        self.leftList = leftList1
        self.rightList = rightList1

        self.create_widgets()
        #self.configure(background='green')

    def copyLeftToRight(button):
        button.rightList.copyPatchFrom(button.leftList)

    def copyRightToLeft(button):
        button.leftList.copyPatchFrom(button.rightList)
    
    def create_widgets(self):
        
        # create the widgets 
        btnCopyRight = Button(self, text = '>>', command=self.copyLeftToRight)
        btnCopyLeft  = Button(self, text = '<<', command=self.copyRightToLeft)

        # place the widgets 
        btnCopyRight.place(relx=.5, rely=.5, y=-20, height=30, anchor=CENTER)
        btnCopyLeft.place(relx=.5, rely=.5, y=20, height=30, anchor=CENTER)

# It is possible to pass one or two file names from the command line that will be opened
App('JD-08 Patch Manager v' + VERSION, (650,350), *sys.argv) 