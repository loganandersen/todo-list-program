#!/usr/bin/python

#pickletoxml.py - converts all pickle files into xml files in the .todolists folder 
#Copyright (C) 2020 logan andersen 

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
from twilight import * 
#sorry for the star I need it because otherwise pickle won't see that it has acess to the functions required to rebuild the object
#The only thing I use from twilight is save_list 
from install import todofolder
import os
import datetime 
import pickle
def legacy_open_list(filename):
    """Uses the pickle module to open a list binary

    Arguments:
        filename :
            The name of the file that pickle is attempting to load, the saved file should be a folder object.
    """
    return pickle.load(open(filename,'rb'))
def convert(filename) :
    """turns a pickled todo list into an xml file"""
    try :
        save_list(legacy_open_list(filename),filename)
        
    except pickle.UnpicklingError:
        pass



def main() : 
    os.chdir(todofolder)
    for i in os.listdir():
        convert(i)

if __name__ == '__main__' :
    main()
