#!/usr/bin/python3
#twicurses.py - a curses implementation of twilight
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
import curses


def curses_clear(item:twilight.BrowserHolder):
    """runs item.screen.clear()"""
    item.screen.clear()

def curses_max_items(item:twilight.BrowserHolder):
    """returns the ammount of lines that can fit on a screen"""
    return item.screen.getmaxyx()[0]

def curses_display_string(item:twilight.BrowserHolder,string,hilight=False,message=False):
    """adds the string with curses.A_STANDOUT if hilight is True, otherwise just displays the string normally
    
    message is just here to avoid errors, It is only used for twigui so it has no function as of now """
    if hilight :
        item.screen.addstr(string,curses.A_STANDOUT)  
    else :
        item.screen.addstr(string)

def curses_refresh(item):
    """Calls item.screen.refresh"""
    item.screen.refresh()

def curses_draw(item,folder,clear=True):
    """Prints folder as a bunch of strings using the twilight.foldertree method.

    This function stops adding strings if the absolute position is not centered.
    This function dosen't use any direct references to item.screen so it is fine to use it for other things"""
    if clear :
        item.clear_screen()
    #check if browser is browsing an empty folder and if so then put the cursor on the empty folder
    #the checking also sets pos to browser.absolute_position() 
    #The offset (pos += 1) is important because foldertrees first thing it prints is the directory
    #name ; wheras absolute position ignores the directory so if it were not true, then the hilight
    #would be at the wrong spot. if there is nothing in the images then pos = 0 and the cursor will
    #hilight the directory name instead.
    pos = item.browser.absolute_postion(folder)
    if pos != None :
        pos += 1
    else:
        pos = 0
    # find the middle of the screen to make it so the numbers stop printing if it falls of the screen
    # this current one only works if there is no wrapping (I think)
    maxitems = item.max_items()
    #if the number is at the middle of the screen then make sure to only scroll so much
    if pos < (maxitems ) // 2 :
        #I don't understand why but for some reason I have to subtract 2 from this for it to work
        stoppoint = maxitems - 2
    #if everyting dosen't fit in one screen then make sure it stops putting down lines so that the
    #hilighted object is in the middle of the screen
    else :
        stoppoint = pos +  (maxitems) // 2
    #if the stoppoint is larger than max items then it dosen't matter

    #print the branches and hilight where the browser is at.
    for num,branch in enumerate(twilight.folder_tree(folder)):
        if num == pos :
            item.display_string(branch+'\n',hilight=True)
        #make it stop when the item is in the middle
        elif num == stoppoint:
            item.display_string(branch+'\n')
            break
        else:
            item.display_string(branch+'\n')
        item.refresh_screen()
def curses_askkey(item):
    """returns item.screen.getkey()"""
    return item.screen.getkey()

def curses_generic_add_item(browserholder,method='add_item',*,option=''):
    """This function takes user input and then creates a new thing in a folder at browser's position

    This function also clears the screen before going
    This function never directly references browserholder.screen
    so it is fine to use it for non curses functions. 

    Arguments:
        browserholder :
            An object that can hold a FolderBrowser object and a screen

            read twilight.BrowserHolder for more information

        method:
            the method called on the browser object that adds the item into the folder list. 

            The method is usually add_item or append_item , but it could be any method in the 
            browser argument so long as it takes one item as input.

    Keyword args :
        option :
            an optional paramiter that will skip the part where it asks the user what type of object they
            want to add to the list.

    """
    ##Fix Later Note
    #This function looks a little bit ugly right now so it should be cleaned up.
    #specifically when the user adds an item It produces a newline twice so everything is 'reddit spaced'
    #Also the first thing on a screen is a newline which looks ugly.
    #It could also be cool if I just made it so it started writing where the cursor was but that would take some time to write
    #and it could be confusing when it is in append mode. 
    browserholder.clear_screen()
    #If the option is empty then ask the user for the type of item they want to enter
    if not option:
        option = browserholder.get_key('\nwhat type of item would you like to enter (folder=e,todofolder=w,todo=q): ')

    #folders     
    #add a folder to the list
    if option == 'e':
        name = browserholder.get_string("\nenter your folder's name, Put a $ at the front of it if you want it to be sequential: ")
        #remove the $ on the front if it is there and make the folder sequential. 
        if name.startswith('$'):
            folder = twilight.Folder(name[1:],sequential=True)
        else :
            folder = twilight.Folder(name)
        #run the method on the browser object with folder as an argument
        #this usually either inserts a folder at its current position or it appends it to the bottom of the list
        getattr(browserholder.browser,method)(folder)
    #todos 
    #add a todo item to the list
    elif option == 'q':
        #get the necessesary requirements for a todo item 
        event = browserholder.get_string('\nenter the name of your event: ')
        #points = browserholder.get_string('\nhow many points in this todo?: ') # removed this because it got annoying
        points = '0' 
        
        #this code is somewhat necrotic because it was made to check if points was valid
        #Now that points is zero always that isn't really a problem
        #I am keeping it in in case I ever want to change the default behavior back to what it used to be
        if points.isdigit():
            points = int(points)
            getattr(browserholder.browser,method)(twilight.ToDoItem(event,points))
        else :
            browserholder.get_key('you cannot continue because points was not a positive integer, please try again')
    #todofolders 
    #add a todofolder to the list
    #this command is essentailly a combination of the two above commands, 
    #where it takes an event and points, and then
    #checks to see if the event has $ in front of it and then it makes a todo folder
    #with those arguments.
    elif option == 'w':
        #ask for necessary attributes of the todo folder
        event = browserholder.get_string("\nenter your todofolders event, Put a $ at the front of it if you want it to be sequential: ")
        #points = browserholder.get_string('\nhow many points in this todofolder?: ')  #removed this because it is annoyinng
        points = '0'
        #either create a sequential todofolder with event and points as attributes
        #or a regular folder with event and points as attribes, it will be sequential
        #if the name starts with a $.
        if points.isdigit():
            points = int(points)
            if event.startswith('$'):
                todofolder = twilight.ToDoFolder(event[1:],points,sequential=True)
            else :
                todofolder = twilight.ToDoFolder(event,points)
            getattr(browserholder.browser,method)(todofolder)
        else :
            #this is obsolete but I am keeping it in incase I want to change the default behavior back to what it used to be
            browserholder.get_key('\nyou cannot continue because points was not a positive integer, please try again')

def curses_new_list(browserholder,foldername='',filename='',seq=False) :
    """A function that makes a new todo list

    If foldername and filename are left blank it will prompt the user to type them.
    If sequential is set to True then the initial folder in the todo list will be True
    It also needs a screen to print its prompts on. 

    Arguments :

        browserholder:
            A BrowserHolder object that holds a screen where the text should be at.

        foldername:
            The name of the initial folder that the todo list has 

        filename :
            The name of the file that the todo list is saved in 

        sequential :
            If true then the innitial folder attribute is sequential 
            (this attribute does nothing right now but It will eventually be integrated with a calendar app)
    """
    return twilight.folderbrowse(twilight.Folder(foldername,sequential=seq),browserholder.screen,browserholder.functions,browserholder.prompts,filename,)



def curses_get_string(browserholder,prompt=''):
    """A function used to ask the user for a string with echos turned on and then turning them off at the end

    Arguments :
        browserholder :
            an instance that holds a screen and a folderbrowser. 
            read twilight.BrowserHolder for more information

        prompt :
            A prompt telling the user what to enter

    Warnings :
        This will change the state of the curses program to make it noecho
        This could be problematic if you want echo on by default.
    """
    #Add the prompt to the screen
    if prompt :
        browserholder.display_string(prompt)
    #turn on echoing so the user see what they are typing
    browserholder.enter_input_mode()
    #decode the bytes in the string to unicode
    final = browserholder.screen.getstr().decode(encoding="utf-8") 
    #curses.noecho() might be problematic because if I set echos on in some other part of the program
    #then it will turn it off when I run this function. I may want to check to somehow revert 
    #the echos back to its previous state rather than making it noecho, It might get fixed eventually
    browserholder.exit_input_mode()
    return final

def curses_edit_todo(item,browserholder):
    """Lists the items editable from item.seed and then takes user input to allow the user to edit a todo

    Arguments :
        
        item :
            An object with the .seed method that is to be edited 

        browserholder :
            an object that holds the screen, and folderbrowser
            Used for displaying text. 
            Look at twilight.BrowserHolder for more information
    """
    browserholder.clear_screen()
    #User editing loop
    #messsage is printed at the end after the screen is cleared
    while True :
        message = ''
        #filter out the attributes that shouldn't be edited from item
        keys = tuple(filter(twilight.is_printworthy,item.seed))
        #print the contents of the directory with numbers in front of them
        for num,name in enumerate(keys) :
            browserholder.display_string(f'{num}: {name} {item.seed[name]}\n')
        #ask for a number from the user and then check if it is a valid input
        action = browserholder.get_string('enter the number for the attribute you would like to edit: ')
        if action in ('','\n','z'):
            return
        #check if the action is a digit and if it is then see if the digit converted to an integer
        #is within the keys function, if it is then get the item and ask what it should be 
        #changed to. The logic inside dictates how it should be changed, if the item is a bool
        #it should just flip the result, if it is an integer, it should make sure the user inters a number
        #Otherwise set the new attribute to a string from the user.
        elif action.isdigit() and int(action) < len(keys) :
            key = keys[int(action)]
            finitem = getattr(item,key)
            if key == 'points':
                new = browserholder.get_string('\nenter a number to change points to: ')
                if new.isdigit():
                    setattr(item,key,int(new))
                else :
                    browserholder.clear_screen()
                    message = 'that is not a valid number\n'
            elif type(finitem) == float :
                new = browserholder.get_string(f'\nenter a number to change {key} to: ')
                #I really hate using try statements but I feel like this makes more sense than
                #using regex or using a large if + and statement with partition
                try :
                    new = float(new)
                except ValueError :
                    browserholder.clear_screen()
                    message = 'that is not a valid number\n'
                else : 
                    setattr(item,key,new)

            elif type(finitem) == bool :
                setattr(item,key,not finitem)
            else : 
                new = browserholder.get_string(f'\nenter a new value for {key} : ')
                setattr(item,key,new)
        else :
            message = 'invalid action, press z to exit\n'
        browserholder.clear_screen()
        browserholder.display_string(message)

def curses_can_scroll(startscreenholder,canscroll=True):
    """calls scrollok with canscroll as an argument, If this is False , It may cause an error"""
    startscreenholder.screen.scrollok(canscroll)



curses_functions = { 
        'clear_screen'     : curses_clear,
        'max_items'        : curses_max_items,
        'draw_screen'      : curses_draw,
        'display_string'   : curses_display_string,
        'refresh_screen'   : curses_refresh,
        'get_key'          : curses_askkey,
        'new_list'         : curses_new_list,
        'enter_input_mode' : curses.echo,
        'exit_input_mode'  : curses.noecho,
        'get_string'       : curses_get_string,
        'add_item_generic' : curses_generic_add_item,
        'edit_a_todo'      : curses_edit_todo,

        }

curses_start_functions = {
        'can_scroll'       : curses_can_scroll  ,
        'get_key'          : curses_askkey ,
        'get_string'       : curses_get_string,
        'refresh_screen'   : curses_refresh,
        'display_string'   : curses_display_string,
        'clear_screen'     : curses_clear,
        'enter_input_mode' : curses.echo,
        'exit_input_mode'  : curses.noecho,
        'new_list'         : curses_new_list,
        }
cursesprompts = {'get_action' : '''
    would you like to:
    print the contents of the todo directory (press p)
    delete a todo list (press d)
    archive a todo list (press a) 
    make a new list? (press u) 
    open an old list (press o)
    quit press (Z)

    '''
}

            
def start_program(stdscr,options=dict(),filename=None):
    """begins the start program with stdscr as the screen argument in twilight.run_start, 

    used in conjunction with curses.wrapper

    Arguments 
    ----------
    stdscr : 
        the screen where the text will be printed
    """
    
    ##This used to be used. If I need to fall back to this then I will uncomment it and then comment everything in
    #make the colors whiter and blacker than usual if possible 
    #if curses.can_change_color() : 
    #    curses.init_color(curses.COLOR_WHITE,999,999,999) 
    #    curses.init_color(curses.COLOR_BLACK,0,0,0) 

    #curses.init_pair(1, curses.COLOR_BLACK,curses.COLOR_WHITE , )
    #colorpair = curses.color_pair(1) 

    #make the screen white 
    #stdscr.bkgd(' ',colorpair)
    
    #Change the colors so that twi uses the default colors for the terminal
    #https://docs.python.org/3.8/library/curses.html#curses.use_default_colors
    curses.use_default_colors()
    #loop through all of the colors set them to the defaults.
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)

    twilight.run_start(stdscr,twilight.STARTKEYMAP,twilight.browserkeymappings,curses_start_functions,curses_functions,cursesprompts,options,filename)

def main(options=dict(),filename=None) :
    """Opens up the start user interface. 

    Moves into the .twitodolists folder and then uses curses.wrapper on start_program"""
    #Move into the .twitodolists folder.
    twilight.move_to_home_directory()
    #run the main program through a curses wrapper
    curses.wrapper(lambda screen : start_program(screen,options,filename))

#Run the main program.
if __name__ == '__main__':
    main()
