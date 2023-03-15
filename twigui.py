#!/usr/bin/python3
#twigui.py - a gui impementation of twilight
#Copyright (C) 2020 Logan Andersen

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
import twilight
import tkinter as tk 
import twicurses 
from tkinter import ttk 
import curses 
import sys 

def handle_keypress(keysymb,handler) :
    """handles the input of the user, used in a root.bind method
    
    This basically just forwards the letter that it grabs to the handler
    Look at InputHandler.get_key for where it uses the variable. 
    This is used by making a lambda function with the handler variable already 
    attached. 
    
    Arguments 
    ---------
    keysymb : is the character that the user pressed
        
    handler : is the input handler object that is waiting for the key to be pressed."""
    #ignore when the user presses Lshift and Rshift
    if keysymb.keycode not in (62,50):  
        if handler.iswaiting :
            handler.key = keysymb.char
            handler.iswaiting = False


def wrap_twistart_with_destroy(root,*args) :
    """this is used to destroy the screen after twilight.run_start is done running

    This is done because otherwise the user will be left with an unresponive screen

    arguments 
    ---------
    root : the object that is getting destroyed 

    *args : the arguments that will be run at twilight.run_start 
    """ 

    twilight.run_start(*args) 
    root.destroy()

class InputHandler :
    """A class that is used to handle any input with the get_key command
    
    To make the Input handler stop waiting you must use something in the Tk event loop change its 
    iswaiting variable to false . If the handler is waiting then it will continually call root.update to 
    make sure the user can still input keys. 
    
    Attributes
    ----------
    
    key :
        the key that will be returned when get_key is called. Change this if you want to change the key.
        
    iswaiting : 
        set this to False when you want get_key to break out if its infinite loop
        
    root : 
        the tkinter root object that is continually updated with root.update() until iswaiting is changed to False"""
    def __init__(self,root) :
        """sets self.key to '' , self.iswaiting to False, and self.root to root
        
        Arguments 
        ---------
        root:
            the screen that is continually updated with self.root.update
        """
        self.key = ''
        self.iswaiting = False 
        self.root = root

    
    def get_key(self) :
        """Returns control to the tk event loop until self.iswaiting changes to false. After that it returns self.key
        
        If somebody can find a better way to do this (root.update actually nests loops from what I understand) 
        then please change this function to act like curses.get_key but with tkinter."""
        self.iswaiting = True 
        #This is very counter intuitive and I have been told this will lead to madness because of loop nesting 
        #But I am lazy so.... 
        #Also I Will write more comments later 
        #look at handle_keypress for how self.key and self.iswaiting changes  
        while self.iswaiting == True :
            #"""""""go back""""""" to tkinter (actually create another loop inside of the previous one) 
            self.root.update()  
        return self.key 
class PseudoScreen :
    """Combines input management and display management into a single object
    
    Attrubutes 
    ------------
        textpad :
            a tkinter textpad widget where the text will be desplayed

        input :
            an InputHandler like object that is in change of processing user input.

        messagelabel :
            a tkinter Label widget where messages will be displayed
    """ 
        
    def __init__(self,textpad,input_,messagelabel) :
        """sets the arguments to the coresponding variables 

        arguments 
        ---------
        textpad :
            a tkinter textpad widget where the text will be desplayed

        input_ :
            an InputHandler like object that is in change of processing user input.

        messagelabel :
            a tkinter Label widget where messages will be displayed
        """
        self.textpad = textpad
        self.input = input_
        self.messagelabel = messagelabel 

    def move_to(self,line) :
        """ moves to a certain line in the program
        
        arguments
        ----------
        line : 
            the ammount of lines to scroll
        """ 
        self.textpad.yview('scroll' ,str(line-1), 'units') 

def empty_function(*args) :
    """does nothing""" 
    pass 


def gui_clear(item:twilight.BrowserHolder): 
    """deletes everything on the screens textpad widget"""
    item.screen.textpad['state'] = 'normal'
    item.screen.textpad.delete('1.0','end')
    item.screen.textpad['state'] = 'disabled'
    item.screen.messagelabel['text'] = ''

def gui_max_items(item:twilight.BrowserHolder):  
    """returns 5000 this is not used because the print function simply prints the whole screen in gui mode"""
    return 5000   

def gui_display_string(item:twilight.BrowserHolder,string,hilight=False,message=False):
    """adds the string to the screen with formatting options
    
    hilights the background to red if hilight = True, 
    if message equals True , then set the label to the text 'string' instead of printing it on the screen. """
    item.screen.textpad['state'] = 'normal'
    if hilight :
        item.screen.textpad.insert('end',string,'hilight') 
    elif message : 
        item.screen.messagelabel['text'] = string.strip()
    else :
        item.screen.textpad.insert('end',string)
    item.screen.textpad['state'] = 'disabled'

def gui_draw(item,folder,clear=True): 
    """Prints folder as a bunch of strings using the twilight.foldertree method.

    Thiis function prints the entire folder and then skips the scroll bar to the item that is selected.
    This function dosen't use any direct references to item.screen so it is fine to use it for other things"""
    if clear :
        item.clear_screen()
    #check if browser is browsing an empty folder and if so then put the cursor on the empty folder
    #The offset (pos += 1) is important because foldertrees first thing it prints is the directory
    #name ; wheras absolute position ignores the directory so if it were not true, then the hilight
    #would be at the wrong spot. if there is nothing in the images then pos = 0 and the cursor will
    #hilight the directory name instead.
    pos = item.browser.absolute_postion(folder)
    if (pos != None ):
        pos += 1
    else:
        pos = 0
    #print the branches and hilight where the browser is at.
    for num,branch in enumerate(twilight.folder_tree(folder)):
        if num == pos :
            item.display_string(branch+'\n',hilight=True)
        #make it stop when the item is in the middle
        else:
            item.display_string(branch+'\n')
        item.refresh_screen()
    item.screen.move_to(pos)
def gui_askkey(item):  
    """returns item.screen.input.get_key()"""
    return item.screen.input.get_key()


def gui_get_string(browserholder,prompt=''): 
    """A function used to ask the user for a string with prompt. 

    Arguments :
        browserholder :
            an instance that holds a screen and a folderbrowser. 
            read twilight.BrowserHolder for more information

        prompt :
            A prompt telling the user what to enter
    """
    #Add the prompt to the screen
    if prompt :
        browserholder.display_string(prompt)
    sentence = [] 
    while True : 
        nextkey = browserholder.get_key() 
        if nextkey == '' : #if key is unknown
            pass
        elif ord(nextkey) == 13 : #if the key is return
            break
        elif ord(nextkey) == 8 : #If the key is backspace
            if len(sentence) > 0 : 
                sentence.pop() 
                browserholder.screen.textpad['state'] = 'normal'
                browserholder.screen.textpad.delete('end -2  chars','end')
                browserholder.screen.textpad['state'] = 'disabled'
        else :
            sentence.append(nextkey) 
            browserholder.display_string(nextkey) 
    return ''.join(sentence) 



gui_functions = { 
        'clear_screen'     : gui_clear,
        'max_items'        : gui_max_items,
        'draw_screen'      : gui_draw,
        'display_string'   : gui_display_string,
        'refresh_screen'   : empty_function,
        'get_key'          : gui_askkey,
        'new_list'         : twicurses.curses_new_list,
        'enter_input_mode' : empty_function,
        'exit_input_mode'  : empty_function,
        'get_string'       : gui_get_string,
        'add_item_generic' : twicurses.curses_generic_add_item,
        'edit_a_todo'      : twicurses.curses_edit_todo,

        }

gui_start_functions = {               
        'can_scroll'       : empty_function ,
        'get_key'          : gui_askkey ,
        'get_string'       : gui_get_string,
        'refresh_screen'   : empty_function,
        'display_string'   : gui_display_string,
        'clear_screen'     : gui_clear,
        'enter_input_mode' : empty_function,
        'exit_input_mode'  : empty_function,
        'new_list'         : twicurses.curses_new_list,
        }

def start_program(stdscr,options=dict()):
    """begins the start program with stdscr as the screen argument in twilight.run_start, 

    used in conjunction with curses.wrapper

    Arguments 
    ----------
    stdscr : 
        the screen where the text will be printed
    """
    twilight.run_start(stdscr,twilight.STARTKEYMAP,twilight.browserkeymappings,curses_start_functions,curses_functions,cursesprompts,options)

def main(options=dict()) :    
    """Creates the screen and Opens up the start user interface. 

    Moves user to twilights home directory
    builds the screen and then runs the tkinter mainloop"""
    #Move into the .twitodolists folder.
    twilight.move_to_home_directory()

    #write the code to build the screen 

    root = tk.Tk()
    root.title('Twilight Gui')
    
    #make textpad related stuff
    textframe = tk.ttk.Frame(root) 
    textpad = tk.Text(textframe, width=80, height=25, background='white',wrap='none')
    scrollbar = tk.ttk.Scrollbar(root,orient='vertical', command = textpad.yview,) 
    textpad['yscrollcommand'] = scrollbar.set 
    textpad.tag_configure('hilight',background='red') 

    #make the message label 
    messagelabel = ttk.Label(root,text='No message to display as of now') 
    
    #grid all of the items 
    textframe.grid(column=0,row=0, sticky = (tk.N,tk.S,tk.W,tk.E))
    textpad.grid(column=0,row=0,sticky = (tk.N,tk.S,tk.W,tk.E))
    scrollbar.grid(column=1, row=0, sticky = (tk.N,tk.S))
    messagelabel.grid(column = 0, row = 1 , sticky = (tk.W,tk.E))
    
    #configure the weights for making the widgets larger 
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0,weight=1)

    textframe.rowconfigure(0,weight=1)
    textframe.columnconfigure(0,weight=5)
    textframe.columnconfigure(1,weight=0)
    #make the handler and screen variables 
    handler = InputHandler(root)
    screen = PseudoScreen(textpad,handler,messagelabel)

    
    #bind the the keys to handle_keypress function
    root.bind("<KeyPress>", lambda x : handle_keypress(x,handler))

    #start up the program and then call the tkinter loop
    root.after(20,wrap_twistart_with_destroy(root,screen,twilight.STARTKEYMAP,twilight.browserkeymappings,gui_start_functions,gui_functions,twicurses.cursesprompts,options ))
    root.mainloop()

    #I may want to make a build screen function later 



#Run the main program.
if __name__ == '__main__':
    main()
