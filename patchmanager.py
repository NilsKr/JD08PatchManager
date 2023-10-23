from tkinter import *
from tkinter import ttk
from tkinter import messagebox 
from tkinter import filedialog
import os

#window = Tk()
#
#frame1 = Frame(window)
#Label(frame1, text = "Vertical lab 1").grid(row = 0, column = 0)
#Label(frame1, text = "Vertical lab 2").grid(row = 1, column = 0)
#frame1.pack()
#
#v = IntVar()
#frame2 = Frame(window)
#rb1 = Radiobutton(frame2, padx = 10, variable=v,value=1)
#rb1.grid(row = 0, column = 0)
#Label(frame2, text = "Horizontal lab1").grid(row = 0, column = 1)
#rb2 = Radiobutton(frame2, padx = 10, variable=v,value=1)
#rb2.grid(row = 1, column = 0)
#Label(frame2, text = "Horizontal lab1").grid(row = 1, column = 1)
#frame2.pack()
#
#frame3 = Frame(window)
#Label(frame3, text = "Vertical lab 3").grid(row = 0, column = 0)
#frame3.pack()
#
#window.mainloop()

#root = Tk()
#root.geometry("750x450")
#root.title("JD-08 Patch Manager")

class App(Tk):
    def __init__(self, title, size):
        
        # main setup
        super().__init__()
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.minsize(size[0],size[1])
        #self.configure(background='white')

        self.style = ttk.Style(self)

        # widgets 
        self.leftFile = PatchFile(self)
        self.rightFile = PatchFile(self)
        self.buttons = ButtonBar(self, self.leftFile, self.rightFile)

        self.columnconfigure((0,2), weight = 10, uniform = 'a')
        self.columnconfigure((1), weight = 2, uniform = 'a')
        self.rowconfigure((0), weight = 1, uniform = 'a')
        
        self.leftFile.grid(row = 0, column = 0, sticky = 'nswe', padx = 4, pady = 4)
        self.buttons.grid(row = 0, column = 1, sticky = 'nswe', padx = 4, pady = 4)
        self.rightFile.grid(row = 0, column = 2, sticky = 'nswe', padx = 4, pady = 4)

        #print(self.style.theme_use())
        #self.style.theme_use('winnative')
        #print(self.style.theme_use())

        # run 
        self.mainloop()

class PatchFile(Frame):
    CONFIGFILE = "patchmanager.cfg"
    def __init__(self, parent):
        super().__init__(parent)
        #self.place(x = 0, y = 0, relwidth = 0.3, relheight = 1)
        #self.configure(background='red')

        self.rowconfigure((0,1,3), weight = 1, uniform = 'b')
        self.rowconfigure((0,1), weight = 0, uniform = 'b')
        self.rowconfigure((2), weight = 7, uniform = 'b')
        self.columnconfigure((0), weight = 1, uniform = 'b')

        self.create_widgets()

    def getProperty(self, propertyName, defaultValue):
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
        
    def setProperty(self, propertyName, newValue):
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
        
    def onBrowse(self):
        defaultDir = self.getProperty("defaultdir", ".")
        fileName = filedialog.askopenfilename(initialdir = defaultDir,
                                          title = "Select a JD-08 backup File",
                                          filetypes = (("JD-08 backup  files",
                                                        "*.svd"),
                                                       ("all files",
                                                        "*.*")))
        if fileName == "":
            return
        messagebox.showinfo("Result", f"Browse returned {fileName}")           
        curdir = os.path.dirname(fileName)
        if curdir != defaultDir:
            self.setProperty("defaultdir", curdir)

        self.patchList.delete(0,END)
        self.patchList.insert(1,"Hello")

        #populateList()

        #fileName = self.loadFile("D:/Session1/Data/Samples & patches/Roland patches/Roland JD-08/BACKUP/JD08Backup.svd")
    
    def onSave(self):
        messagebox.showinfo("Clicked", "Save")
    def onRevert(self):
        messagebox.showinfo("Clicked", "Revert")
    def onRevertAll(self):
        messagebox.showinfo("Clicked", "Revert all")
    
    
    def create_widgets(self):

        # create the widgets 
        fileFrame = Frame(self)
        label = Label(fileFrame, text = "File", anchor="w")
        self.fileName = fileName = Entry(fileFrame, state=DISABLED)
        #fileName.configure(state="normal")
        btnBrowse = Button(fileFrame, text = '...', command = self.onBrowse)
        
        listFrame = Frame(self)
        scrollFrame = LabelFrame(listFrame)

        scrollBar = Scrollbar(scrollFrame)#, orientation = 'vertical', width = 20)

        self.patchList = patchList = Listbox(listFrame, yscrollcommand = scrollBar.set)
        patchList.insert(1, "Browse for .svd file to display")
        #patchList.insert(1, "Python")
        #patchList.insert(2, "Perl")
        #patchList.insert(3, "C")
        #patchList.insert(4, "PHP")
        #patchList.insert(5, "JSP")
        #patchList.insert(6, "Ruby")
        #for i in range(250):
        #    patchList.insert(i + 7, "Entry " + str(i + 6))
        scrollBar.config(command = patchList.yview)    

        btnSave = Button(self, text = 'Save', command= self.onSave)
        btnRevert = Button(self, text = 'Revert patch', command= self.onRevert)
        btnRevertAll = Button(self, text = 'Revert all', command= self.onRevertAll)


        #toggle_frame = Frame(self)
        #menu_toggle1 = CheckBox(toggle_frame, text = 'check 1')
        #menu_toggle2 = CheckBox(toggle_frame, text = 'check 2')

        #entry = TkEntry(self)

        # create the grid
        #self.columnconfigure((0,1,2), weight = 1, uniform = 'a')
        #self.rowconfigure((0,1,2,3,4), weight = 1, uniform = 'a')
        self.columnconfigure((0), weight = 1, uniform = 'c')
        self.rowconfigure((1,3), weight = 1, uniform = 'c')
        self.rowconfigure((0), weight = 0, uniform = 'c')
        self.rowconfigure((2), weight = 7, uniform = 'c')

        # place the widgets 
        #label.grid(row = 0, column = 0, sticky = 'sw', padx=10)
        #fileFrame.grid(row = 1, column = 0, sticky = 'nwse')
        #fileName.place(relx=0, x=10, relwidth=1, width = -44, rely=1, y=-24, anchor='nw')
        #btnBrowse.place(relx=1, x=-4, width=20, height = 20, rely=1, y=-24, anchor='ne')
        fileFrame.place(relx=0, x=0, relwidth=1, width = 0, height=40, rely=0, y=10, anchor='nw')
        #label.configure(background='green')
        label.place(x=10, y=10, relwidth=1, height = 20, anchor='w')
        fileName.place(relx=0, x=10, relwidth=1, width = -44, height = 20, rely=0, y=20, anchor='nw')
        btnBrowse.place(relx=1, x=-4, width=20, height = 20, rely=0, y=20, anchor='ne')

        #listFrame.grid(row = 2, column = 0, sticky = 'nwse')
        #patchList.place(relx=0, x=10, relwidth=1, width = -44, relheight=1, rely=0, y=0, anchor='nw')
        #scrollFrame.place(relx=1, x=-4, width=20, relheight=1, rely=0, y=0, anchor='ne')
        #scrollBar.place(relwidth = 1, relheight = 1)
        listFrame.place(relx=0, x=0, relwidth=1, width=0, relheight=1, height=-100, rely=0, y=56, anchor='nw')
        patchList.place(relx=0, x=10, relwidth=1, width=-44, relheight=1, rely=0, y=0, anchor='nw')
        scrollFrame.place(relx=1, x=-4, width=20, relheight=1, rely=0, y=0, anchor='ne')
        scrollBar.place(relwidth = 1, relheight = 1)
        
        #btnSave.grid(row = 3, column = 0, sticky = 'w', padx = 4, pady = 4)
        #btnRevert.grid(row = 3, column = 0, sticky = 'e', padx = 4, pady = 4)
        btnSave.grid(row = 3, column = 0, sticky = 'w', padx = 4, pady = 4)
        btnRevert.grid(row = 3, column = 0, padx = 4, pady = 4)
        btnRevertAll.grid(row = 3, column = 0, sticky = 'e', padx = 4, pady = 4)

    def getSelected(self):
        print(self)
        return self.patchList.curselection()
        
    def getPatch(self, index):
        messagebox.showinfo("getPatch", str(self) + " -> " + str(index))         
        return []

    def setPatch(self, index, data):
        messagebox.showinfo("setPatch", str(self) + " -> " + str(index))         

    def copyPatchFrom(self, src):
        fromIndex = self.getSelected()
        toIndex   = src.getSelected()
        self.setPatch(toIndex, src.getPatch(fromIndex))
        #messagebox.showinfo("showinfo", str(self) + " -> " + str(src))  
    
    def loadFile(self, fileName):
        f = open(fileName, mode="rb")
 
        # Reading file data with read() method
        data = f.read()
         
        # Knowing the Type of our data
        print(type(data))
         
        # Printing our byte sequenced data 
        print(len(data))
         
        # Closing the opened file
        f.close()    
        return true;
        

class ButtonBar(Frame):
    def __init__(self, parent, leftList1, rightList1):
        super().__init__(parent)
        #self.place(x = 0, y = 0, relwidth = 0.3, relheight = 1)
        self.leftList = leftList1
        self.rightList = rightList1

        print(self.leftList)
        self.create_widgets()
        #self.configure(background='green')

    def copyLeftToRight(button):
        print(button)
        button.leftList.copyPatchFrom(button.rightList)

    def copyRightToLeft(button):
        button.rightList.copyPatchFrom(button.leftList)
    
    def create_widgets(self):
        
        # create the widgets 
        btnCopyRight = Button(self, text = '>>', command=self.copyLeftToRight)
        btnCopyLeft = Button(self, text = '<<', command=self.copyRightToLeft)

        # place the widgets 
        btnCopyRight.place(relx=.5, rely=.5, y=-20, height=30, anchor=CENTER)
        btnCopyLeft.place(relx=.5, rely=.5, y=20, height=30, anchor=CENTER)

App('JD-08 Patch Manager', (550,350))