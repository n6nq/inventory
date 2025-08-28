import psycopg2
import curses
from window import CmdWindow
from database import Database
import cnst

def main(stdscr):
    win = CmdWindow(stdscr)
    # Print first screen
    win.set_title('Inventory program, Ver 0.01')
    win.restart()
    win.bell()
    win.prompt('Press any key to continue...')
    win.getch(cnst.ANY)
    win.clrln(win.prompt_line)
    win.save_loc()

    db = Database(win)
    win.restore_loc()
    #win.restart()

    while(True):
        win.restart()
        choice = win.choice_at(win.prompt_line, 1, ['New','Find','Show','Delete','Exit'], True)

        match choice:
            case 'N':
                new_item(win, db)   #TODO add escape path to this function
            case 'F':
                find_something(win, db)     #TODO implement this function
            case 'D':
                delete_something(win, db)
            case 'S':
                show_something(win, db)
            case 'E':
                exit()
            case _:
                print('handle_not_choice')

def list_obj_is_new(obj):
    assert(len(obj) >= 1)
    return obj[0] == cnst.NEWOBJ

def list_obj_is_escaped(obj):
    assert(len(obj) >= 1)
    return obj[0] == cnst.ESCAPED

def new_item(win, db):
    # Paint the item line
    win.item_choice_str('Item: ')
    item_at = win.getloc()
    #choice_line = item_at[0] + 1

    # Get an existing or new category
    cats = db.get_categories()
    selected_cat = win.select_from_list(cats, 1, 'Category') 

    if list_obj_is_new(selected_cat):
        newcatname = selected_cat[1]
        selected_cat = db.add_category(newcatname)

    elif list_obj_is_escaped(selected_cat):                     # todo
        return
    
    cat_id = selected_cat[0]
    win.str_at(item_at[0], item_at[1], selected_cat[1]+', ')
    item_at = win.getloc()

    # Get an existing or new type
    types = db.get_types_for(cat_id)
    selected_type = win.select_from_list(types, 1, 'Type')  
    
    if list_obj_is_new(selected_type):
        newtypename = selected_type[1]
        selected_type = db.add_type(newtypename, cat_id)

    elif list_obj_is_escaped(selected_type):                     # todo
        return

    type_id = selected_type[0]
    win.str_at(item_at[0], item_at[1], selected_type[1]+', ')
    item_at = win.getloc()

    # Get an existing or new subtype
    subtypes = db.get_subtypes_for(type_id)
    selected_stype = win.select_from_list(subtypes, 1, 'subtype')
    if selected_stype[0] == -1:
        newsubtypename = selected_stype[1]
        selected_stype = db.add_subtype(newsubtypename, type_id)
    elif selected_stype[0] == -2:                     # todo
        return
    subtype_id = selected_stype[0]
    win.str_at(item_at[0], item_at[1], selected_stype[1]+', ')
    item_at = win.getloc()

    # Get Box id
    letters = db.get_box_letters()
    selected_letter = win.select_from_list(letters, 0, 'box letter')
    if selected_letter[0] == -1:
        newletter = selected_letter[1][0].upper()
        newnumber = '1'
    elif selected_letter[0] == -2:                     # todo
        return
    else:
        newletter = selected_letter[0]
        numbers = db.get_box_numbers(selected_letter[0])
        selected_number = win.select_from_list(numbers, 0, 'box number')
        if selected_number[0] == -1:
            newnumber = selected_number[1]
        elif selected_number[0] == -2:                     # todo
            return
        else:
            newnumber = selected_number[0]
    boxid  = newletter + newnumber
    win.str_at(item_at[0], item_at[1], boxid+', ')
    item_at = win.getloc()

    # Get box location
    locations = db.get_locations()
    selected_location = win.select_from_list(locations, 0, 'location')
    if selected_location[0] == -1:
        loc = selected_location[1]
    else:
        loc = selected_location[0]
    win.str_at(item_at[0], item_at[1], loc+', ')
    item_at = win.getloc()

    # Get item description
    descript = win.getstr_at(win.description_line, 1, 'Enter item description') #TODO add edit ability to this function
    win.str_at(item_at[0], item_at[1], descript+', ')
    item_at = win.getloc()

    # Save item to database
    db.add_item(cat_id, type_id, subtype_id, boxid, loc, descript)




def find_something(win, db):
    pass

def delete_something(win, db):
    pass

def show_something(win, db):
    win.restart()
    win.str_at(2, 1, 'Showing which?:')
    choice = win.choice_at(win.prompt_line, 1, ['Items','Categories','Types','Subtypes','ListTest2', 'Return'], True)
    match choice:
        case 'I':
            show_items(win, db)
        case 'C':
            show_categories(win, db)
        case 'T':
            show_types(win, db)
        case 'S':
            show_subtypes(win, db)
        case 'L':
            win.select_from_list3()
        case 'R':
            return
        case _:
            print('handle_not_choice')


def show_items(win, db):
    win.restart()
    win.str_at(2, 1, 'Showing which items?')
    choice = win.choice_at(3, 1, ['All','Category =','Type =','Subtype =','Exit'], True)
    match choice:
        case 'A':
            show_all_items(win, db)
        case 'C':
            show_items_where_category_eq(win, db)
        case 'T':
            show_items_where_type_eq(win, db)
        case 'S':
            show_items_where_subtype_eq(win, db)
        case 'E':
            exit()
        case _:
            print('handle_not_choice')

def show_all_items(win, db):
    win.restart()
    win.str_at(2, 1, 'Showing all items:')
    items = db.get_joined_items()
    win.select_from_list(items, -1, "All Items:")
    #selected_item = win.select_from_list(items, -1, 'items:')
    #todo what todo with selected item

def show_categories(win, db):
    pass


def show_types(win, db):
    pass


def show_subtypes(win, db):
    pass

if __name__ == "__main__":
    curses.wrapper(main)