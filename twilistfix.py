#!/usr/bin/python3
#twilistfix.py -A program to fix todo lists that have been broken between updates
#Copyright (C) 2020  Logan Andersen

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

#email me at loganandersen@mailfence.com


#NOTE FOR ALL FUTURE PROGRAMERS 
#This program is basically depreciated 
#If you still have a version of the program that uses the pickled objects instead of XML 
#Then please update because this is very old

from twilight import (
        get_all_items, 
        get_name, 
        move_to_home_directory,
        open_list,
        Folder,
        ToDoFolder,
        ToDoItem,
        save_list,
        )

import pickle 
import os

#class for a falsescreen that just prints stuff instead of adding it to curses
#It is nonfunctional because of curses.noecho in some functions 

#class FalseScreen :
#    """An object used to print things instead of using curses"""
#    @staticmethod
#    def clear() :
#        pass
#
#    @staticmethod
#    def addstr(string):
#        print(string)
#
#    @staticmethod
#    def getkey():
#        return input()
#
#    @staticmethod
#    def getstr() :
#        return input().encode()


def get_file():
    """Prompts the user to select a file by typing in a number"""
    while True :
        #print out the filenames and ask for a number
        files = os.listdir()
        for index, filename in enumerate(files):
            print(f'{index} {filename}')
        filenum = input('enter number for the file you want to open: ')
        #check if the number exists by first seeing if it is a digit and 
        #then turning it into an integer and seeing if it is in the list.
        if filenum.isdigit() and (filenum := int(filenum)) < len(files):
            return files[filenum]
        else:
            print('invalid selection, please try again')


def objectfix(filename:str):
    todolist = open_list(filename)
    if not hasattr(todolist,'folder'):
        todolist.folder = None
    for i in get_all_items(todolist):
        if not hasattr(i,'timestamp'):
            i.timestamp = None
    save_list(todolist,filename)

def main():
    move_to_home_directory()
    filename = get_file()
    objectfix(filename)
    print("folder sucessfully fixed")

main()
