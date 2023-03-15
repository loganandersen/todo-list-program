#!/usr/bin/python

#install.py - installs the twilight program by making the default folders
#Copyright (C) 2020  logan andersen

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <https://www.gnu.org/licenses/>.

#Email me at loganandersen@mailfence.com


#PROGRAM START
#---------------------------------------------------
#read the readme for instructions for how to install 
#---------------------------------------------------

import os 
import shutil
#Feel free to change the location of this file if you like
#this is where the file will be installed 
binfile = '/usr/bin/twilight' 
homedir = os.path.expanduser('~')
#Do not change FOLDERNAME, The program will break if you do, I will make a config file later
FOLDERNAME = '.twilight' 
TODOLISTS = 'twitodolists'
SOFTWARE = 'software'
ARCHIVE = 'archived_todo_lists' 


twifolder = os.path.join(homedir,FOLDERNAME)
todofolder = os.path.join(twifolder,TODOLISTS)
softwarefolder = os.path.join(twifolder,SOFTWARE)
archivefolder = os.path.join(twifolder,ARCHIVE) 
oldfolder = os.path.join(homedir,'.'+TODOLISTS)

if __name__ == '__main__' :
    #make the folders if they don't exist
    if not os.path.exists(twifolder):
        os.mkdir(twifolder)
    if not os.path.exists(todofolder):
        os.mkdir(todofolder)
    if not os.path.exists(softwarefolder):
        os.mkdir(softwarefolder)
    if not os.path.exists(archivefolder) :
        os.mkdir(archivefolder) 


    #move stuff over to the softwarefolder
    movesoftware = (
            'twicurses.py',
            'twilight.py',
            'twitext.py',
            'twigui.py',
            )
    for filename in movesoftware :
        shutil.copy(filename,os.path.join(softwarefolder,filename))
    #create a twi.py to move to wherever the user wants the software to be
    shutil.copy('twi.py','twi')
    

    #Move all the other folders over 
    
    #move things over from the old folder
    if os.path.exists(oldfolder):
        for i in os.listdir(oldfolder):
            shutil.move(os.path.join(oldfolder,i),os.path.join(todofolder,i))
        os.rmdir(oldfolder)


