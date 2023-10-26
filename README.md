# JD08PatchManager
Python GUI program to copy selective patches from one Roland JD-08 .svd file to another.

![Screenshot](https://github.com/NilsKr/JD08PatchManager/blob/main/screenshot.png?raw=true)

## INTRODUCTION

With the JD-08 synthesizer, Roland has decided not to allow saving of separate patches,
nor to implement SysEx dump functionality to achieve the same. 
This means that it is virtually impossible to share newly created patches with others. 

At the time of writing (October 2023), the only way to make a backup of one's own patches 
is an elaborate procedure described in e.g.

https://www.sweetwater.com/sweetcare/articles/roland-jd-08-factory-reset/

The problem with this procedure, besides it being tedious, is that all patches are grouped
in one binary .svd file. So it is hard to merge/sort patch edits made by oneself or 
others at various times.

That's where this tool comes in. One can open two .svd files and copy patches from one
to the other. Edits will be in memory unless Save is clicked explicitly. CTRL-click on
Save allows for "Save as" functionality. While the file hasn't been saved, one can 
revert the selected patch or all patches to the state in which the .svd file was loaded.

One or two .svd file names can be passed on the command line so they get opened at startup.

## INSTALLATION

Disclaimer: I'm developing on Windows, so Mac/Linux users, forgive me if any OS specific
issues are encountered.

This application was developed on Python 3, so I'm not sure if if will work on older versions.
The libraries sys, os, and tkinter should come bundled with the Python install, so a 
requirements.txt file is currently not present.

### Windows
If you are running Windows and you don't have Python installed, you may use the binary release
attached to the GitHub project page.

### Linux
On Linux (tested on Mint 21.1 Cinnamon) the commands to run the application are:

	sudo apt install git-core python3-tk
	git clone https://github.com/NilsKr/JD08PatchManager.git
	cd JD08PatchManager/
	python3 patchmanager.py
	
### MacOS
To be described. Procedure will be similar to the Linux one.	

## CONTRIBUTIONS

Drop me a line if you want to contribute code or if you want to report a but or you have 
ideas for useful features. 

## CONTACT

You can reach me at: `nkronert at hotmail dot com`

## LICENSE

[![GNU GPLv3](https://www.gnu.org/graphics/heckert_gnu.small.png "GNU GPLv3")](https://www.gnu.org/licenses/gpl-3.0.en.html)

    Copyright (C) 2023 Nils Kronert

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    https://github.com/NilsKr/JD08PatchManager

As the licensing information mentions, this software comes WITHOUT ANY WARRANTY. 
In the unlikely case where the Roland JD-08 considers a file edited by this software
to be corrupt and bricks itself, I cannot be held responsible.

On that positive note, have fun!
Cheers,
Nils