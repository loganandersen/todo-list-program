#!/usr/bin/python3
#twilight.py - a todo list for the command line
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

import time
import os
import xml.etree.ElementTree as ET
import shutil 

OPTIONS = {'checkbox' : '☑☐' }

HELPTEXTFOLDERBROWSE = '''
movement keys :
h : exit the folder you are intwitodolists
k : move the cursor up
j : move the cursor down
l : enter the folder your cursor is pointing at

Item modification keys : 
i : insert any item at cursor (it will prompt for the type)
I : append any item (it will prompt for the type)

q : insert a todo item at cursor 
Q : append a todo item 

w : insert a todo folder at cursor
W : append a todo folder

e : insert a folder at cursor
E : append a folder

d : delete an item
y : paste the most recently deleted item at cursor
a : toggle a todo checkbox
A : uncheck all of the items in a todofolder
^A: check if everything in a todo folder is done and toggle its box if it is
f : view an item
F : view and edit an item

Exit keys:
o : adds a copy of a folder into the paste selection
z : exits you back to the home menu 
Z : exits you out of the program

misc keys:
p : prints the full directory in a folder tree with your position at <<<< 
s : saves the file 
? : print help text 
'''
#edit this if you want to change the key mappings
browserkeymappings = {
        'h'               : "exit_folder",
        'k'               : "cursor_up" ,
        'j'               : "cursor_down" ,
        'l'               : "enter_folder" ,
        'i'               : "generic_insert" ,
        'I'               : "generic_append" , 
        'q'               : "todoitem_insert" ,
        'Q'               : "todoitem_append" ,
        'w'               : "todofolder_insert" ,
        'W'               : "todofolder_append" ,
        'e'               : "folder_insert" ,
        'E'               : "folder_append" ,
        'd'               : "delete_item" ,
        'y'               : "paste_item" ,
        'a'               : "check_todo" ,
        ''              : "check_todo_everything" , #this is ctrl+A
        'A'               : "uncheck_all_in_folder", 
        'f'               : "view_item" ,
        'F'               : "edit_item" ,
        'o'               : "copy_item" ,
        'u'               : "create_new_list" ,
        'z'               : "exit_to_home" ,
        'Z'               : "quit_program", 
        ''              : "exit_to_home", #this is ctrl+D
        'p'               : 'print_top_directory',
        's'               : 'save_file',
        '?'               : 'print_help',
        'KEY_LEFT'        : "exit_folder",
        'KEY_UP'          : "cursor_up" ,
        'KEY_DOWN'        : "cursor_down" ,
        'KEY_RIGHT'       : "enter_folder" ,

        '\\'              : "TEST_FUNCTION", #this is always going to be used for debugging purposes
        }

#Do not change right now , It will not work if you do .
STARTKEYMAP = {
        'o' : 'open_list',
        'u' : 'new_list_user',
        'd' : 'delete_list',
        'p' : 'print_lists',
        'Z' : 'exit_program',
        'a' : 'archive_file',
        '': 'exit_program', #this is ctrl+D
        #'\\': 'crash' #used for debugging purposes
        }
def all_items_and_folders(item):
    """recursively goes through each folder in item and then returns the contents"""
    if hasattr(item,'todos'):
        for i in item.todos:
            yield i
            if hasattr(i,'todos'):
                yield from all_items_and_folders(i)

def get_all_items(item):
    """returns anything with a "done" attribute from all_items_and_folders(item)"""
    return filter(lambda x : hasattr(x,'done') , all_items_and_folders(item))
def get_name(item):
        if hasattr(item,'name'):
            return item.name
        else :
            return item.event
class Position:
    """stores a folder and a number inside of a folder

    Attributes : 
        
        directory : 
            the directory the postition is in

        index : 
            an index of directory.todos[index]

    """
    def __init__(self,directory,index):
        """sets arguments to self.argument"""
        self.directory = directory
        self.index = index 
class FolderBrowser:
    """The folderbrowser object is made to browse folders and retrieve items from them

    used by the user in conjuction with other functions to browse the list and it is also
    used automatically by some functions. 

    Attributes :
        
        directory :
            meant to represent the folder being browsed.

        landmarks :
            a dictionary that is supposed to contain string : postion pairs

            by default this dictionary contains 1 pair at the point it was instantiated at 
            "home" : Position(directory,0)

        folderindex : 
            represents the positon the folderbrowser is hovering over 

        clipoard :
            a list that holds deleted objects so they can be pasted back
    """
    def __init__(self,directory):
        """sets the following attrubutes 

        Arguments: 

            directory:
                the directory the folderbrowser is supposed to browse
        """
        self.directory = directory
        self.landmarks = {'home' : Position(directory,0)}
        self.folderindex = 0 
        self.clipboard = []
    @property
    def position(self):
        """returns a position object where the folderbrowser is at""" 
        return Position(self.directory,self.folderindex)
    def exit(self,index=0,*,errorsupress = False):
        """changes self.directory to the directories parrent directory

        This method is basically similar to cd .. 
        If it is at the very top directory then it will either throw an error 
        of return the string 'top' depending on if errorsupress is True or false

        Arguments:
            index:
                the position that the folderbrowser should exit into in the parent's .todos folder

        KeyWord Arguments :
            errorsupress = False :
                If enabled the program will not raise an exeption and will return 'top'
        """
        
        #checks if it has the folder attribute (the parent folder)
        #and then checks if if that folder attribute is not equal to None
        #the reason why it checks the first thing is because some old lists 
        #have no .folder attribute so it is necessary to prevent crashing for
        #those old lists. This should be optimized once I make it so I am no
        #longer using the pickle module. If the folder is None then it means the
        #folderbrowser is at the top directory. (because it has no parents)

        #this code may be able to be changed since I am no longer using the pickle module
        if hasattr(self.directory, 'folder') and self.directory.folder != None:
            self.directory = self.directory.folder
            self.folderindex = index
        else :
            if errorsupress :
                return 'top'
            else :
                raise Exception('reached top level directory')
    def search(self,term,*,getter = get_name):
        """looks for a term within the of the items returned by getter function (default is getname)

        WARNING:
        this is not being used right now and may be broken
        This only does a shallow search I may create a deep search method later"""
        beginningitems = self.directory.todos
        items = map(getter,beginning_items)
        items = enumerate(items)
        filtereditems = tuple(filter(lambda x : term in x[1], items))
        #This last statement creates a filtered list of beginning items by getting the index of the items from enumerate.
        finalitems = [beginningitems[i[0]] for i in filterediitems]
        return finalitems
    def jump(self,position):
        """jumps the FolderBrower to a position specied by a position object"""
        self.directory = position.directory
        self.folderindex = position.index
    def go_to_landmark(self,name):
        """enters into a defined landmark 

        the name argument should represent a key to the landmark dictionary"""
        self.jump(self.landmarks[name])
    def peek(self,ammount = 1):
        """looks ahead or behind one line to check if it can move forward 

        returns True the browser can move forward 
        returns False if the browser cannot move forward"""
        return (self.folderindex + ammount > -1) and (self.folderindex + ammount < len(self.directory.todos))
    def forward(self,ammount = 1,*,errorsupress = False):
        """hovers over the next item in a folder by incrimenting the index
        
        Use a number to repeat more than once
        use errorsupress to return end instead of raising an exeption when you hit the end of the directory"""
        len(self.directory.todos) - 1 >= self.folderindex + ammount 
        if len(self.directory.todos) - 1 >= self.folderindex + ammount : 
            self.folderindex += ammount 
        elif errorsupress: 
            return 'end'
        else:
            raise Exception('Hit end of directory after trying to go forward')
    def backward(self,ammount = 1,*,errorsupress = False):
        """hovers over the previous item in a folder by decrementing the index variable
         
        Use a number to repeat more than once
        use errorsupress to return end instead of raising an exeption when you hit the beginning of the directory"""
        if 0 <= (self.folderindex - ammount) : 
            self.folderindex -= ammount 
        elif errorsupress: 
            return 'front' 
        else:
            raise Exception('Hit beginning of directory after trying to go backward')
    def mark(self,name,*,postion:Position = False):
        """adds a mark into the landmark dictionary at your current position 

        Arguments:
            name:
                represents the key to be added to the landmark dictionary

        KeyWord Arguments:
            position:
                represents the position to be added into the landmarks dictionary
                if it is not specified self.position will be used instead
        """ 
        if position :
            self.landmarks[name] = position
        else :
            self.landmarks[name] = self.position
    
    def get_item(self,*,errorskip=False):
        """returns the item the browser object is hovering over
        
        if errorskip is True and the directory folderbrowser is on is 
        empty then it will return self.directory instead""" 
        #the first part is to fix an error with the printdir function
        #it works because it gives the folder instead of the item if the 
        #browser is at an empty item. Be careful if you change this
        #check to see if the printdir function breaks by going into an 
        #empty folder within a folder and pressing 'p'
        if errorskip and len(self.directory.todos) == 0 :
            return self.directory 
        return self.directory.todos[self.folderindex]

    def add_item(self,item):
        """adds an item into the directory at the browsers current position"""
        self.directory.insert_item(item,self.folderindex)
    def append_item(self,item) :
        """appends an item to the bottom of the folder the browser is in"""
        self.directory.append(item)
    def absolute_postion(self,directory = None):
        """gives a number that tells you where you are on a folder
        
        The default directory is the home directory
        The position is as if you went into every folder and then 
        it goes in the folder and when it gets to the end it exits
        """
        if directory is None :
            directory = self.landmarks['home'].directory
        for i,j in enumerate(all_items_and_folders(directory)) :
            if j is self.get_item(errorskip=True):
                return i
    def delete(self):
        """removes the item the folderbrowser is under and stores it in clipboard"""
        self.clipboard.append(self.get_item())
        self.directory.delete(self.folderindex)

    def copy(self):
        """adds a copy of the selected item into clipboard"""
        self.clipboard.append(self.get_item().copy())
    
    def paste(self,*,errorsupress=False):
        """places the last deleted item and then removes it from the clipboard"""
        if len(self.clipboard) != 0 :
            self.add_item(self.clipboard.pop())
        elif errorsupress : 
            return 'noclip'
        else :
            raise Exception('pop from empty list')


def folder_tree(folder):
    """takes a folder or todo folder and returns an iterable of many strings that are a human readable version of the folder as if you called tree on it"""
    def done_check(item,checkbox='☑☐'):
        """returns a checkmark if an item is done returns an empty box if an item is not done 

        returns an empty string if an item does not have done"""
        if hasattr(item,'done'):
            if item.done : 
                return checkbox[0] + ' '
            return checkbox[1] + ' '
        return ''
    def recursor(foldr,aggrigator = ''):
        """Yeilds a series lines containing the foldername and a checkmark after it """
        browser = FolderBrowser(foldr)
        #skip folders that have no items in them 
        #otherise go through and return their names
        if len(foldr.todos) != 0: 
            while browser.peek():
                yield aggrigator + '├── ' + get_name(browser.get_item()) + ' ' +  done_check(browser.get_item(),OPTIONS['checkbox'])
                if hasattr(browser.get_item(),'todos'):
                    yield from recursor(browser.get_item(),aggrigator + '│   ')
                browser.forward()
            yield aggrigator + '└── ' + get_name(browser.get_item()) + ' ' + done_check(browser.get_item(),OPTIONS['checkbox'])
            if hasattr(browser.get_item(),'todos'):
                yield from recursor(browser.get_item(),aggrigator + '    ')

    yield f'{get_name(folder)} {done_check(folder)}'
    yield from recursor(folder)

def get_done_items(folder):
    """takes a folder object and returns an iterable that contains all of the todoitems and todofolders"""
    return filter(lambda x : x.done, get_all_items(folder))

def set_all(folder,value) :
    for i in get_all_items(folder) :
        i.done = value

def sum_points(folder):
    """looks at all of the todos in a folder and then returns the sum of the points"""
    items = get_done_items(folder)
    return sum(map(lambda x : getattr(x,'points'),items))

class ToDoItem:
    """An object meant to represent a thing that the user has to do

    Attributes :
        
        event : str
            Meant to represent the name of the event that the user plans to do

        points : int 
            Meant to represent the utility gained from doing an action

            Has no functionality as of nod but will be used for priority in the calendar app

        done : bool 
            represents if the todo item has been done

        folder : Folder, ToDoFolder
            the parent directory the todoitem is held in

        timestamp : float
            represents the time whan an item was done 
    """
    def __init__(self,event,points,*,done=False,timstamp=None):
        """takes event and points and then sets them to the todoitems attributes

        Arguments : 

            event : str
                represents the name of the event that the user wants to do
            
            points : int
                represents the utility gained from doing an action 

        KeyWord arguments : 

            done : bool 
                represents if the todo has been done
        """
        
        self.event = event
        self.points = points
        self.done = done
        self.folder = None
        self.timestamp = None
        self.description = ''
    def toggle(self):
        """sets self.done to not self.done and then marks when it was done by changing self.timestamp"""
        self.done = not self.done
        self.timestamp = time.time()
    def __repr__(self):
        """returns a representation of the object as a string"""
        return f'ToDoItem({self.event!r},{self.points!r},done={self.done!r})'
    @property
    def seed(self):
        """returns a dictionary representation of the object""" 
        return {'event' : self.event , 
                'points' : self.points , 
                'done' : self.done , 
                'folder' : self.folder , 
                'timestamp':self.timestamp, 
                'description':self.description, 
                } 

    @classmethod 
    def from_seed(cls,seed:dict):
        """takes a seed object (dictionary) and then makes the instance from it

        arguments :
            seed : 
                a dictionary that is used to represent the ToDoItem object
        """
        #create a minimal version of the item
        item = cls(seed['event'] , seed['points'])
        #add in all of the attributes
        for key in seed :
            setattr(item,key,seed[key])
        return item

    def copy(self,changefolder=False) :
        """return a copy of the todoitem

        if changefolder is set to a different folder object
        then the copy's .folder attribute will be set to
        changefolder. 

        Arguments :
        ------------
        changefolder
            the folder that the copy should have. 
            If it is set to false (default) then the folder
            will not change for the copy.
        """
        copy = type(self).from_seed(self.seed)
        if changefolder != False : 
            if hasattr(changefolder,'todos') or changefolder == None : 
                copy.folder = changefolder 
            else : 
                raise TypeError("changefolder value was set to an invalid type. \n" +
                        "Any type for changefolder must have the .todos attribute" )
        return copy



class Folder:
    """An object that is used to hold many ToDoItem, ToDoFolder and Folder objects.

    Attrubutes :
        name : str
            the name of the folder
        
        todos : list
            contents of the folder stored as a list
        
        folder : Folder, ToDoFolder
            the parent folder that Folder is held inside of. 
        sequential : bool 
            represents if the items in the folder should be done in order
    """


    def __init__(self,name:str,*todos,sequential=False):
        """Gives the many attributes to the Folder Object 
        
        name , todos, and sequentail are generated by the arguments. 
        folder is set to None by default but it can turn into a Folder
        object or a ToDoFolder object if the Instantiated Folder is put
        in another folder.
        
        The __init__ function also runs the self.refresh_todos() method
        which changes the .folder attribute of all the items contained in
        self.todos 
        Arguments : 
            name : str 
                represents the name of the folder , is set to self.name
            todos : tuple
                a multiple paramiter argument that is turned into a list 
                and then set to self.todos. the list should contain 
                Folder objects, ToDoItem objects , and ToDoFolder Objects.
        Keyword Arguments :
            sequential :
                a boolian argument made to represent whether or not the items in 
                todos should be done in order. 
                Right now this has no use but it will eventually be used with the 
                calendar application once development of that starts.
        """
        self.name = name
        self.todos = list(todos)
        self.folder = None
        self.refresh_todos()
        self.sequential = sequential 
        self.description = ''
    def refresh_todos(self):
        """This method sets every item's folder attribute in self.todos to self

        This is done so that the items inside of self.todos know what folder is holding them.
        The primary use for this for exiting to a higher folder from inside of the folder 
        """ 
        for i in self.todos:
            i.folder = self
    def __repr__(self):
        """Returns a representation of the object"""
        #this needs to be updated with .sequential and maybe .folder
        return f'Folder({self.name},*{self.todos!r})'
    def append (self,other):
        """Adds an item into the end of self.todos and sets the items .folder attribute to self
        Arguments :
            other :
                the item that you want to append 
        """ 
        other.folder = self
        self.todos.append(other)
    def delete (self,index):
        """takes an integer 'index' and then removes that item in the self.todos list
        Arguments :
            index :
                represents the position of self.todos 
        """
        del self.todos[index]
    
    def insert_item(self,item,position):
        """inserts an item into an integer position on the list self.todos
        Arguments : 
            item: 
                the item that should be inserted 
            
            position:
                the position where item should be inserted
        """
        item.folder = self
        self.todos.insert(position,item)

    def check_done(self):
        """returns true if every item within a folder is done , false otherwise""" 
        return all(map(lambda x : getattr(x,'done'),get_all_items(self))) 

    @property
    def seed(self):
        """This returns a dictionary representation of an instance of Folder
        it is used in the edit_todos function, and may also be used in the future 
        for generating xml and ical files
        """

        return {'name' : self.name , 'todos' : self.todos , 'folder' : self.folder , 'description' : self.description} 

    @classmethod 
    def from_seed(cls,seed:dict):
        """takes a seed object and then makes the instance from it
        
        arguments:
            seed : 
                a dictionary that is used to represent the Folder object
        """
        item = cls(seed['name'] , *seed['todos'])
        for key in seed :
            setattr(item,key,seed[key])
        return item

    def copy(self,changefolder=False) :
        """return a copy of the todoitem

        if changefolder is set to a different folder object
        then the copy's .folder attribute will be set to
        changefolder. 

        Arguments :
        ------------
        changefolder
            the folder that the copy should have. 
            If it is set to false (default) then the folder
            will not change for the copy.
        """
        #Get the basic object
        copy = type(self).from_seed(self.seed)
        if changefolder != False : 
            if hasattr(changefolder,'todos') or changefolder == None: 
                copy.folder = changefolder 
            else : 
                raise TypeError("changefolder value was set to an invalid type. \n" +
                        "Any type for changefolder must have the .todos attribute" )


        #make a copy of all of the children objects so that they don't share any lists.
        #this part is actually fairly recursive. the base case for a copy method is either
        #A ToDoItem.copy (which returns returns the ToDoItem) or if copy.todos is empty
        #if copy.todos is empty then it returns a copy of the .todos list.
        newlist = [] 
        for i in copy.todos :
            newlist.append(i.copy(copy))

        copy.todos = newlist

        return copy

class ToDoFolder(Folder,ToDoItem):
    """An object that combines the functionality of a todo and the functionality of a folder 

    This object inherits the methods of a ToDoItem object and a Folder object.
    It also has some of it's own method like checkdone. Instead of having the name 
    attribute it instead has the event attribute (like ToDoItem) 
    It is meant to let the user break up tasks into smaller todo items

    
    Attributes :
        
        event : str
            meant to represent what should be done i.e. (build my house)

        points : int 
            used to represent the utility gained in accomplishing a task.

            Not implemented at the user level yet. 

        done : bool 
            used to represent whether or not the ToDo has been done

        folder : ToDoFolder,Folder,None 
            This attribute represents the parent folder that the ToDoFolder is contained in.

            If it has no parent folder then it will be set equal to None. Be sure to account for 
            This fact in the code as it could cause an error. 

        todos : list
            A list that holds the contents of the folder 
            items in the list should be ToDoItems,TodoFolders, and Folders.

        sequential : bool
            used to represent whether or not the items contained in the ToDoFolder should be done in order

            has no functionality as of now.

        timestamp : float
            represents the time whan an item was done 
    """
        

    def __init__(self,event,points,*todos,done=False,sequential=False):
        """sets the necessary attrubutes for something to be a ToDoFolder

        uses arguments to set the following attributes :
        event,points,done,todos,sequential. todos is turned into 
        a list instead of a tuple. 

        Uses Folder.refresh_todos() to make every item contained in
        todos have the todo folder instance as their folder attribute 

        Arguments:
            event :
                A string that is used to name the thing the user should do 
            
            points :
                An integer (may work with floats) that is used to represent how much points the todo is worth.

                Points are not implemened as of yet but they will probably be used in conjunction with
                the calendar app this is supposed to go with. Things with more points will be scheduled with
                higher priority.

            todos: 
                a list of things contained in the ToDoFolder object. 

                These things should be ToDoItems, Folders, and ToDoFolders.
                todos is an arbitrary argument list (variadic arguments) 
        
        Keyword Arguments :
            done : 
                A boolean that represents if the ToDoFolder has been finished 

            seqential : 
                A boolean that represents whether or not the items contained in the folder should be done in order. 

                This item is not implemented yet. It will be used for the calendar program I am making 
        """

        self.event = event
        self.points = points
        self.done = done
        self.timestamp = None

        #self.folder can change if the item is put in a folder or todo folder
        #and then it uses self.refresh_todos() 
        self.folder = None
        self.todos = list(todos) 
        #go through every item in self.todos and then set their .folder attribute
        #to self 
        self.refresh_todos()
        self.description = ''
        self.sequential = sequential
    def __repr__(self):
        """returns a representation of the folder object"""
        return f'ToDoFolder({self.event!r},{self.points!r},*{self.todos!r},done={self.done!r})'
    
    @property
    def seed(self):
        return {'event' : self.event , 
                'points' : self.points , 
                'done' : self.done , 
                'folder' : self.folder ,
                'todos' : self.todos , 
                'sequential' : self.sequential,
                'timestamp':self.timestamp,
                'description' : self.description
                } 


    @classmethod 
    def from_seed(cls,seed):
        """takes a seed object and then makes the instance from it

        arguments :
            seed :
                the seed that will be used to create a ToDoFolder object 

        """
        #create a minimal version of the item
        item = cls(seed['event'] , seed['points'] , *seed['todos'])
        #add in all of the attributes
        for key in seed :
            setattr(item,key,seed[key])
        return item

def save_list(folder,filename):
    """Uses xml module to save a folder object and then exports it as xml to filename

    Arguments :
        
        folder : 
            the object that will get 
        
        filename :
            the location of the file where xml will be dumped
    """
    def classname(item):
        """return the name of the class that item is a part of

        arguments :
            item:
                the item you want to get the class name of
        """
        return type(item).__name__

    def save_process_seed(dictionary:dict):
        """takes a seed dictionary and then returns a dictionary with he things that are unnecessary or will crash the xml removed

        arguments:
            dictionary : dict
                the dictionary that will be used to represent the item you want"""
        
        newdict = dict()
        for key in dictionary :
            if key not in ('folder','todos') :
                #I put this in here because I am unsure if I want to have iterables looked through
                if hasattr(dictionary[key],'__iter__'):
                    newdict[key] = dictionary[key]
                else :
                    #turn anything that can crash the program into a string which dosen't crash the program
                    newdict[key] = str(dictionary[key])
        return newdict

    #create a new xml root and a new xml tree 
    #with tag as folder's class name
    #also give root the attributes of folder so it can save them as xml 
    root = ET.fromstring(f'<{type(folder).__name__} />') 
    root.attrib = save_process_seed(folder.seed)
    root.text = '\n' + '  '
    tree = ET.ElementTree(root)

    def build_tree(foldr,root,indent = '  '):
        """Recursively goes through the folder object and builds the xml tree onto root.

        attributes :
            foldr :
                a todofolder or folder object that will have its elements converted into xml

            root : 
                an xml branch that will have the converted items from foldr tacked onto it

            indent :
                the level of indenation for tails of the items, used to make the xml print nicely"""

        for num,item in enumerate(foldr.todos) :
            #make every item a subelement (xml branch) for the root branch
            #and give them their seed translated into xml saveable format
            itemxml = ET.SubElement(root,classname(item),save_process_seed(item.seed))

            #add the relitive position of the item
            itemxml.attrib['POSITION'] = str(num)

            #add tails
            #if the item is the last element in foldr then make the indent smaller otherwise 
            #give the tail with a regular indent
            if num == len(foldr.todos) - 1 :
                itemxml.tail = '\n' + ' '*(len(indent)-2)  
            else : 
                itemxml.tail = '\n' + indent

            #text 
            #if the item has todos then just give it a newline for the todos to fit in
            #otherwise make it so the name of the item is the text 
            if hasattr(item,'todos') and len(item.todos) > 0:
                itemxml.text = '\n' + indent + '  '
            else : 
                itemxml.text = get_name(item)

            #If the item has its own todos then build all of the 
            #stuff for the todos under it with indent increased by '  '
            #and with the xml representation of the item as its parent folder
            if hasattr(item,'todos') :
                build_tree(item,itemxml,indent + '  ')

    #build the tree for root and write the xml to filename
    build_tree(folder,root)
    tree.write(filename)

def open_list(filename,) : 
    """Returns a todolist from an xml document describing a todolist 

    Arguments : 
        filename :
            the name of the file you would like to open
    """
    #This dictionary converts the strings in the xml documents into 
    #functions that can be used to create instance variables. 
    #The ones with lambda functions are bools, The problem was that
    #the string False would evaluate as True. 
    TYPEMAP = { 
            'ToDoItem'    : ToDoItem ,
            'Folder'      : Folder ,
            'ToDoFolder'  : ToDoFolder ,
            'event'       : str ,
            'description' : str ,
            'name'        : str ,
            'points'      : int ,
            'done'        : lambda x : x == 'True' ,
            'timestamp'   : float ,
            'POSITION'    : int ,
            'sequential'  : lambda x : x == 'True' ,
    }
    #get the tree and the root by parsing the xml document
    tree = ET.parse(filename)
    root = tree.getroot()

    def valid_seed(branch,todos=()):
        """returns a dictionary that can be used by .fromseed method to construct an object

        arguments :
            branch: 
                the branch that will be turned into an object
            
            todos:
                a list object containing the todos for the todo argument in folders and ToDofolders

        """
        newdict = dict()
        #look through the attributes , convert them into their proper types and filter out POSITION 
        for i in branch.attrib :
            if i == 'POSITION' :
                continue
            elif branch.attrib[i] != 'None':
                #find the function to convert in typemap and apply it to 
                #the string in branch.attrib to get the attribute of the 
                #correct type. 
                newdict[i] = TYPEMAP[i](branch.attrib[i])

            #Many attributes start out as None and become a differnt type
            #so this part converts things with the text 'None' as None
            else :
                newdict[i] = None

        #if branch is a Folder or ToDoFolder then give it the todos argument as its todo list
        if branch.tag in ('Folder,ToDoFolder'):
            newdict['todos'] = list(todos)
        return newdict

    def make_item(item,todos=()):
        """takes an xml branch and returns a ToDoItem, ToDoFolder, or Folder object with todos as it's todos attribute

        if the todos are unknown then use build_item instead

        arguments: 
            item :
                an xml branch item that will be converted into a ToDoItem,ToDoFolder, or Folder
            
            todos :
                a list object that will be used as the ToDoFolder or Folder's .todos attribute
        """
        return TYPEMAP[item.tag].from_seed(valid_seed(item,todos))

    def build_item(branch) :
        """takes an xml branch object, discovers the propper items for .todos and then returns a Folder,ToDoFolder or ToDoItem with the todos in

        arguments :
            branch :
                the xml branch that you would like to convert into a Folder,ToDoFolder, or ToDoItem
        """
        #If there are children in the branch
        #then turn those children into their propper items and then add those items into todos for 
        #the item you want to return. 
        if len(branch) > 0 :
            #go through and make a todo list for everything
            #numtodos contains the positions and the todo items in tuples 
            numtodos = [] 
            for i in branch :
                numtodos.append((int(i.attrib['POSITION']),build_item(i)))
            #you are not supposed to depend on xml document structure for information so sort is necessary
            numtodos.sort(key=lambda x : x[0])
            #get a list that only contains the todos instead of (todo , position ) tuples
            todos = list(map(lambda x : x[1] , numtodos))
            return make_item(branch,todos)
        else :
            #if there are no items just return an item with an empty todos list. 
            return make_item(branch)

    return(build_item(root))

# _testfolder was used to test the folderbrowser and is currenly not being used
# This may be removed at a later date
_testfolder = Folder('anime',
                    ToDoItem('1',1,done=True),
                    ToDoItem('2',2,done=True),
                    Folder('3',
                           ToDoItem('4',4),
                           ToDoItem('5',8,done=True),
                           Folder('6',
                                  ToDoItem('7',256,done=True),
                                  ToDoItem('8',512),
                                  Folder('6',
                                      Folder('6',
                                          ToDoItem('7',256,done=True),
                                          ToDoItem('8',512)
                                          ),
                                      ToDoItem('7',256,done=True),
                                      ToDoItem('8',512),
                                      Folder('6',
                                          ToDoItem('7',256,done=True),
                                          ToDoItem('8',512)
                                          )
                                      )
                                )
                        ),
                    ToDoFolder("9",16,
                               ToDoItem('10',32,done=True),
                               ToDoItem('11',64,done=True),
                               done=True
                            ),
                    ToDoItem('12',128,done=True),
                    )

#This is broken for now But it may be added in later
#def scrollmode(screen,option=None): 
#    screen.addstr('you are in scroll mode press j and k to move up and down press any other key to exit')
#    if not option :
#        option = screen.getkey() 
#    while option in 'jkJK' :
#        if option in 'jJ':
#            screen.scroll(1)
#        elif option in 'kK' : 
#            screen.scroll(-1)
#        screen.refresh()
#        option = screen.getkey()




def is_printworthy(name):
    """a function used to exclude attributes from .seed method that should not be edited

    This function is used to tell what should be printed in edit_todo and the p option in folder_browse
    For it to work , it should be used in conjunction with the filter function. 

    Arguments:
        name : a single key from a dictionary usually from the .seed method"""
    return name not in ('folder','todos')


#keymappings keymappings relates certain keys to certain functions 
#this will be used to replace the elif monster that is folderbrowse 
class BrowserHolder:
    """Used to abstract away how things are displayed to a user, while keeping the controlls the same
    
    This class is used as an abstraction to define many different implementations of twilight
    The current implementations are twitext (uses print statements and input statements), twicurses
    (uses the python curses module) and twigui (which uses the tkinterr module). 
    It takes many arguments to create an implementation of twilight.
    below follows a terse description of the arguments required to form an implementation of twilight
    read the __init__ function for a more detailed description of the arguments.

    Each time the .go method is called the BrowserHolder will take an input and 
    run the corrosponding function.Please refer to folderbrowse to see how 
    BrowserHolder can be implemented to take user input till the user wants to stop.

    If a user level method returns something then it will either be returning an error message or
    it will be telling folderbrowse to do something. 


    Arguments :
    ------------------------------------------------------------------------------------
    folder :  
        folder is the folder the folderbrowser is browsing, as of now 
        the folder is always a Folder object returned from the open_list function. 

    screen :
        screen is the screen where text will be displayed. It is not directly referenced
        by the methods contained in BrowserHolder, rather it is to be referenced only by 
        the functions contained in the functions dictionary.

    keymap :
        a dictionary that translates commands (as of now just single characters) to function names (strings)

    functions :
        a dictionary that relates names of functions to actual concrete functions. This allows for the 
        programmer to define how strings are displayed. 

    prompts :
        a dictionary that relates single names to long strings of text.
        as of now It is only used for the get_action prompt

    filename :
        the name of the file being opened . If it is set to none you can browse a folder but
        saving it will cause a crash. 


    Attributes 
    -----------------------------------------------------------
    folder :
        the folder being browsed

    screen : 
        the place where text is displayed

    filename : str
        the name of the file that the xml todo list will be saved

    keymap : dict
        translates commands to function names

    functions : dict
        a dictionary of functions to do many operations according to the screen type

    prompts : diict
        a dictionary that gives abbreviations for long paragraphs of text

    jumps : list
        a list that contains positions where the user used to be. This is used for exiting. 

    browser : FolderBrowser 
        a folderbrowser object that is controlled by the user 

    topdir : 
        the highest directory in the folder tree 
    """ 
    def __init__(self,folder,screen,keymap,functions,prompts,filename=None,):
        """takes a large ammount of arguments and initializes the BrowserHolder instance for browsing and taking user input

        The last function run by __init__ is start browsing so also read the docstring for that.
        

        Arguments 
        -----------
        folder :
            folder is the folder that the user will browse. As of now It is either taken from the open_list function or 
            taken from the new_list function. 

        screen :
            the screen can be any object intended to display text. It is never directly 
            referenced in the code and should only be referenced by the functions contained 
            in self.functions. 

        keymap : dict
            this object is a dictionary that maps single letters to method names . 
            Each function name should be a method of folderbrowse , otherwise the
            program can crash. Methods that are to be put in keymap will be called 
            "User Level Methods" in their docstrings. 
            
            here is a quick discrption of the user level methods 
            all of these should be in a keymappings dictionary as strings  
            --------------------------------------------------------------

            exit_folder : makes the browser use the parent folder of the folder it is in 
            
            cursor_up : makes the cursor go up one item on the todo list. 
            
            cursor_down : makes the cursor go down one item on the todo list
            
            enter_folder : makes the browser browse a child folder that is selected under the cursor
            
            generic_insert : takes user input to get which item type it should add and then adds the item where the cursor is at

            generic_append  : takes user input to get which item type it should add and then adds the item at the bottom of the todo list

            todoitem_insert : adds a todo item to where the cursor is at. asks user for attributes. 

            todoitem_append : adds a todo item to the bottom of the todo list, asks user for attributes.

            todofolder_insert : adds a todo folder to where the cursor is at, asks user for attributes.
            
            todofolder_append : adds a todofolder to the bottom of the list, asks user for attributes. 
            
            folder_insert : adds a folder to where the cursor is at, asks user for attributes.

            folder_append : adds a folder to the bottom of the todo list, asks user for attributes.

            delete_item : removes the item where the cursor is at from the todolist.

            paste_item : adds the last deleted item to the todo list where the cursor as at.

            check_todo : sets the selected todoitem's .done attribute to   not self.done

            check_todo_everything : looks at a todofolder and sets it's done attribute to True if all the items in it are checked done. otherwise set it to false.

            uncheck_all_in_folder : unchecks all of checkmarks within the folder 

            view_item : list the attributes of an item to screen
            
            copy_item : copy the item the user is hovering over into the deleted items list

            edit_item : list the attributes of an item to screen and then get user input to change them.

            open_old_list : asks for user input and begins browsing a list stored in ~/.twilight/twitodolists

            create_new_list : makes a new list in ~/.twilight/twitodolists and then begins browsing it

            exit_to_home : goes into a startholder input loop. 

            quit_program : closes the program 

            print_top_directory : print the entire todolist 

            save_file : saves the file as its filename in ~/.twilight/twitodolistss

            print_help : displays the buttons the user can press and what happens when they are pressed 
            
            TEST_FUNCTION : used for testing new features. Should do nothing in user versions of the program

            
            Example of a proper keymap dictionary
            
            For the sake of brevity this dictonary will not have all 
            of the commands. Let it be noted that the programmer can
            choose which functions xe would like to put in. 
            -------------------------------------
            {
                'h' : 'exit_folder',
                'j' : 'cursor_up',
                'k' : 'cursor_down',
                'l' : 'enter_folder',
            }

        functions : dict
            This is a dictionary that contains many functions related to displaying and recieving text. 
            It is used to implement certain bottom level commands so that the programmer does not have to 
            write unique functions for each different types of screens. 

            The needed functions for an instance of BrowserHolder are listed below
            with a terse discription of what they should do. and what arguments they should take. 
            -------------------------------------------------------------------------------------

            get_key(browserholder): 
                get_key should take user input and then return a string representing a single character
                it should return the first key pressed by the user. 

            get_string(browserholder,prompt=''):
                get_string should display the prompt to the user and then make the text input visible to the user
                while the user's text is visible it should allow the user to type an arbitraily long string of text. 
                when the user is done it should return the text typed by the user. 

            refresh_screen(browserholder):
                refresh_screen should make all text sent to be added to the screen visible.
                It should do nothing if that is not applicable. (such as in twitext.py) 
            
            display_string(browserholder,string:str,hilight=False,message=False):
                display_string should take a string and a boolian as an input and then
                make it so the user can see the text in the string. 
                If hilight is True then it should indicate to the user that the string is 
                different from the other ones. As of now hilight is just used for showing where the 
                cursor is on the todolist. 

                If message is true then it can put the message in a special place where it is more easily seen by
                the user. As of now this is only used in twigui 

            clear_screen(browserholder):
                clear_screen should remove all items from the screen to allow new items to
                be displayed. If it isn't applicable to the current implementation (such as
                twitext.py) then it should do nothing. 

            draw_screen(browserholder,folder,clear=True):
                draw_screen should take a folder (or todofolder) object and then iterate through
                each of the elements in its .todos attribute. It should display the names and donness status
                of the items. It should also hilight the item that the cursor is on. It should also display
                any the contents of any folder within folder's .todos attribute. 

                If possible this should use other methods from browserholder rather than using unique screen 
                methods 

            max_items(browserholder):
                returns the ammount of strings that can be displayed on a screen. If not applicable it should 
                simply return a large number.
            
            enter_input_mode():
                this should make it so the user can see what they are typing. 

            exit_input_mode() :
                this should make it so the user cannot see what they are typing 
            
            new_list(browserholder,foldername='',filename='',seq=False) :
                this should ask the user for a filename and foldername and then run folderbrowse on an empty
                Folderobject with foldername as it's name and, the current screen, functions and prompts. It should also have
                filename as the filename for folderbrowse.
                
                It should also return any output from folderbrowse 

                Look at folderbrowse for more information. Also look at curses_new_list on twicurses.py for an implementation. 

            add_item_generic(browserholder,method='add_item',*,option=''):
                this should take user input and then appennd an item to the todo list the user is in.
                If method is add_item then it should insert the todo at where the cursor is 
                If the method is append_item then it should append the todo Item at the bottom of the list. 
                The first piece of user input should be to select which item the user wants to add, Unless
                option has been assigned a value. If option has a value then it should skip past the part 
                where it asks the user and assume it is adding what the option specifies. After the type of item
                is selected, it should ask the user necessary attributes needed to create the item the user wants. 
                After the items have been created it should append or insert them in the todo list. 

                if possible this function should use other methods of browserholder rather than directly referencing
                browserholder.screen
                
            edit_a_todo(item,browserholder):
                this function should list the attributes avalable to edit by the user and then ask the user to pick which one to edit
                It should then ask the user to type in the new value for the item and then change the value of the item to whatever 
                was typed in (unless that would be improper for the attribute to have). 

                if possible this function should user other methods of browserholder rather than directly referencing browserholder.screen
                

            Example of a proper functions dictionary :
            for the sake of berevity this will not list every function needed
            But for this to function all of the above functions listed should be in 
            the dictionary. 
            Look at twicurses.py curses_functionns , and twitext.py's text_functions 
            for more fleshed out dictionaries. 
            -------------------------------------------------------------------------
            {
                'get_key'        : example_get_key,
                'refresh_screen' : emptyfunction,
                'display_string' : example_display_string ,
            }

        prompts : dict
            A dictionary that relates small strings of text to a large paragraph of text. 
            As of now the only prompt required is 

            'get_action'

            just make a dictionary with one key 'get_command' and then the prompt to get
            the command and you should be fine.

            this dictionary is shared between BrowserHolder and StartHolder. 

            Example
            --------
            {
                'get_action' : ''' the
                quick brown fox jumped
                over the lasy dog''',
            }

        filename : str
            the name of the file that the folder will be saved as if the user prompts for it to save. 

        """
        self.folder = folder
        self.screen = screen
        self.filename = filename
        self.keymap = keymap
        #functions is used to store necessary implementation functions for different output types 
        self.functions = functions
        self.prompts = prompts
        self.start_browsing()

    def start_browsing(self):
        """clears the screen , sets the values for self.jumps , self.topdir, and self.browser andd then prints the folder's todos"""
        #clear the screens
        self.clear_screen()
        self.refresh_screen()
        #Define the browser that the user uses to browse the file
        self.browser = FolderBrowser(self.folder)
        #jumps is a list of integers denoting the different indexes where the browser used to be
        #It is added onto when the user enters a folder and ,
        #popped from when the user leaves the folder.
        self.jumps = []
        #Topbrowser is a throwaway browser that is used to find a top folder.
        #This is used incase folderbrowse is called on a folder that is not at
        #the top directory. This is important because Knowing where the topdirectory
        #is can help avoid crashing while trying to exit a folder. 
        topbrowser = FolderBrowser(self.folder)
        #This loop makes the topbrowser go to the very Top of a directory thereby finding the highest folder
        #Afterwards the location of topbrowser is stored in topdir
        while topbrowser.exit(errorsupress = True) != 'top': pass
        self.topdir = topbrowser.directory
        #Print the directory for the first time.
        self.draw_screen(self.folder)

    def invalid_action(self):
        """tells the user that they made an improper move"""
        return 'that is not a move, press ? for help'

    def go(self):
        """asks for user input, run the action associated with that letter and print screen

        This function uses keymap to translate the letters into the desired functions and then runs them.
        After that it takes any message and then it will check to see if the message is a tuple or string
        If it is a string it will display the string. if the message is a tuple then it will check
        if the first number is exit and if it is It will tell folderbrowse to exit. """

        act = self.get_key('enter an action: ')
        message = getattr(self,self.keymap.get(act,'invalid_action'))()
        #The message variable is printed on the screen at the end of the loop.
        #It can also be printed in a special container such as in the gui implementation
        #It is primarily used if there is incorrect input
        #print the directory (note every time the screen is printed, it will clear it)
        self.draw_screen(self.browser.directory)
        #add any error messages to the end after the screen has been printed.
        if message :
            if type(message) == tuple :
                if message[0] == 'exit':
                    return ('exit',message[1])
            elif type(message) == str :
                self.display_string(message+'\n',message=True)

    def get_key(self,prompt='',message=False):
        """prints the prompt and then returns a user key (Uses functions dict)"""
        #I am unsure if i want it to be like this. I may want to put self.display_string in the get_key function
        if prompt :                  
            self.display_string(prompt,message=message)
        return self.functions['get_key'](self)
    def get_string(self,prompt=''):
        """uses functions dict to return a user typed string"""
        return self.functions['get_string'](self,prompt)
    def refresh_screen(self):
        """uses functions dict to make added text visible"""
        self.functions['refresh_screen'](self)
    def display_string(self,string:str,hilight=False,message=False):
        """uses functions dict to make a string visible to the user

        If Hilight is true then the text will be made to look different from 
        regular text
        
        If message is True then the text will be put in a special area where messages go
        (In some implementations this is not a feature) 
        """
        self.functions['display_string'](self,string,hilight,message)
    def clear_screen(self):
        """uses functions dict clear all elements on a screen"""
        self.functions['clear_screen'](self)
    def draw_screen(self,folder,clear=True):
        """uses functions dict to display self.browser.directory to user's screen"""
        self.functions['draw_screen'](self,folder,clear)
    def max_items(self):
        """uses functions dict to get the maximum ammount of strings that can fit on a screen"""
        return self.functions['max_items'](self)
    def enter_input_mode(self):
        """uses functions dict to make all text the user enters visible"""
        self.functions['enter_input_mode']()
    def exit_input_mode(self) :
        """uses functions dict to make all text the user enters invisible"""
        self.functions['exit_input_mode']()
    def new_list(self,filename='',foldername='',seq=False) :
        """uses functions dict to get a filename and foldername from the user and then starts browsing that new folder"""
        self.functions['new_list'](self,foldername,filename,seq)
    def add_item_generic(self,method='add_item',*,option=''):
        """uses functions dict to add a new item to a todo list

        It should support the following options and methods
        ---------------------------------------------------
        methods : 'add_item' , 'append_item' 

        options : 'q' , 'w' , 'e'

        """
        self.functions['add_item_generic'](self,method,option=option)
    def edit_a_todo(self,item):
        """uses functions dict to change a value of a user selected item"""
        self.functions['edit_a_todo'](item,self)

    #start of user functions

    def enter_folder(self) :
        """enters the folder the user is hovering over

        if the user tries to enter a folder that dosen't exist then it will 
        return 'that is not a folder' instead """
        #check to make sure the directory has anything in it to avoid index error
        if len(self.browser.directory.todos) != 0 :
            #add the position of the folder you are at into jumps
            self.jumps.append(self.browser.folderindex) ### I may want to change this so that it is in the IF statement and then I wouldn't need to pop in the else statement
            #check if what you are looking at is a folder 
            if hasattr(self.browser.get_item(),'todos'):
                #go into the folder
                self.browser.jump(Position(self.browser.get_item(),0))
            else : 
                #if what you are looking at isn't a folder then remove the jump index
                #and display error message 'that is not a folder'
                self.jumps.pop()
                return 'that is not a folder'
    def exit_folder(self):
        """makes it so the user exits the directory they are in and begins browsing the parent drectory""" 
        #Makes the browser exit to the top item of jumps or it makes the browser exit to zero if jumps is empty
        if len(self.jumps) > 0:
            self.browser.exit(self.jumps.pop(),errorsupress = True)
        else : 
            #exit to a higher directory than home 
            self.browser.exit(errorsupress = True)
    def cursor_up(self):
        """moves the item the user is selecting up by one"""
        self.browser.backward(errorsupress = True)
    def cursor_down(self): 
        """moves the item the user is selecting down by one"""
        self.browser.forward(errorsupress = True)

    def generic_insert(self):
        """adds a user specified item to the todo list where the user's cursor is at.

        asks the user what item type they would like to add ,
        asks for the required attributes and then creates an item with those attributes
        and then adds the item to where the cursor is at.

        calls self.add_item_generic with no arguments"""
        self.add_item_generic()
    def generic_append(self):
        """adds a user specified item to the bottom of the todo list

        asks the user what item type they would like to add ,
        asks for the required attributes and then creates an item with those attributes
        and then adds the item to the bottom of the todo list the folderbrowser is in.

        calls self.add_item_generic with append_item as an argument"""
        self.add_item_generic('append_item')

    def todoitem_insert(self):
        """adds a todo item where the pointer is at

        asks the user for necessary attributes.

        calls self.add_item_generic with 'q' as an argument"""
        self.add_item_generic(option='q')
    def todoitem_append(self):
        """adds a todo item to the bottom of the folder being browsed

        asks the user for necessary attributes

        calls self.add_item_generic with 'append_item' and 'q' as an argument"""
        self.add_item_generic('append_item',option='q')

    def folder_insert(self):
        """adds a folder item where the pointer is at

        asks the user for necessary attributes.

        calls self.add_item_generic with 'e' as an argument"""
        self.add_item_generic(option='e')
    def folder_append(self):
        """adds a folder item to the bottom of the folder being browsed

        asks the user for necessary attributes

        calls self.add_item_generic with 'append_item' and 'e' as an argument"""
        self.add_item_generic('append_item',option='e')

    def todofolder_insert(self):
        """adds a todofolder item where the pointer is at

        asks the user for necessary attributes.

        calls self.add_item_generic with 'w' as an argument"""
        self.add_item_generic(option='w')
    def todofolder_append(self):
        """adds a todofolder item to the bottom of the folder being browsed

        asks the user for necessary attributes

        calls self.add_item_generic with 'append_item' and 'w' as an argument"""
        self.add_item_generic('append_item',option='w')

    def delete_item(self):
        """deletes the item the pointer is hovering over from the todo list

        if the folder is empty then it will delete the folder and exit 
        the user from the folder instead

        if the user tries deleting the highest directory it will tell them they cannot
        the deleted item is put into a stack that can be pulled from with paste."""
        if len(self.topdir.todos) != 0:
            #exit if the folder the directory is in is empty
            if len(self.browser.directory.todos) == 0:
                self.browser.exit(self.jumps.pop(),errorsupress = True) 
            #the delete method also stores the deleted item into the browser's history
            self.browser.delete()
            #the browser then moves up to make sure it dosen't fall of the edge of the index next time it tries to print
            #I could possibly make it so it checks if the index is too large and then only go backwards in that scenario
            self.browser.backward(errorsupress = True)
        else :
            return 'you cannot delete the top folder'
    def copy_item(self):
        """copys the item the pointer is hovering over from the todo list"""
        #exit if the folder the directory is in is empty
        if len(self.browser.directory.todos) != 0:
            self.browser.copy()
            return 'Item has been copied'
        else :
            return 'there is nothing to copy'
    def paste_item(self):
        """takes the last item that was deleted and puts it at the cursor's position"""
        self.browser.paste(errorsupress = True)
    def check_todo(self):
        """toggles the done attribute on the todo item or todo folder the cursor is on

        if it is not a foldder it will return that is a folder"""
        if len(self.browser.directory.todos) != 0:
            item = self.browser.get_item()
            if hasattr(item,'toggle'):
                item.toggle()
            else:
                return 'that is a folder'
        else:
            return 'that is a folder'
    def check_todo_everything(self):
        """If every item in a todofolder is set to done then set the above folder's done attribute to True

        otherwise set the folder's done attribute to false, or return 'that is not a ToDoFolder' if 
        it is not a todofolder"""
        item = self.browser.get_item(errorskip = True)
        if hasattr(item, 'check_done') and hasattr(item, 'done'):
            item.done = item.check_done()
        else :
            return 'that is not a ToDoFolder'

    def uncheck_all_in_folder(self) :
        item = self.browser.get_item(errorskip = True) 
        if hasattr(item, 'todos') :
            value = len(tuple(get_done_items(item))) <= 0
            set_all(item,value)
            if hasattr(item,'done') :
                item.done = value
        else :
            return 'that is not a folder' 

    def view_item(self):
        """prints the attributes of a selected item"""
        if len(self.browser.directory.todos) == 0:
            message = 'no files to edit'
            return message 
        #If there are files to edit then list the attributes out. 
        #If this is causing a problem by not listing an attribute 
        #Make sure that you have edited the is_printworthy function to include it
        #and make sure that you have edited the relevant item.seed function to include it
        else : 
            self.clear_screen()
            item = self.browser.get_item() 
            #the keys in item.seed should be the exact same as item.seeds attributes
            #they are each printed with a number after them
            for num,name in enumerate(filter(is_printworthy,item.seed)) :
                self.display_string(f'{num}: {name} {item.seed[name]}\n')
            self.get_key('press any key to exit')
    def edit_item(self):
        """prints the attributes of a selected item and then allows the user to edit them"""
        if len(self.browser.directory.todos) == 0:
            message = 'no files to edit'
            return message
        else :
            self.edit_a_todo(self.browser.get_item())

    def open_old_list(self):
        """tells folderbrowse to exit and open a new list from startbrowse"""
        if self.get_key('would you like to save (enter n for no)') != 'n':
            save_list(self.topdir,self.filename)
        return ('exit','o')
    def create_new_list(self):
        """tells folderbrowse to exit and create a new list with startbrowse"""
        if self.get_key('would you like to save before you exit (press n for no): ') != 'n':
            save_list(self.topdir,self.filename)
        return ('exit','u')

    def exit_to_home(self):
        """tells folderbrowser to exit back to startbrowse"""
        if self.get_key('\nwould you like to save before you exit (press n for no): ',message=True) != 'n':
            save_list(self.topdir,self.filename)
        self.clear_screen()
        action = self.get_key(self.prompts['get_action'])
        return ('exit',action)

    def quit_program(self):
        """tells program to exit back to shell"""
        if self.get_key('\nare you sure you want to quit (y/n): ',message=True) == 'y':
            if self.get_key('\nwould you like to save before you exit (press n for no): ',message=True) != 'n':
                save_list(self.topdir,self.filename)
            return ('exit','Z')

    def print_top_directory(self):
        """displays the highest directory to the user"""
        self.draw_screen(self.topdir)
        self.get_key()
    
    def save_file(self):
        """saves the file as xml on ~/.twilight/twitodolists"""
        save_list(self.topdir,self.filename)
        return 'folder has been saved'

    def print_help(self):
        """returns the variable HELPTEXTFOLDERBROWSE ,
        
        this may be changed at a later time to dynamically 
        display what the keybindings do rather than a static text 
        document"""
        return HELPTEXTFOLDERBROWSE

    def TEST_FUNCTION(self) : 
        """This function is for use by developers to test out new features.

        As of now it is used to test the newly added copy function""" 
        self.browser.add_item(self.browser.get_item().copy())
        






def folderbrowse(folder,screen,functions,prompts,filename=None,):
    """A function that takes user input to edit and save todo lists.

    it works by continuously running holder.go and then processing the output
    from it to check if it needs to exit. It returns codes to StartBrowser to tell it to do 
    things related to it if it exits.

    Arguments 
    ---------------------------
    folder:
        the folder that the browser starts browsing

    screen :
        the screen where the text will be printed

    functions :
        a dictionary of functions used to define the functions in a 
        BrowserHolder instance. 
        
    prompts : dict 
        a dictionary that translates short codes into long paragraphs of text

    filename : 
        the name of the file where the topdir folder will be saved 

    """
    holder = BrowserHolder(folder,screen,browserkeymappings,functions,prompts,filename,)
    while True: 
        result = holder.go() 
        if type(result) == tuple :
            if result[0] == 'exit' :
                #clear the screen so that the todo list dosen't show up
                holder.clear_screen()
                return result[1]



def new_list(screen,functions,prompts,foldername='',filename='',seq=False):
    """A function that makes a new todo list

    Arguments :

        screen:
            The screen that folderbrowse is run on

        foldername:
            The name of the initial folder that the todo list has 

        filename :
            The name of the file that the todo list is saved in 

        seq :
            If true then the innitial folder attribute is sequential 
            (this attribute does nothing right now but It will eventually be integrated with a calendar app)
    """
    return folderbrowse(Folder(foldername,sequential=seq),screen,functions,prompts,filename,)


class StartHolder :
    """A class that is used to abstract away the start menu from how text is displayed

    If you would like to change the user interface then define the proper functions and then run the script
    Right now there are three user interfaces , twitext.py, twigui.py and twicurses.py.

    Arguments
    ----------
    screen : 
        the object that controlls the user interface where text will be displayed
        It is different on each implementation of twilight. It should only be referenced 
        in functions and startfunctions

    startkeymap : dict
        a dictionary that can decode keys into function names, 
        used for defining user controlls. 
        
        As of now this argument must be set to STARTKEYMAP
        but that will be changed eventually. 

    keymap : dict 
        a dictionary that can decode keys into function names
        It is what gets passed to the folderbrowse function and
        it should be equal to what you would like to use as the kemap for
        BrowserHolder. Look at BrowserHolder to see what is required to be in 
        there. 

    startfunctions : dict
        a dictionary that contains all of the necessary functions to make StartHolder work. 
        Most of these functions are related to accepting user input and displaying text.

        read __init__ for a more longer discription of what is required
    
    functions : dict
        a dictionary that is passed as the argument for functions to BrowserHolder.
        Read the docstring for BrowserHolder __init__ for more information on it.

    prompts : dict 
        a dictionary that relates simple strings like 'get_action' to large paragraphs of text 
        for getting those actions. Read __init__ for more information on it.

    attributes 
    ----------------------------
    screen :
        the screen where text is displayed

        this should only be referenced by the functions in startfunctions

    startkeymap :
        a dictionary that decodes keys into function names

    keymap : 
        a dictionary that decodes keys into function names 
        
        It is the same keymap as the one used in folderbrowse,
        the sole purpose of this keymap is to be passed into 
        folderbrowse. Do not use it to define functions in startholder.

    startfunctions :
        a dictionary that links method names to actual functions

        It is used to define a unique ui without having the programmer
        worry about the screen. 

    prompts : 
        a dictionary that converts short names into long strings of text. 

        Used to display user prompts with get_key or get_string

    action : 
        a character that is decoded by keymap and then ran as a function
        
        This attribute must be changed, otherwise the function will just 
        continually loop at the same function. 


    """


    def __init__(self,screen,startkeymap,keymap,startfunctions,functions,prompts,getactionatstart=True):
        """Sets many attributes and then runs self.start

        Arguments
        ----------
        screen :
            the screen where all text will be printed. 

        startkeymap :
            Startkeymap should be a dictionary that translates single characters into method names

            as of now it must be equal to STARTKEYMAP 
            this will be changed in the future.

            Startkeymap should have the following method names inside of it
            Technically speaking these methods are optional but it should atleast have some.
            -------------------------------------------------------------------------------

            'open_list'     : prompts the user to open a list that is saved in .twitodolists

            'new_list_user' : creates a new list in .twitodolists

            'delete_list'   : lists the contents of .twitodolists and then prompts the user to delete one

            'print_lists'   : lists the contents of .twitodolists

            'exit_program'  : returns you back to shell. 


            Example of a proper dictionary 
            -------------------------------
            {
                'o' : 'open_list',
                'u' : 'new_list_user',
                'd' : 'delete_list',
                'p' : 'print_lists',
                'Z' : 'exit_program',
            }

        keymap :
            A dictionary that translates characters to method names
            
            It is passed into folderbrowser so look at BrowserHolder
            to see what it should look like. 

        startfunctions :
            A dictionary that converts method names into concrete functions. 

            most functions are related to user interface. Like displaying text and getting 
            keys. 
            
            The following methods should exist in startfunctions for an instance of 
            folderbrowse to be functional. reusing functons is incouraged. If you can
            use startholder methods instead of referencing screen directly that is also
            encouraged.
            -------------------------------

            can_scroll(startscreenholder,canscroll=True):
                if canscroll is equal to true the program should not throw an error when scrolling the screen
                past its limits. 

                Use an empty function if this is not applicable. (such as in twitext.py)

            get_key(startholder): 
                get_key should take user input and then return a string representing a single character
                it should return the first key pressed by the user. 

            get_string(startholder,prompt=''):
                get_string should display the prompt to the user and then make the text input visible to the user
                while the user's text is visible it should allow the user to type an arbitraily long string of text. 
                when the user is done it should return the text typed by the user. 

            refresh_screen(startholder):
                refresh_screen should make all text sent to be added to the screen visible.
                It should do nothing if that is not applicable. (such as in twitext.py) 

            display_string(browserholder,string:str,hilight=False,message=False):
                display_string should take a string and a boolian as an input and then
                make it so the user can see the text in the string. 
                If hilight is True then it should indicate to the user that the string is 
                different from the other ones. As of now hilight is just used for showing where the 
                cursor is on the todolist. 

                If message is true then it can put the message in a special place where it is more easily seen by
                the user. As of now this is only used in twigui 

            clear_screen(startholder):
                clear_screen should remove all items from the screen to allow new items to
                be displayed. If it isn't applicable to the current implementation (such as
                twitext.py) then it should do nothing. 

            enter_input_mode():
                this should make it so the user can see what they are typing. 

            exit_input_mode() :
                this should make it so the user cannot see what they are typing 
            
            new_list(startholder,foldername='',filename='',seq=False) :
                this should ask the user for a filename and foldername and then run folderbrowse on an empty
                Folderobject with foldername as it's name and, the current screen, functions and prompts. It should also have
                filename as the filename for folderbrowse.
                
                It should also return any output from folderbrowse 

                Look at folderbrowse for more information. Also look at curses_new_list on twicurses.py for an implementation.


            Example of a proper start functions dictionary 
            for the sake of brevity this will not have all the 
            requrired functions. look at twicurses.py or twitext.py
            for an example with all the required functions. 
            the things without quotes around them should be functions
            previously defined in the program. 
            ----------------------------------------------
            {
                'can_scroll'       : example_can_scroll 
                'new_list'         : example_new_list 
                'enter_input_mode' : example_enter_input_mode
            }



        functions :
            passed as an argument into folderbrowse.

            Read BrowserHolder for more information on how it should look, 
            and which methods it should conntain

        prompts :
            A dictionary that relates small strings of text to a large paragraph of text. 
            As of now the only prompt required is 

            'get_action'

            just make a dictionary with one key 'get_command' and then the prompt to get
            the command and you should be fine.

            this dictionary is shared between browserholder and start holder

            Example
            --------
            {
                'get_action' : ''' the
                quick brown fox jumped
                over the lasy dog''',
            }

        """

        self.screen = screen
        self.keymap = keymap 
        self.startkeymap = startkeymap
        self.startfunctions = startfunctions
        self.functions = functions 
        self.prompts = prompts
        self.start(getactionatstart)

    def start(self,getaction):
        """sets can_scroll to True , gets an action from the user, and clears the screen"""
        self.can_scroll()
        if getaction : 
            self.action = self.get_key(self.prompts['get_action'])
        else : 
            self.action = "invalid"
        self.clear_screen()

    def go(self,filename=None):
        """Runs the function that self.action currently maps to

        This may be changed to make it so self.action is a method name instead
        of a key.
        """
        if filename == None :
            return getattr(self,self.startkeymap.get(self.action,'invalid_action'))()
        else :
            self.action = folderbrowse(open_list(filename),self.screen,self.functions,self.prompts,filename,)
            return getattr(self,"open_list") 

    #start of customizable functions
    def can_scroll(self,canscroll:bool=True):
        """uses the startfunctions dictionary to tell the program that it can scroll"""
        self.startfunctions['can_scroll'](self,canscroll)

    def get_key(self,prompt='',message=False):
        """displays prompt and then uses startfunctions dictionanry to get a key from the user
        
        If message is true then it will be put in a message container instead of the regular container""" 
        #I am unsure if i want it to be like this. I may want to put self.display_string in the get_key function
        if prompt :                  
            self.display_string(prompt,message=message)
        return self.startfunctions['get_key'](self)
    def get_string(self,prompt=''):
        """uses startfunctions dict to return a user typed string"""
        return self.startfunctions['get_string'](self,prompt)
    def refresh_screen(self):
        """uses startfunctions dict to make added text visible"""
        self.startfunctions['refresh_screen'](self)
    def display_string(self,string:str,hilight=False,message=False):
        """uses startfunctions dict to make a string visible to the user

        If Hilight is true then the text will be made to look different from 
        regular text
        
        If message is True then the text will be placed in the message 
        container rather than the true screen (only functional in twigui as of now) 
        """
        self.startfunctions['display_string'](self,string,hilight,message)
    def clear_screen(self):
        """uses startfunctions dict clear all elements on a screen"""
        self.startfunctions['clear_screen'](self)
    def enter_input_mode(self):
        """uses startfunctions dict to make all text the user enters visible"""
        self.startfunctions['enter_input_mode']()
    def exit_input_mode(self) :
        """uses functions dict to make all text the user enters invisible"""
        self.startfunctions['exit_input_mode']()
    def new_list(self,filename='',foldername='',seq=False) :
        """uses functions dict to get a filename and foldername from the user and then starts browsing that new folder"""
        return self.startfunctions['new_list'](self,foldername,filename,seq)

    #end of things made through dictionaries

    def invalid_action(self) :
        """get new action and then set it to self.action

        and then clear the screen"""
        self.action = self.get_key(self.prompts['get_action']+'invalid action')
        self.clear_screen()

    def list_directory_contents(self):
        """displays the contents of .twitodolists and then returns the files as strings

        THIS HAS SIDE EFFECTS, Don't let the return statement fool you."""
        files = os.listdir()
        if len(files) == 0 :
            self.display_string('    no files here')
        for index, filename in enumerate(files):
            self.display_string(f'    {index} {filename} \n')
        return files

    def get_file_from_user_input(self,number,files):
        """number into a filename by putting that number in the index for files"""
        if number.isdigit():
            number = int(number)
            if number < len(files):
                return files[number]
            else :
                self.display_string(f'    {number} is not a valid number\n')
        elif number == 'q':
            self.clear_screen()
            self.action = self.get_key(self.prompts['get_action'])
            return None
        else :
            self.display_string(f'    {number} is not a valid number\n')
            return None

    def get_list_name(self,word):
        files = self.list_directory_contents()
        filenum = self.get_string('    enter number for the file you want to ' + word + ' press q to escape\n    ')
        listname = self.get_file_from_user_input(filenum,files)
        return listname
        
    #user commands start here

    def new_list_user(self) :
        """asks for a foldername and filename and then creates a new list with it"""
        foldername = self.get_string('enter a foldername: ')
        filename = self.get_string('enter a filename for the file: ')
        self.action = self.new_list(filename,foldername)
        self.clear_screen()

    def open_list(self):
        """runs folderbrowse on a todo list selected by the user"""
        #print the files in .twitodos with numbers and prompt for a number
        listname = self.get_list_name('open')
        if listname != None :
            self.action = folderbrowse(open_list(listname),self.screen,self.functions,self.prompts,listname,)

        self.clear_screen()
    
    def delete_list(self):
        """deletes a todo list selected by the user"""
        #print the files in .twitodos with numbers and prompt for a number
        listname = self.get_list_name('close') 
        if listname != None :
            os.remove(listname)
            self.action = self.get_key(self.prompts['get_action'])
        self.clear_screen()


    def archive_file(self) :
        listname = self.get_list_name('archive')
        if listname != None :
            shutil.move(listname,os.path.join('../archived_todo_lists/',os.path.basename(listname)+'_'+str(int(time.time()))))
            self.action = self.get_key(self.prompts['get_action'])
        self.clear_screen()
            
    def print_lists(self):
        """prints all the todolists in .twitext"""
        self.list_directory_contents()
        self.get_key('    press enter to exit')
        self.clear_screen()
        self.action = self.get_key(self.prompts['get_action'])
    
    def exit_program(self):
        """returns a singleton tuple with exit as the argument 

        This is presumably returned to run_start"""
        return ('exit',)


def move_to_home_directory():
    """This changes the directory to the default directory

    The default directory is ~/.twitodolists as of now
    """
    folderdirs = os.path.expanduser('~/.twilight/twitodolists')
    os.chdir(folderdirs)

def _change_OPTIONS_global_variable_change_warning(options) :
    """Takes a dictionary called options and then sets OPTIONS[key] to options[key]
    
    This should only be used one time in run_start"""
    global OPTIONS
    for key in options :
        OPTIONS[key] = options[key]

def run_start(screen,startkeymap,keymap,startfunctions,functions,prompts,options=dict(),filename=None):
    """A function that creates the start screen for an implementation of twilight

    The main block of the program is StartHolder, look at that for more detail 
    Also read BrowserHolder for more detail on some of the arguments 

    Arguments 
    ----------
    screen :
        the screen where the text will be printed

    startkkeymap : dict
        a dictionary that defines the buttons the user must press to operate the start menu

    keymap : 
        a dictionary that defines the buttonns a user must press to operate the todo list editing mode

    startfunctions : 
        a dictionary that defines the necessary functions required to complete a StartHolder class

    functions : 
        a dictionary that defines the necessary functions required to complete a BrowserHolder class

    prompts : 
        a dictionary that adds customizability to the user prompts

    """

    _change_OPTIONS_global_variable_change_warning(options)
    holder = StartHolder(screen,startkeymap,keymap,startfunctions,functions,prompts,getactionatstart = (filename == None)) 
    while True: 
        result = holder.go(filename) 
        #remove filename after first try
        filename = None 
        if type(result) == tuple :
            if result[0] == 'exit' :
                return
