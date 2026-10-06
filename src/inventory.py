#import re
#import select
#from ast import Continue
#from ast import Sub
from typing import cast

#import psycopg2
import curses
import os
#from unittest import case

#from dbpostgres import Database
from inventory.src.dbsqlite import Database
from inventory.src.models import Item, ListMember, Category, Type, Subtype, String
from inventory.src.window import CmdWindow
import inventory.src.cnst as cnst

current_item: Item = Item.from_empty()
current_cat: Category | None = None
current_type: Type | None = None
current_subtype: Subtype | None = None
current_box: String | None = None
current_location: String | None = None

def main(stdscr: curses.window):
    global current_item

    win = CmdWindow(stdscr)
    errorHandler = win.errorHandler
    prompter = win.prompter

    db = Database(errorHandler, prompter, "inventory.db")

    run_app(win, db)

def run_app(win: CmdWindow, db: Database) -> None:
    win.restore_loc()
    current_item = Item.from_empty()

    # Print first screen
    win.set_title('Inventory program, Ver 0.01')
    win.restart()
    win.save_loc()

    while(True):
        win.restart()
        win.str_at(win.item_line, 1, 'Current_item: ' + current_item.str_all())
        choice = win.choice_at(win.prompt_line, 1, ['New&Item','&New','&Find','&Show','&Update','&Delete','&Exit'], True)

        match choice:
            case 'I':
                retobj = new_item(win, db)   #TODO add escape path to this function
                if type(retobj) == Item:
                    current_item = retobj
            case 'N':
                retobj = new_something(win, db)   #TODO add escape path to this function
                if type(retobj) == Item:
                    current_item = retobj
            case 'F':
                retobj = find_item(win, db)     #TODO implement this function
                if type(retobj) == Item:
                    current_item = retobj
            case 'U':
                update_something(win, db)
            case 'D':
                delete_something(win, db)
            case 'S':

                show_something(win, db)
            case 'E':
                exit()
            case cnst.ESCAPE:
                pass
            case _:
                try_again(win, db)

def try_again(win: CmdWindow, db: Database) -> None:
    win.bell()
    win.clrln(win.prompt_line)
    win.str_at(win.prompt_line, 1, "Choice not handled! Type any key to try again.")
    win.getch(cnst.ALL)

def list_obj_is_new(obj: ListMember) -> bool:
    return obj.id == cnst.NEWOBJ

def select_item(win: CmdWindow, db: Database, items: list[Item], dspwhat: int, selectWhich: int|str, startLine: int) -> Item | None:
    # Callers of select_item are not allowed to create new items, so newAllowed: bool is not provide is this adapter. New items should
    # only be created with new_item. Since other ListMemberTypes are much simpler, they are allowed to be created in their adapter functions. 
    # This is a design decision that could be changed later if needed.
    selected_item: Item | None = None
    selected: int = win.select_from_list(items, dspwhat, selectWhich, 'Items', startLine, False)

    match selected:
        case cnst.CANCELED:
            return None
        case cnst.NEWOBJ:
            # Since callers of this function are not allowed to create new items, this is a programming error.
            assert(False)
        case int(index) if 0 <= index < len(items):
            selected_item = items[index]
        case _:
            return None
    return selected_item

def select_category(win: CmdWindow, db: Database, cats: list[Category], dspwhat: int, selectWhich: int|str, startLine: int, newAllowed: bool) -> Category | None:
    selected_cat: Category | None = None
    selected: int = win.select_from_list(cats, dspwhat, selectWhich, 'Category', startLine, newAllowed)

    match selected:
        case cnst.CANCELED:
            return None
        case cnst.NEWOBJ:
            selected_str: String = cast(String, cats.pop())  # slice off the last one
            newcatname: str = selected_str.string                
            selected_cat = db.add_category(newcatname)  # now it's a Category
        case int(index) if 0 <= index < len(cats):
            selected_cat = cats[index]
        case _:
            return None
    return selected_cat

def select_type(win: CmdWindow, db: Database, types: list[Type], dspwhat: int, selectWhich: int|str, startLine: int, cat_id: int, newAllowed: bool) -> Type | None:
    selected_type: Type | None = None
    selected: int = win.select_from_list(types, dspwhat, selectWhich, 'Type', startLine, newAllowed)

    match selected:
        case cnst.CANCELED:
            return None
        case cnst.NEWOBJ:
            selected_str: String = cast(String, types.pop())  # slice off the last one
            newtypename: str = selected_str.string
            assert(cat_id != -1)                    # programming error  -1 should only be passed when newAllowed is False
            selected_type = db.add_type(newtypename, cat_id)  # now it's a Category
        case int(index) if 0 <= index < len(types):
            selected_type = types[index]
        case _:
            return None
    return selected_type

def select_stype(win: CmdWindow, db: Database, stypes: list[Subtype], dspwhat: int, selectWhich: int|str, startLine: int, type_id: int, newAllowed: bool) -> Subtype | None:
    selected_stype: Subtype | None = None
    selected: int = win.select_from_list(stypes, dspwhat, selectWhich, 'Subtype', startLine, newAllowed)

    match selected:
        case cnst.CANCELED:
            return None
        case cnst.NEWOBJ:
            selected_str: String = cast(String, stypes.pop())  # slice off the last one
            newstypename: str = selected_str.string
            assert(type_id != -1)                    # programming error  -1 should only be passed when newAllowed is False
            selected_stype = db.add_subtype(newstypename, type_id)  # now it's a Category
        case int(index) if 0 <= index < len(stypes):
            selected_stype = stypes[index]
        case _:
            return None
    return selected_stype

def select_boxletter(win: CmdWindow, db: Database, letters: list[String], dspwhat: int, selectWhich: int|str, startLine: int, newAllowed: bool) -> String | None:

    selected: int = win.select_from_list(letters, dspwhat, selectWhich, 'Box Letters', startLine, newAllowed)

    match selected:
        case cnst.CANCELED:
            return None
        case cnst.NEWOBJ:
            selected_str: String = letters.pop()  # slice off the last one
            return selected_str                     # '1' means it's new, so it gets a '1'
        case int(index) if 0 <= index < len(letters):   
            selected_str = letters[index]
            return selected_str                     # '0' means an existing letter, so user has to pick a number
        case _:
            return None

def select_boxnumber(win: CmdWindow, db: Database, numbers: list[String], dspwhat: int, selectWhich: int|str, startLine: int, newAllowed: bool) -> String | None:

    selected: int = win.select_from_list(numbers, dspwhat, selectWhich, 'Box Numbers', startLine, newAllowed)

    match selected:
        case cnst.CANCELED:
            return None
        case cnst.NEWOBJ:
            selected_str: String = numbers.pop()  # slice off the last one
            return selected_str                     # '1' means it's new, so it gets a '1'
        case int(index) if 0 <= index < len(numbers):   
            selected_str = numbers[index]
            return selected_str                     # '0' means an existing letter, so user has to pick a number
        case _:
            return None

def select_location(win: CmdWindow, db: Database, locations: list[String], dspwhat: int, selectWhich: int|str, startLine: int, newAllowed: bool) -> String | None:

    selected: int = win.select_from_list(locations, dspwhat, selectWhich, 'Locations', startLine, newAllowed)

    match selected:
        case cnst.CANCELED:
            return None
        case cnst.NEWOBJ:
            selected_str: String = locations.pop()  # slice off the last one
            return selected_str                     # '1' means it's new, so it gets a '1'
        case int(index) if 0 <= index < len(locations):   
            selected_str = locations[index]
            return selected_str                     # '0' means an existing letter, so user has to pick a number
        case _:
            return None


def new_item(win: CmdWindow, db: Database) -> Item | None:
    # Paint the item line

    win.item_choice_str('Item: ')
    item_at = win.getloc()

    cats = db.get_categories()
    selected_cat: Category | None = select_category(win, db, cats, cnst.DSPLYNAME, 0, win.list_header_line, True)

    if selected_cat is None:
        return None
    
    cat_id: int = selected_cat.id
    cat_str: str = selected_cat.c_name
    win.str_at(item_at[0], item_at[1], cat_str+', ')
    item_at = win.getloc()

    # Get an existing or new type ####################################################
    types = db.get_types_for_cat(cat_id)
    selected_type = select_type(win, db, types, cnst.DSPLYNAME, 0, win.list_header_line, cat_id, True)

    if selected_type is None:
        return None

    type_id: int = selected_type.id
    type_name: str = selected_type.t_name
    win.str_at(item_at[0], item_at[1], type_name+', ')
    item_at = win.getloc()

    # Get an existing or new subtype ################################################
    subtypes = db.get_subtypes_for_types([type_id])
    selected_stype: Subtype | None = select_stype(win, db, subtypes, cnst.DSPLYNAME, 0, win.list_header_line, type_id, True)

    if selected_stype is None:
        return None

    sub_id = selected_stype.id
    sub_str = selected_stype.st_name
    win.str_at(item_at[0], item_at[1], sub_str+', ')
    item_at = win.getloc()

    # Get Box id
    letters = db.get_box_letters()
    
    selected_str: String | None = select_boxletter(win, db, letters, cnst.DSPLYSTR, 0, win.list_header_line, True)


    match selected_str:
        case None:
            return None
        case String():
            newletter: str = selected_str.string.upper()
        case _:
            assert(False)       # Programming error


    if selected_str.id == cnst.NEWOBJ:
        newnumber = "1"
    else:
        numbers = db.get_box_numbers(newletter)

        if len(numbers) == 0:
            newnumber = "1"
        else:
            selected_num: String | None = select_boxnumber(win, db, numbers, cnst.DSPLYSTR, 0, win.list_header_line, True)

            match selected_num:
                case None:
                    return None
                case String():
                    newnumber: str = selected_num.string
                case _:
                    assert(False)       # Programming error

    boxid  = newletter + newnumber
    win.str_at(item_at[0], item_at[1], boxid+', ')
    item_at = win.getloc()

    # Get box location
    locations = db.get_locations()  #fix list[unknown]  
    selected_loc: String | None = select_location(win, db, locations, cnst.DSPLYSTR, 0, win.list_header_line, True)

    match selected_loc:
        case None:
            return None
        case String():
            loc: str = selected_loc.string
        case _:
            assert(False)       # Programming error

    win.str_at(item_at[0], item_at[1], loc+', ')
    item_at = win.getloc()

    # Get item description
    descript = win.getstr_at(win.description_line, 1, 'Enter item description') #TODO add edit ability to this function
    if descript == None:
        return None
    win.str_at(item_at[0], item_at[1], descript+', ')
    item_at = win.getloc()

    # Save item to database
    ni = db.add_item(cat_id, type_id, sub_id, boxid, loc, descript)
    return ni




def find_item(win: CmdWindow, db: Database) -> Item | None:

    while(True):
        win.restart()
        win.str_at(win.what_line, 1, "Find item from:")
        choice = win.choice_at(win.prompt_line, 1, ['&All','&Cat =','Cat+&Type =','Cat+Type+&SubType =','String&Value','&Return'], True)

        match choice:
            case 'A':
                return find_item_by_all(win, db)
            case 'C':
                return find_item_by_cat(win, db)     #TODO implement this function
            case 'T':
                return find_item_by_cat_type(win, db)
            case 'S':
                return find_item_by_cat_type_sub(win, db)
            case 'V':
                return find_by_str_value(win, db)
            case 'R' | cnst.ESCAPE:
                return None
            case _:
                try_again(win, db)

        

def find_item_by_all(win: CmdWindow, db: Database) -> Item | None:
    win.restart()
    win.str_at(win.what_line, 1, 'Find item from all items:')
    items = db.get_items()
    selected_item: Item | None = select_item(win, db, items, cnst.DSPLYALL, 0, win.list_header_line)

    return selected_item

def find_by_str_value(win: CmdWindow, db: Database) -> Item | None:
    win.restart()
    win.str_at(win.what_line, 1, 'Find item by string value:')
    items = db.get_items()
    selected_item: Item | None = select_item(win, db, items, cnst.DSPLYALL, 0, win.list_header_line)

    return selected_item

def find_item_by_cat(win: CmdWindow, db: Database) -> Item | None:
    win.restart()
    win.str_at(win.what_line, 1, 'Find item by category:')
    cats = db.get_categories()
    selected_cat: Category | None = select_category(win, db, cats, cnst.DSPLYNAME, 0, win.list_header_line, False)

    if selected_cat == None:
        return None
    win.restart()
    win.str_at(win.what_line, 1, 'Find item with category: '+ selected_cat.c_name)
    items = db.get_items_by_cat(selected_cat.id)
    selected_item: Item | None = select_item(win, db, items, cnst.DSPLYALL, 0, win.list_header_line)

    return selected_item

def find_item_by_cat_type(win: CmdWindow, db: Database) -> Item | None:
    win.restart()
    win.str_at(win.what_line, 1, 'Find item by category and type:')
    cats = db.get_categories()
    selected_cat: Category | None = select_category(win, db, cats, cnst.DSPLYNAME, 0, win.list_header_line, False)

    if selected_cat == None:
        return None
    win.restart()
    win.str_at(win.what_line, 1, 'Find item by category '+selected_cat.c_name+ ' and which type:')
    types = db.get_types_for_cat(selected_cat.id)
    selected_type: Type | None = select_type(win, db, types, cnst.DSPLYNAME, 0, win.list_header_line, selected_cat.id, False)

    if selected_type == None:
        return None
    win.str_at(win.what_line, 1, 'Find item with category: '+ selected_cat.c_name + ' and type: ' + selected_type.t_name)
    items = db.get_items_by_cat_type(selected_cat.id, selected_type.id)
    selected_item: Item | None = select_item(win, db, items, cnst.DSPLYALL, 0, win.list_header_line)

    return selected_item

def find_item_by_cat_type_sub(win: CmdWindow, db: Database) -> Item | None:
    win.restart()
    win.str_at(win.what_line, 1, 'Find item by category, type and subtype:')
    cats = db.get_categories()
    selected_cat: Category | None = select_category(win, db, cats, cnst.DSPLYNAME, 0, win.list_header_line, False)

    if selected_cat == None:
        return None

    win.restart()
    win.str_at(win.what_line, 1, 'Find item by category '+selected_cat.c_name+ ' and which type:')
    types = db.get_types_for_cat(selected_cat.id)
    selected_type: Type | None = select_type(win, db, types, cnst.DSPLYNAME, 0, win.list_header_line, selected_cat.id, False)

    if selected_type == None:
        return None

    win.restart()
    win.str_at(win.what_line, 1, 'Find item by category '+selected_cat.c_name+ ', type '+selected_type.t_name+ ' and which subtype:')
    subtypes = db.get_subtypes_for_types([selected_type.id])
    selected_subtype: Subtype | None = select_stype(win, db, subtypes, cnst.DSPLYNAME, 0, win.list_header_line, selected_type.id, False)

    if selected_subtype == None:
        return None

    win.str_at(win.what_line, 1, 'Find item with category: '+selected_cat.c_name+', type: '+selected_type.t_name+' and subtype: '+selected_subtype.st_name)
    items = db.get_items_by_cat_type_subtype(selected_cat.id, selected_type.id, selected_subtype.id)
    selected_item: Item | None = select_item(win, db, items, cnst.DSPLYALL, 0, win.list_header_line)

    return selected_item

def update_something(win: CmdWindow, db: Database) -> None:
    win.restart()
    win.str_at(win.what_line, 1, 'Update which?:')
    choice = win.choice_at(win.prompt_line, 1, ['&Item','&Category','&Type','&Subtype', '&Return'], True)
    match choice:
        case 'I':
            update_item(win, db)
        case 'C':
            udpate_category(win, db)
        case 'T':
            update_type(win, db)
        case 'S':
            update_subtype(win, db)
        case 'R' | cnst.ESCAPE:
            return
        case _:
           try_again(win, db)

def update_item(win: CmdWindow, db: Database) -> None:
    global current_item
    if current_item.id == 0:
        win.restart()
        win.str_at(win.what_line, 1, 'You need to select a current_item first. See the "Find" choice.')
    else:
        win.restart()
        uline = win.what_line
        nline = uline+1
        lline = uline+2
        win.str_at(uline, 1, 'Updating item: '+current_item.str_all()+'.')
        win.str_at(nline, 1, 'Start with which column ? ')
        new_item = db.get_item_by_id(current_item.id)
        if new_item is None:
            win.str_at(nline, 1, 'Error: item not found in database.')
            return
        dirty: bool = False

        while(True):
            win.clrtoend(lline, 1)
            choice = win.choice_at(win.prompt_line,1,['&Category>Type>SubType','&Box','&Location','&Description','&UPDATE','&Return'],True)
            
            # Get an existing or new category
            win.clrln(nline)
            prefix = '     New item: '
            win.str_at(nline, 1, prefix + new_item.str_all())

            if choice == 'R' or choice == cnst.ESCAPE:
                return

            if choice == 'C':
                cats = db.get_categories()
                selected_cat: Category | None = select_category(win, db, cats, cnst.DSPLYNAME, 0, win.list_header_line, True)

                if selected_cat is None:
                    continue

                if selected_cat.id != new_item.cat_id:
                    new_item.cat_id = selected_cat.id
                    new_item.cat_str = selected_cat.c_name
                    dirty = True
                    win.clrln(nline)
                    win.str_at(nline, 1, prefix + new_item.str_all())
            
                # Get an existing or new type
                types = db.get_types_for_cat(new_item.cat_id)

                if new_item.cat_id != current_item.cat_id:  # if cat_id not equal cat_id in current_item 
                    preselect = 0                       #   then preselect the first first type
                else:                                       # else
                    preselect =  current_item.type_id       #   preselect the type in current_item

                selected_type = select_type(win, db, types, cnst.DSPLYNAME, preselect, win.list_header_line, new_item.cat_id, True)

                if selected_type is None:
                    continue

                if selected_type.id != new_item.type_id:
                    new_item.type_id = selected_type.id
                    new_item.type_str = selected_type.t_name
                    dirty = True
                    win.clrln(nline)
                    win.str_at(nline, 1, prefix + new_item.str_all())

                # Get an existing or new subtype
                subtypes = db.get_subtypes_for_types([new_item.type_id])

                if new_item.type_id != current_item.type_id:    # if type_id not equal type_id in current_item 
                    preselect = 0                        #   then preselect the first subtype
                else:                                           # else
                    preselect = current_item.sub_id          #   preselect the previous subtype

                selected_stype: Subtype | None = select_stype(win, db, subtypes, cnst.DSPLYNAME, 0, win.list_header_line, selected_type.id, True)

                if selected_stype is None:
                    continue

                if selected_stype.id != new_item.sub_id:
                    new_item.sub_id = selected_stype.id
                    new_item.sub_str = selected_stype.st_name
                    dirty = True
                    win.clrln(nline)
                    win.str_at(nline, 1, prefix + new_item.str_all())


            # Get Box id

            if choice == 'B':
                letters = db.get_box_letters()

                selected_str: String | None = select_boxletter(win, db, letters, cnst.DSPLYSTR, 0, win.list_header_line, True)

                match selected_str:
                    case None:
                        continue
                    case String():
                        newletter: str = selected_str.string.upper()
                    case _:
                        assert(False)       # Programming error

                if selected_str.id == cnst.NEWOBJ:
                    newnumber = "1"
                else:
                    numbers = db.get_box_numbers(newletter)

                    if len(numbers) == 0:
                        newnumber = "1"
                    else:
                        selected_num: String | None = select_boxnumber(win, db, numbers, cnst.DSPLYSTR, 0, win.list_header_line, True)

                        match selected_num:
                            case None:
                                continue
                            case String():
                                newnumber: str = selected_num.string
                            case _:
                                assert(False)       # Programming error

                box  = newletter + newnumber
                new_item.box = box
                dirty = True
                win.clrln(nline)
                win.str_at(nline, 1, prefix + new_item.str_all())

            # Get box location
            if choice == 'L':
                locations = db.get_locations()
                selected_loc: String | None = select_location(win, db, locations, cnst.DSPLYSTR, 0, win.list_header_line, True)

                match selected_loc:
                    case None:
                        continue
                    case String():
                        loc: str = selected_loc.string
                        new_item.loc = loc
                    case _:
                        assert(False)       # Programming error

            
                dirty = True
                win.clrln(nline)
                win.str_at(nline, 1, prefix + new_item.str_all())

            # Get item description
            if choice == 'D':
                descript = win.getstr_at(lline, 1, 'Enter item description')    #TODO add edit ability to this function
            
                if descript == None:
                    descript = new_item.descript

                new_item.descript = descript
                dirty = True
                win.clrln(nline)
                win.str_at(nline, 1, prefix + new_item.str_all())

            # Save item to database
            if choice == 'U' and dirty:
                win.clrln(uline)
                if db.update_item(new_item):
                    current_item = new_item
                    win.str_at(uline, 1, 'Updating item: '+new_item.str_all()+'.')
                else:
                    win.str_at(uline, 1, 'Error updating item: '+new_item.str_all()+'.')
                    win.str_at(win.prompt_line,1,'Press any key to continue...')
                    win.getch(cnst.ANY)
                return 

def udpate_category(win: CmdWindow, db: Database) -> None:
    win.restart()
    uline = win.what_line
    nline = uline+1
    lline = uline+2

    cats = db.get_categories()
    win.str_at(uline,1,'Update which Category?')
    selected_cat: Category | None = select_category(win, db, cats, cnst.DSPLYNAME, 0, lline, False)

    if selected_cat == None:
        return

    win.restart()
    win.str_at(uline, 1, "Update "+ selected_cat.c_name)
    new_value = win.getstr_at(nline,1,"New value")

    if new_value != None:
        if not db.update_cat(selected_cat.id, new_value):
            win.str_at(win.prompt_line,1,'Error updating category: '+selected_cat.c_name+'.')
            win.str_at(win.prompt_line+1,1,'Press any key to continue...')
            win.getch(cnst.ANY)

def update_type(win: CmdWindow, db: Database) -> None:
    win.restart()
    uline = win.what_line
    nline = uline+1
    lline = uline+2

    #make a cat dictionary
    cats = db.get_categories()
    catdict = {}
    for cat in cats:
        catdict[cat.id] = cat.c_name

    types = db.get_types()
    win.str_at(uline,1,'Update which Type?')
    selected_type: Type | None = select_type(win, db, types, cnst.DSPLYNAME, 0, lline, -1, False)

    if selected_type == None:
        return

    win.restart()
    win.str_at(uline, 1, "Update "+ selected_type.t_name)
    new_value = win.getstr_at(nline,1,"New value")

    if new_value != None:
        if not db.update_type(selected_type.id, new_value):
            win.str_at(win.prompt_line,1,'Error updating type: '+selected_type.t_name+'.')
            win.str_at(win.prompt_line+1,1,'Press any key to continue...')
            win.getch(cnst.ANY)


def update_subtype(win: CmdWindow, db: Database) -> None:
    win.restart()
    uline = win.what_line
    nline = uline+1
    lline = uline+2

    subtypes = db.get_subtypes()
    win.str_at(uline,1,'Update which SubType?')
    selected_subtype: Subtype | None = select_stype(win, db, subtypes, cnst.DSPLYNAME, 0, lline, -1, False)

    if selected_subtype == None:
        return

    win.restart()
    win.str_at(uline, 1, "Update "+ selected_subtype.st_name)
    new_value = win.getstr_at(nline,1,"New value")

    if new_value != None:
        if not db.update_subtype(selected_subtype.id, new_value):
            win.str_at(win.prompt_line,1,'Error updating subtype: '+selected_subtype.st_name+'.')
            win.str_at(win.prompt_line+1,1,'Press any key to continue...')
            win.getch(cnst.ANY)


def delete_something(win: CmdWindow, db: Database) -> None:
    win.restart()
    win.str_at(win.what_line, 1, 'Delete which?:')
    choice = win.choice_at(win.prompt_line, 1, ['&Item','&Category','&Type','&Subtype', '&Return'], True)
    match choice:
        case 'I':
            delete_item(win, db)
        case 'C':
            delete_category(win, db)
        case 'T':
            delete_type(win, db)
        case 'S':
            delete_subtype(win, db)
        case 'R' | cnst.ESCAPE:
            return
        case _:
           try_again(win, db)

def delete_item(win: CmdWindow, db: Database) -> None:
    win.restart()
    win.str_at(win.what_line, 1, 'Select item for deletion:')
    items = db.get_items()
    selected_item: Item | None = select_item(win, db, items, cnst.DSPLYALL, 0, win.list_header_line)

    if selected_item == None:
        return
    win.str_at(win.prompt_line-1, 1, 'Delete:  '+selected_item.str_all()+' ???')
    choice = win.choice_at(win.prompt_line, 1, ['&Yes','&No'], True)
    if choice == 'Y':
        if not db.delete_item(selected_item.id):
            win.str_at(win.prompt_line,1,'Error deleting item: '+selected_item.str_all()+'.')
            win.str_at(win.prompt_line+1,1,'Press any key to continue...')
            win.getch(cnst.ANY)
    return None

def delete_category(win: CmdWindow, db: Database) -> None:
    win.restart()
    win.str_at(win.what_line, 1, 'Select category for deletion:')
    cats = db.get_categories()
    selected_cat: Category | None = select_category(win, db, cats, cnst.DSPLYNAME, 0, win.list_header_line, False)

    if selected_cat == None:
        return
    
    win.str_at(win.prompt_line-1, 1, 'Delete:'+repr(selected_cat)+' ???')
    choice = win.choice_at(win.prompt_line, 1, ['&Yes','&No'], True)
    if choice == 'Y':
        if not db.delete_cat(selected_cat.id):
            win.str_at(win.prompt_line,1,'Error deleting category: '+selected_cat.c_name+'.')
            win.str_at(win.prompt_line+1,1,'Press any key to continue...')
            win.getch(cnst.ANY)
    return None

def delete_type(win: CmdWindow, db: Database) -> None:
    win.restart()
    win.str_at(win.what_line, 1, 'Select type for deletion:')
    types = db.get_types()
    selected_type: Type | None = select_type(win, db, types, cnst.DSPLYNAME, 0, win.list_header_line, -1, False)

    if selected_type == None:
        return
    win.str_at(win.prompt_line-1, 1, 'Delete:'+repr(selected_type)+' ???')
    choice = win.choice_at(win.prompt_line, 1, ['&Yes','&No'], True)
    if choice == 'Y':
        if not db.delete_type(selected_type.id):
            win.str_at(win.prompt_line,1,'Error deleting type: '+selected_type.t_name+'.')
            win.str_at(win.prompt_line+1,1,'Press any key to continue...')
            win.getch(cnst.ANY)
    return None

def delete_subtype(win: CmdWindow, db: Database) -> None:
    win.restart()
    win.str_at(win.what_line, 1, 'Select subtype for deletion:')
    stypes = db.get_subtypes()
    selected_stype: Subtype | None = select_stype(win, db, stypes, cnst.DSPLYNAME, 0, win.list_header_line, -1, True)

    if selected_stype is None:
        return None

    win.str_at(win.prompt_line-1, 1, 'Delete:'+selected_stype.str_all()+' ???')
    choice = win.choice_at(win.prompt_line, 1, ['&Yes','&No'], True)
    if choice == 'Y':
        if not db.delete_stype(selected_stype.id):
            win.str_at(win.prompt_line,1,'Error deleting subtype: '+selected_stype.st_name+'.')
            win.str_at(win.prompt_line+1,1,'Press any key to continue...')
            win.getch(cnst.ANY)
    return None

def new_something(win: CmdWindow, db: Database) -> Item |None:
    global current_item
    win.restart()
    win.str_at(win.what_line, 1, 'A new which?:')
    choice = win.choice_at(win.prompt_line, 1, ['&Item','&Category','&Type','&Subtype', '&Return'], True)
    match choice:
        case 'I':
            return new_item(win, db)
        case 'C':
            new_category(win, db)
        case 'T':
            new_type(win, db)
        case 'S':
            new_subtype(win, db)
        case 'R' | cnst.ESCAPE:
            pass
        case _:
           try_again(win, db)
    return None

def new_category(win: CmdWindow, db: Database) -> None:
    cats = db.get_categories()
    win.str_at(win.what_line,1,"If your new Category is in this list, you should just esc and use the existing one.")
    win.str_at(win.what_line+1,1, "Otherwise, just type the new category name and hit Enter.")
    select_category(win, db, cats, cnst.DSPLYNAME, 0, win.what_line+2, True)  # Only the new category is returned, if any.  The database is updated in select_category().




def new_type(win: CmdWindow, db: Database) -> None:
    cats = db.get_categories()
    win.str_at(win.what_line,1,"A new Type must belong to an existing or new Category.")
    win.str_at(win.what_line+1,1, " Please select or createthe new type's parent from the existing list.")
    selected_cat: Category | None = select_category(win, db, cats, cnst.DSPLYNAME, 0, win.what_line+2, True) 

    if selected_cat is None:
        return None

    
    win.restart()
    types = db.get_types_for_cat(selected_cat.id)
    win.str_at(win.what_line,1,"If your new Type is in this list, you should just esc and use the existing one.")
    win.str_at(win.what_line+1,1, "Otherwise, just type the new Type name and hit Enter.")
    select_type(win, db, types, cnst.DSPLYNAME, 0, win.list_header_line, -1, False) # Only the new type is returned, if any.  The database is updated in select_type().

def new_subtype(win: CmdWindow, db: Database) -> None:
    win.str_at(win.what_line,1,"A new SubType must belong to an existing Category and Type. Please select")
    win.str_at(win.what_line+1,1, "the new Subtype's parent Category and Type from the following two lists.")
    cats = db.get_categories()
    selected_cat = select_category(win, db, cats, cnst.DSPLYNAME, 0, win.what_line+2, True) 

    if selected_cat == None:
        return

    win.restart()
    types = db.get_types_for_cat(selected_cat.id)
    selected_type = select_type(win, db, types, cnst.DSPLYNAME, 0, win.list_header_line, selected_cat.id, True)

    if selected_type == None:
        return

    win.restart()
    subtypes = db.get_subtypes_for_types([selected_type.id])
    win.str_at(win.what_line,1,"If your new SubType is in this list, you should just esc and use the existing one.")
    win.str_at(win.what_line+1,1, "Otherwise, just type the new SubType name and hit Enter.")
    select_stype(win, db, subtypes, cnst.DSPLYNAME, 0, win.list_header_line, selected_type.id, True) # Only the new subtype is returned, if any.  The database is updated in select_stype().



def show_something(win: CmdWindow, db: Database) -> None:
    win.restart()
    win.str_at(win.what_line, 1, 'Show which?:')
    choice = win.choice_at(win.prompt_line, 1, ['&Items','&Categories','&Types','&Subtypes', '&Return'], True)
    match choice:
        case 'I':
            show_items(win, db)
        case 'C':
            show_categories(win, db)
        case 'T':
            show_types(win, db)
        case 'S':
            show_subtypes(win, db)
        case 'R' | cnst.ESCAPE:
            return
        case _:
           try_again(win, db)


def show_items(win: CmdWindow, db: Database) -> None:
    global current_item
    win.restart()
    win.str_at(2, 1, 'Show which items?')
    choice = win.choice_at(3, 1, ['&All','&Category =','&Type =','&Subtype =','&Return'], True)
    match choice:
        case 'A':
            selected_item = show_all_items(win, db)
            if selected_item != None:
                current_item = selected_item
        case 'C':
            selected_item = show_items_where_category_eq(win, db)
            if selected_item != None:
                current_item = selected_item
        case 'T':
            selected_item = show_items_where_type_eq(win, db)
            if selected_item != None:
                current_item = selected_item
        case 'S':
            selected_item = show_items_where_subtype_eq(win, db)
            if selected_item != None:
                current_item = selected_item
        case 'R' | cnst.ESCAPE:
            return
        case _:
            try_again(win, db)


def show_all_items(win: CmdWindow, db: Database) -> None:
    global current_item
    win.restart()
    items = db.get_items()
    selected_item: Item | None = select_item(win, db, items, cnst.DSPLYALL, 0, win.list_header_line)

    if selected_item is not None:
        current_item = selected_item  
    return None

def show_items_where_category_eq(win: CmdWindow, db: Database) -> None:
    global current_item
    cats = db.get_categories()
    selected_cat: Category | None = select_category(win, db, cats, cnst.DSPLYNAME, 0, win.list_header_line, False)

    if selected_cat is None:
        return None
    #selected_cat = cats[selected] 

    win.restart()
    items = db. get_items_by_cat(selected_cat.id)
    selected_item: Item | None = select_item(win, db, items, cnst.DSPLYALL, 0, win.list_header_line)


    if selected_item is not None:
        current_item = selected_item
    return None

def show_items_where_type_eq(win: CmdWindow, db: Database) -> None:
    global current_item
    types = db.get_types()
    selected_type: Type | None = select_type(win, db, types, cnst.DSPLYALL, 0, win.list_header_line, -1, False)

    if selected_type is None:
        return None

    win.restart()
    items = db. get_items_by_type(selected_type.id)
    selected_item: Item | None = select_item(win, db, items, cnst.DSPLYALL, 0, win.list_header_line)

    if selected_item is not None:
        current_item = selected_item
    return None

def show_items_where_subtype_eq(win: CmdWindow, db: Database) -> None:
    global current_item
    stypes = db.get_subtypes()
    selected_stype: Subtype | None = select_stype(win, db, stypes, cnst.DSPLYALL, 0, win.list_header_line, -1, False)

    if selected_stype is None:
        return None
    
    win.restart()
    items = db.get_items_by_stype(selected_stype.id)
    selected_item: Item | None = select_item(win, db, items, cnst.DSPLYALL, 0, win.list_header_line)

    if selected_item is not None:
        current_item = selected_item
    return None



def show_categories(win: CmdWindow, db: Database) -> None:
    cats = db.get_categories()
    select_category(win, db, cats, cnst.DSPLYNAME, 0, win.list_header_line, False)

def show_types(win: CmdWindow, db: Database) -> None:
    types = db.get_types()
    select_type(win, db, types, cnst.DSPLYNAME, 0, win.list_header_line, -1, False)

def show_subtypes(win: CmdWindow, db: Database) -> None:
    stypes = db.get_subtypes()
    select_stype(win, db, stypes, cnst.DSPLYNAME, 0, win.list_header_line, -1, False)

if __name__ == "__main__":
    curses.wrapper(main)