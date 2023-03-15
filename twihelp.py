#twihelp - prints out the docstrings on twilight
#Copyright (C) 2020 Logan Andersen
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <https://www.gnu.org/licenses/>.

#Email me at loganandersen@mailfence.com

import twilight
print('the purpose of this program is to print out the twilight help documentation\n'
        +'it is primarily intended for developers. A tutorial for users is going to come later')

helpfile = input("""
        enter the name of the file you would like to call help on

        twilight
        twitext 
        twicurses
        twi

""").strip()
if helpfile == 'twilight' :
    import twilight as helpmod
elif helpfile == 'twitext' :
    import twitext as helpmod
elif helpfile == 'twicurses':
    import twitext as helpmod
elif helpfile == 'twi':
    import twi as helpmod
    
help(helpmod)
