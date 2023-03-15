#!/usr/bin/python3
#twi.py - reads commands from argv and runs the correct twilight program
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
import sys 
import os
import argparse 

#get software from here by import statements 
softwaredir = os.path.expanduser('~/.twilight/software')
sys.path.append(softwaredir)

MODES = {'curses','gui','text'} 

DEFAULTMODE = 'curses'

MODETEXT = '''Sets the mode that twilight will run at. There are three possible modes :
curses (default)    runs the program in curses 
text                runs the program by printing text in the terminal
gui                 runs the program with a tkinter text widget.'''

CHECKBOXTEXT = '''Accepts a two letter string to substitute for the checkbox characters.
The default checkbox characters look like this '☑☐'. The first character will be the 
done checkbox and the second character will be the not done checkbox.'''

DESCRIPTION = '''a todo list program written in python'''

EPILOG = '''
EXAMPLES 
    twi 
        run the program in curses mode

    twi -m curses
        run the program in curses mode

    twi -h 
        display help text

    twi -m text 
        tun the program in text mode

AUTHOR 
    Written by Logan Andersen

COPYRIGHT
    Copyright 2020 Logan andersen;     License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
    This is free software: you are free to change and redistribute it.  There is NO WARRANTY, to the extent permitted by law.
'''





def main():
    """Parses the arguments and then runs twitext, twicurses , or prints help depending on the arguments"""
    parser = argparse.ArgumentParser(
            description=DESCRIPTION,
            epilog=EPILOG,
            formatter_class=argparse.RawTextHelpFormatter,
            ) 

    parser.add_argument('-m','--mode', help=MODETEXT,choices = MODES, default=DEFAULTMODE)  
    parser.add_argument('-b','--checkbox-characters', help=CHECKBOXTEXT, default='☑☐')
    parser.add_argument('filename',help="the filename that will be run (must be in the twi folder lists folder", nargs='?'  )

    args = parser.parse_args() 

    options = { 'checkbox' : args.checkbox_characters } 

    if args.mode == 'curses':
        import twicurses 
        twicurses.main(options,args.filename)
    elif args.mode == 'text' :
        import twitext 
        twitext.main(options)
    elif args.mode == 'gui' : 
        import twigui 
        twigui.main(options)

if __name__ == '__main__':
    main()
