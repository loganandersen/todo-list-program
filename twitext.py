#!/usr/bin/python3
#twitext.py - a curses implementation of twilight
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
import twilight
import twicurses 
def empty_function(*args,**kwdargs):
    """returns None an absorbs any arguments"""
    pass

def text_max_items(item:twilight.BrowserHolder):
    """returns 5000 

    this is a large number because you can scroll in the terminal already 
    so it is unecessary to wory about how many items fit in the screen
    """
    return 5000

def text_display_string(item:twilight.BrowserHolder,string,hilight=False,message=False):
    """uses print to print string. 

    if hilight is equal to True then it print it with <<< infront of the line
    otherwise it will just print it.
    Each time it prints something end is set to '' instead of \\n so it is necessesary to
    to add the \\n into your string

    Arguments : 
        item : 
            not referenced in the funtion,  just kept for other implementations 

        string : 
            the string to be printed

        hilight :  
            a boolian that tells the program whether or not there should be <<<< at the end of the string

        message :
            a boolian that specifies whether or not it is a message; as of now it has no functuion (it is only used in twigui) 
    """
    if hilight :
        #fit <<< after the last \n in the string
        splts = string.rpartition('\n')
        final = splts[0] + ' <<<' + splts[1] + splts[2] 
        print(final,end='')
    else :
        print(string,end='')

def text_askkey(item):
    """asks for input and then returns the first character the user types

    If the user types no character it will return '\\n' instead 
    """
    key = input() 
    if len(key) >= 1 :
        return key[0]
    else :
        return '\n'




def text_get_string(browserholder,prompt=''):
    """returns user input with prompt displayed before they type

    Arguments
    ---------
    browserholder :
        can be anything , used for the screen in other twilight implementations 

    prompt :
        is displayed to ask the user what they should type

    """
    #Add the prompt to the screen
    return input(prompt)





text_functions = { 
        'clear_screen'     : empty_function,
        'max_items'        : text_max_items,
        'draw_screen'      : twicurses.curses_draw,
        'display_string'   : text_display_string,
        'refresh_screen'   : empty_function,
        'get_key'          : text_askkey,
        'new_list'         : twicurses.curses_new_list,
        'enter_input_mode' : empty_function,
        'exit_input_mode'  : empty_function,
        'get_string'       : text_get_string,
        'add_item_generic' : twicurses.curses_generic_add_item,
        'edit_a_todo'      : twicurses.curses_edit_todo,

        }

text_start_functions = {
        'can_scroll'       : empty_function  ,
        'get_key'          : text_askkey ,
        'get_string'       : text_get_string,
        'refresh_screen'   : empty_function,
        'display_string'   : text_display_string,
        'clear_screen'     : empty_function,
        'enter_input_mode' : empty_function,
        'exit_input_mode'  : empty_function,
        'new_list'         : twicurses.curses_new_list,
        }
textprompts = {'get_action' : '''
    would you like to:
    print the contents of the todo directory (press p)
    delete a todo list (press d)
    make a new list? (press u) 
    open an old list (press o)
    quit press (Z)

    '''
}

            
def start_program(stdscr,options=dict()):
    """displays the user interface and accepts user input

    Arguments
    ---------
    stdscr:
        the screen where text is displayed. This should be None because this implementation uses print rather than 
        a more specific screen. 

    options : 
        the options to be put into the twilight.run_start program
        
    """
    twilight.run_start(stdscr,twilight.STARTKEYMAP,twilight.browserkeymappings,text_start_functions,text_functions,textprompts,options)

def main(options=dict()) :
    """moves to the twitodolist folder and then runs start_program with screen = None"""
    #Move into the .twitodolists folder.
    twilight.move_to_home_directory()
    #run the main program through a curses wrapper
    start_program(None,options)

#Run the main program.
if __name__ == '__main__':
    main()
    
