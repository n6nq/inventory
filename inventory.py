import psycopg2
import curses
import os
from window import CmdWindow
from database import Database
import cnst

current_item = None
current_cat = None
current_type = None
current_subtype = None
current_box = None
current_location = None

def main(stdscr):
    global current_item
    #print("Starting inventory program...")
  
    # get database location from environment
    pgaddress = os.getenv('PGADDRESS')
    pgport = os.getenv('PGPORT')
    if pgaddress == None:
        pgaddress = 'localhost'
    if pgport == None:
        pgport = '5432'
    current_item = None
    win = CmdWindow(stdscr)
    # Print first screen
    win.set_title('Inventory program, Ver 0.01')
    win.restart()
    win.save_loc()
    #win.getch(cnst.ANY)
    db = Database(win,pgaddress,pgport)
    win.restore_loc()
    current_item = ''

    while(True):
        win.restart()
        win.str_at(win.item_line, 1, 'Current_item: ' + ", ".join(str(x) for x in current_item))
        choice = win.choice_at(win.prompt_line, 1, ['New&Item','&New','&Find','&Show','&Update','&Delete','&Exit'], True)

        match choice:
            case 'I':
                current_item = new_item(win, db)   #TODO add escape path to this function
            case 'N':
                new_something(win, db)   #TODO add escape path to this function
            case 'F':
                c_i = find_item(win, db)     #TODO implement this function
                if c_i != None:
                    current_item = c_i
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

def try_again(win, db):
    win.bell()
    win.clrln(win.prompt_line)
    win.str_at(win.prompt_line, 1, "Choice not handled! Type any key to try again.")
    win.getch(cnst.ALL)

def list_obj_is_new(obj):
    assert(len(obj) >= 1)
    return obj[0] == cnst.NEWOBJ

def new_item(win, db):
    empty = tuple()
    # Paint the item line
    win.item_choice_str('Item: ')
    item_at = win.getloc()
    #what_line = item_at[0] + 1

    # Get an existing or new category
    cats = db.get_categories()
    selected_cat = win.select_from_list(cats, 1, 0, 'Category', win.list_header_line, True) 

    if selected_cat == None:
        return empty

    if list_obj_is_new(selected_cat):
        newcatname = selected_cat[1]
        selected_cat = db.add_category(newcatname)

   
    cat_id = selected_cat[0]
    win.str_at(item_at[0], item_at[1], selected_cat[1]+', ')
    item_at = win.getloc()

    # Get an existing or new type
    types = db.get_types_for_cat(cat_id)
    selected_type = win.select_from_list(types, 1, 0, 'Type', win.list_header_line, True)  
    
    if selected_type == None:
        return empty

    if list_obj_is_new(selected_type):
        newtypename = selected_type[1]
        selected_type = db.add_type(newtypename, cat_id)

    type_id = selected_type[0]
    win.str_at(item_at[0], item_at[1], selected_type[1]+', ')
    item_at = win.getloc()

    # Get an existing or new subtype
    subtypes = db.get_subtypes_for(type_id)
    selected_stype = win.select_from_list(subtypes, 1, 0, 'subtype', win.list_header_line, True)

    if selected_stype == None:
        return empty

    if list_obj_is_new(selected_stype):
        newsubtypename = selected_stype[1]
        selected_stype = db.add_subtype(newsubtypename, type_id)

    subtype_id = selected_stype[0]
    win.str_at(item_at[0], item_at[1], selected_stype[1]+', ')
    item_at = win.getloc()

    # Get Box id
    letters = db.get_box_letters()
    selected_letter = win.select_from_list(letters, 0, 0, 'box letter', win.list_header_line, True)

    if selected_letter == None:
        return empty

    if list_obj_is_new(selected_letter):
        newletter = selected_letter[1][0].upper()
        newnumber = '1'
    else:
        newletter = selected_letter[0]
        numbers = db.get_box_numbers(selected_letter[0])
        selected_number = win.select_from_list(numbers, 0, 0, 'box number', win.list_header_line, True)

        if selected_number == None:
            return empty
        if list_obj_is_new(selected_number):
            newnumber = selected_number[1]
        else:
            newnumber = selected_number[0]
    boxid  = newletter + newnumber
    win.str_at(item_at[0], item_at[1], boxid+', ')
    item_at = win.getloc()

    # Get box location
    locations = db.get_locations()
    selected_location = win.select_from_list(locations, 0, 0, 'location', win.list_header_line, True)

    if selected_location == None:
        return empty
    if list_obj_is_new(selected_location):
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
    ni = db.add_item(cat_id, type_id, subtype_id, boxid, loc, descript)
    return (ni[0],selected_cat[1],selected_type[1],selected_stype[1],ni[4],ni[5],ni[6])




def find_item(win, db):
    global current_item

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

def find_item_by_all(win, db):
    win.restart()
    win.str_at(win.what_line, 1, 'Find item from all items:')
    items = db.get_joined_items()
    selected_item = win.select_from_list(items, -1, 0, "Items:", win.list_header_line, False)
    # will automatically return None
    return selected_item

def find_by_str_value(win, db):
    win.restart()
    win.str_at(win.what_line, 1, 'Find item by string value:')
    items = db.get_joined_items()
    selected_item = win.select_from_list(items, -1, 0, "Items:", win.list_header_line, False)
    # will automatically return None
    return selected_item

def find_item_by_cat(win, db):
    win.restart()
    win.str_at(win.what_line, 1, 'Find item by category:')
    cats = db.get_categories()
    selected_cat = win.select_from_list(cats, 1, 0, "Categories:", win.list_header_line, False)
    if selected_cat == None:
        return None
    win.restart()
    win.str_at(win.what_line, 1, 'Find item with category: '+ selected_cat[1])
    items = db.get_items_by_cat(selected_cat[0])
    selected_item = win.select_from_list(items, -1, 0, "Items:", win.list_header_line, False)
    # will automatically return when user escapes
    return selected_item

def find_item_by_cat_type(win, db):
    win.restart()
    win.str_at(win.what_line, 1, 'Find item by category and type:')
    cats = db.get_categories()
    selected_cat = win.select_from_list(cats, 1, 0, "Categories:", win.list_header_line, False)
    if selected_cat == None:
        return None
    win.restart()
    win.str_at(win.what_line, 1, 'Find item by category '+selected_cat[1]+ ' and which type:')
    types = db.get_types_for_cat(selected_cat[0])
    selected_type = win.select_from_list(types, 1, 0, "Type for Category: "+selected_cat[1], win.list_header_line, False)
    if selected_type == None:
        return None
    win.str_at(win.what_line, 1, 'Find item with category: '+ selected_cat[1] + ' and type: ' + selected_type[1])
    items = db.get_items_by_cat_type(selected_cat[0], selected_type[0])
    selected_item = win.select_from_list(items, -1, 0, "Items:", win.list_header_line, False)
    # If None, it will be returned
    return selected_item

def find_item_by_cat_type_sub(win, db):
    win.restart()
    win.str_at(win.what_line, 1, 'Find item by category, type and subtype:')
    cats = db.get_categories()
    selected_cat = win.select_from_list(cats, 1, 0, "Categories:", win.list_header_line, False)
    if selected_cat == None:
        return None

    win.restart()
    win.str_at(win.what_line, 1, 'Find item by category '+selected_cat[1]+ ' and which type:')
    types = db.get_types_for_cat(selected_cat[0])
    selected_type = win.select_from_list(types, 1, 0, "Type for Category: "+selected_cat[1], win.list_header_line, False)
    if selected_type == None:
        return None

    win.restart()
    win.str_at(win.what_line, 1, 'Find item by category '+selected_cat[1]+ ', type '+selected_type[1]+ ' and which subtype:')
    subtypes = db.get_subtypes_for(selected_type[0])
    selected_subtype = win.select_from_list(subtypes, 1, 0, "SubType for Category: "+selected_cat[1], win.list_header_line, False)
    if selected_subtype == None:
        return None

    win.str_at(win.what_line, 1, 'Find item with category: '+selected_cat[1]+', type: '+selected_type[1]+' and subtype: '+selected_subtype[1])
    items = db.get_items_by_cat_type_subtype(selected_cat[0], selected_type[0], selected_subtype[0])
    selected_item = win.select_from_list(items, -1, 0, "Items:", win.list_header_line, False)
    # None will be returned
    return selected_item

def update_something(win, db):
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

def replace_column(row, col, new_value):
    columns = row.split(sep = ', ')
    columns[col] = new_value
    new_row = ", ".join(str(x) for x in columns)
    return new_row

def get_column(row, col):
    columns = row.split(sep = ', ')
    return columns[col]

def update_item(win, db):
    global current_item
    if current_item == None or len(current_item) == 0:
        win.restart()
        win.str_at(win.what_line, 1, 'You need to select a current_item first. See the "Find" choice.')
    else:
        win.restart()
        uline = win.what_line
        nline = uline+1
        lline = uline+2
        win.str_at(uline, 1, 'Updating item: '+", ".join(str(x) for x in current_item)+'.')
        win.str_at(nline, 1, 'Start with which column ? ')
        new_item = ", ".join(str(x) for x in current_item) + '.'
        real_item = db.get_plain_item_by_id(current_item[0])
        item_id = real_item[0]
        cat_id = real_item[1]
        type_id = real_item[2]
        subtype_id = real_item[3]
        box_id = real_item[4]
        loc = real_item[5]
        descript = real_item[6]

        while(True):
            win.clrtoend(lline, 1)
            choice = win.choice_at(win.prompt_line,1,['&Category>Type>SubType','&Box','&Location','&Description','&UPDATE','&Return'],True)
            
            # Get an existing or new category
            win.clrln(nline)
            prefix = '     New item: '
            win.str_at(nline, 1, prefix + new_item)
            #orig_at = win.getloc()  #deprecated
            #item_at = orig_at       #deprecated

            if choice == 'R' or choice == cnst.ESCAPE:
                return

            if choice == 'C':
                cats = db.get_categories()
                selected_cat = win.select_from_list(cats, 1, get_column(new_item, 1), 'Category', lline, True) 

                if selected_cat == None:
                    continue

                if list_obj_is_new(selected_cat):
                    newcatname = selected_cat[1]
                    selected_cat = db.add_category(newcatname)
   
                cat_id = selected_cat[0]
                new_item = replace_column(new_item, 1, selected_cat[1])
                win.clrln(nline)
                win.str_at(nline, 1, prefix + new_item)
                #win.str_at(item_at[0], item_at[1], selected_cat[1]+', ')
                #item_at = win.getloc()
            
                # Get an existing or new type
                types = db.get_types_for_cat(cat_id)

                if cat_id != real_item[1]:  # if cat_id not equal cat_id in current_item 
                    preselecttype = 0           #   then preselect the first first type
                else:                       # else
                    preselecttype = real_item[2]#   preselect the type in current_item

                selected_type = win.select_from_list(types, 1, preselecttype, 'Type', lline, True)  
    
                if selected_type == None:
                    continue

                if list_obj_is_new(selected_type):
                    newtypename = selected_type[1]
                    selected_type = db.add_type(newtypename, cat_id)

                type_id = selected_type[0]
                new_item = replace_column(new_item, 2, selected_type[1])
                win.clrln(nline)
                win.str_at(nline, 1, prefix + new_item)
                #win.str_at(item_at[0], item_at[1], selected_type[1]+', ')
                #item_at = win.getloc()

                # Get an existing or new subtype
                subtypes = db.get_subtypes_for(type_id)

                if type_id != real_item[2]:         # if type_id not equal type_id in current_item 
                    preselectsubtype = 0            #   then preselect the first subtype
                else:                               # else
                    preselectsubtype = real_item[3] #   preselect the type in current_item

                selected_stype = win.select_from_list(subtypes, 1, preselectsubtype, 'SubType', lline, True)

                if selected_stype == None:
                    continue

                if list_obj_is_new(selected_stype):
                    newsubtypename = selected_stype[1]
                    selected_stype = db.add_subtype(newsubtypename, type_id)

                subtype_id = selected_stype[0]
                new_item = replace_column(new_item, 3, selected_stype[1])
                win.clrln(nline)
                win.str_at(nline, 1, prefix + new_item)
                #win.str_at(item_at[0], item_at[1], selected_stype[1]+', ')
                #item_at = win.getloc()

                if subtype_id == None:
                    cat_id = real_item[1]
                    type_id = real_item[2]
                    subtype_id = real_item[3]
                    new_item = current_item
                    win.clrln(nline)
                    win.str_at(nline, 1, prefix + new_item)

                #win.str_at(orig_at[0], orig_at[1],real_item[1]+', '+real_item[2]+', '+real_item[3])
                #item_at = win.getloc()

            # Get Box id

            if choice == 'B':
                letters = db.get_box_letters()
                selected_letter = win.select_from_list(letters, 0, get_column(new_item, 4)[0], 'box letter', lline, True)

                if selected_letter == None:
                    continue

                if list_obj_is_new(selected_letter):
                    newletter = selected_letter[1][0].upper()
                    newnumber = '1'
                else:
                    newletter = selected_letter[0]
                    numbers = db.get_box_numbers(selected_letter[0])
                    selected_number = win.select_from_list(numbers, 0, get_column(new_item, 4)[1:], 'box number', lline, True)

                    if selected_number == None:
                        continue

                    if list_obj_is_new(selected_number):
                        newnumber = selected_number[1]
                    else:
                        newnumber = selected_number[0]
                box_id  = newletter + newnumber
                new_item = replace_column(new_item, 4, box_id)
                win.clrln(nline)
                win.str_at(nline, 1, prefix + new_item)

            # Get box location
            if choice == 'L':
                locations = db.get_locations()
                selected_location = win.select_from_list(locations, 0, get_column(new_item, 5), 'location', lline, True)

                if selected_location == None:
                    continue

                if list_obj_is_new(selected_location):
                    loc = selected_location[1]
                else:
                    loc = selected_location[0]
                new_item = replace_column(new_item, 5, loc)
                win.clrln(nline)
                win.str_at(nline, 1, prefix + new_item)

            # Get item description
            if choice == 'D':
                descript = win.getstr_at(lline, 1, 'Enter item description') #TODO add edit ability to this function
            
                if descript == None:
                    descript = get_column(real_item, 6)

                new_item = replace_column(new_item, 6, descript)
                win.clrln(nline)
                win.str_at(nline, 1, prefix + new_item)

            # Save item to database
            if choice == 'U':
                ni = db.update_item(item_id, cat_id, type_id, subtype_id, box_id, loc, descript)
                current_item = tuple(new_item.split(sep = ', '))
                win.clrln(uline)
                win.str_at(uline, 1, 'Updating item: '+", ".join(str(x) for x in current_item)+'.')
                return 

    win.str_at(win.prompt_line,1,'Press any key to continue...')
    win.getch(cnst.ANY)
    return

# def update_item_cat(win, db,real_item):
#     win.restart()
#     win.str_at(win.what_line, 1, 'Updating item: '+repr(current_item)+'. Which column?')
#     choice = win.choice_at(win.prompt_line,1,['&Category','&Type','&SubType','&Box','&Location','&Description','&Return'],True)


# def update_item_type(real_item):
#     pass

# def update_item_subtype(real_item):
#     pass

# def update_item_box(real_item):
#     pass

# def update_item_location(real_item):
#     pass

# def update_item_description(real_item):
#    pass

def udpate_category(win, db):
    win.restart()
    uline = win.what_line
    nline = uline+1
    lline = uline+2

    cats = db.get_categories()
    win.str_at(uline,1,'Update which Category?')
    selected_cat = win.select_from_list(cats, 1, 0, 'Categories', lline, False)

    if selected_cat == None:
        return

    win.restart()
    win.str_at(uline, 1, "Update "+ selected_cat[1])
    new_value = win.getstr_at(nline,1,"New value")

    if new_value != None:
        db.update_cat(selected_cat[0], new_value)

def update_type(win, db):
    win.restart()
    uline = win.what_line
    nline = uline+1
    lline = uline+2

    types = db.get_types()
    win.str_at(uline,1,'Update which Type?')
    selected_type = win.select_from_list(types, 1, 0, 'Types', lline, False)

    if selected_type == None:
        return

    win.restart()
    win.str_at(uline, 1, "Update "+ selected_type[1])
    new_value = win.getstr_at(nline,1,"New value")

    if new_value != None:
        db.update_type(selected_type[0], new_value)


def update_subtype(win, db):
    win.restart()
    uline = win.what_line
    nline = uline+1
    lline = uline+2

    subtypes = db.get_subtypes()
    win.str_at(uline,1,'Update which SubType?')
    selected_subtype = win.select_from_list(subtypes, 1, 0, 'SubTypes', lline, False)

    if selected_subtype == None:
        return

    win.restart()
    win.str_at(uline, 1, "Update "+ selected_subtype[1])
    new_value = win.getstr_at(nline,1,"New value")

    if new_value != None:
        db.update_subtype(selected_subtype[0], new_value)


def delete_something(win, db):
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

def delete_item(win, db):
    win.restart()
    win.str_at(win.what_line, 1, 'Select item for deletion:')
    items = db.get_joined_items()
    selected_item = win.select_from_list(items, -1, 0, "Items:", win.list_header_line, False)
    if selected_item == None:
        return
    win.str_at(win.prompt_line-1, 1, 'Delete:'+repr(selected_item)+' ???')
    choice = win.choice_at(win.prompt_line, 1, ['&Yes','&No'], True)
    if choice == 'Y':
        db.delete_item(selected_item[0])
    return None

def delete_category(win, db):
    win.restart()
    win.str_at(win.what_line, 1, 'Select category for deletion:')
    cats = db.get_categories()
    selected_cat = win.select_from_list(cats, 1, 0, "Categories:", win.list_header_line, False)
    if selected_cat == None:
        return
    win.str_at(win.prompt_line-1, 1, 'Delete:'+repr(selected_cat)+' ???')
    choice = win.choice_at(win.prompt_line, 1, ['&Yes','&No'], True)
    if choice == 'Y':
        db.delete_cat(selected_cat[0])
    return None

def delete_type(win, db):
    win.restart()
    win.str_at(win.what_line, 1, 'Select type for deletion:')
    types = db.get_types()
    selected_type = win.select_from_list(types, 1, 0, "Types:", win.list_header_line, False)
    if selected_type == None:
        return
    win.str_at(win.prompt_line-1, 1, 'Delete:'+repr(selected_type)+' ???')
    choice = win.choice_at(win.prompt_line, 1, ['&Yes','&No'], True)
    if choice == 'Y':
        db.delete_type(selected_type[0])
    return None

def delete_subtype(win, db):
    win.restart()
    win.str_at(win.what_line, 1, 'Select subtype for deletion:')
    stypes = db.get_subtypes()
    selected_stype = win.select_from_list(stypes, 1, 0, "SubTypes:", win.list_header_line, False)
    if selected_stype == None:
        return
    win.str_at(win.prompt_line-1, 1, 'Delete:'+repr(selected_stype)+' ???')
    choice = win.choice_at(win.prompt_line, 1, ['&Yes','&No'], True)
    if choice == 'Y':
        db.delete_stype(selected_stype[0])
    return None

def new_something(win, db):
    global current_item
    win.restart()
    win.str_at(win.what_line, 1, 'A new which?:')
    choice = win.choice_at(win.prompt_line, 1, ['&Item','&Category','&Type','&Subtype', '&Return'], True)
    match choice:
        case 'I':
            current_item = new_item(win, db)
        case 'C':
            new_category(win, db)
        case 'T':
            new_type(win, db)
        case 'S':
            new_subtype(win, db)
        case 'R' | cnst.ESCAPE:
            return
        case _:
           try_again(win, db)

def new_category(win, db):
    cats = db.get_categories()
    win.str_at(win.what_line,1,"If your new Category is in this list, you should just esc and use the existing one.")
    win.str_at(win.what_line+1,1, "Otherwise, just type the new category name and hit Enter.")
    selected_cat = win.select_from_list(cats, 1, 0, 'Category', win.what_line+2, True) 

    if selected_cat == None:
        return

    if list_obj_is_new(selected_cat):
        newcatname = selected_cat[1]
        selected_cat = db.add_category(newcatname)

def new_type(win, db):
    cats = db.get_categories()
    win.str_at(win.what_line,1,"A new Type must belong to an existing Category. Please select")
    win.str_at(win.what_line+1,1, "the new type's parent from the existing list.")
    selected_cat = win.select_from_list(cats, 1, 0, 'Category', win.what_line+2, False) 

    if selected_cat == None:
        return

    win.restart()
    types = db.get_types_for_cat(selected_cat[0])
    win.str_at(win.what_line,1,"If your new Type is in this list, you should just esc and use the existing one.")
    win.str_at(win.what_line+1,1, "Otherwise, just type the new Type name and hit Enter.")
    new_type = win.select_from_list(types, 1, 0, 'Types', win.what_line+2, True) 

    if new_type == None:
        return

    if list_obj_is_new(new_type):
        db.add_type(new_type[1], selected_cat[0])

def new_subtype(win, db):
    win.str_at(win.what_line,1,"A new SubType must belong to an existing Category and Type. Please select")
    win.str_at(win.what_line+1,1, "the new Subtype's parent Category and Type from the following two lists.")
    cats = db.get_categories()
    selected_cat = win.select_from_list(cats, 1, 0, 'Category', win.what_line+2, False) 

    if selected_cat == None:
        return

    win.restart()
    types = db.get_types_for_cat(selected_cat[0])
    selected_type = win.select_from_list(types, 1, 0, 'Type', win.what_line+2, False) 

    if selected_type == None:
        return

    win.restart()
    subtypes = db.get_subtypes_for(selected_type[0])
    win.str_at(win.what_line,1,"If your new SubType is in this list, you should just esc and use the existing one.")
    win.str_at(win.what_line+1,1, "Otherwise, just type the new SubType name and hit Enter.")
    new_stype = win.select_from_list(subtypes, 1, 0, 'SubTypes', win.what_line+2, True)

    if new_stype == None:
        return

    if list_obj_is_new(new_stype):
        db.add_subtype(new_stype[1], selected_type[0])

def show_something(win, db):
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


def show_items(win, db):
    global current_item
    win.restart()
    win.str_at(2, 1, 'Show which items?')
    choice = win.choice_at(3, 1, ['&All','&Category =','&Type =','&Subtype =','&Return'], True)
    match choice:
        case 'A':
            current_item = show_all_items(win, db)
        case 'C':
            current_item = show_items_where_category_eq(win, db)
        case 'T':
            current_item = show_items_where_type_eq(win, db)
        case 'S':
            current_item = show_items_where_subtype_eq(win, db)
        case 'R' | cnst.ESCAPE:
            return
        case _:
            try_again(win, db)

def show_all_items(win, db):
    global current_item
    win.restart()
    items = db.get_joined_items()
    selected_item = win.select_from_list(items, -1, 0, "Showing all items:", win.what_line, False)
    if selected_item == None:
        return current_item
    return selected_item

def show_items_where_category_eq(win, db):
    global current_item
    cats = db.get_categories()
    selected_cat = win.select_from_list(cats, -1, 0, 'Select a Category', win.list_header_line, False)
    if selected_cat == None:
        return current_item
    win.restart()
    items = db. get_items_by_cat(selected_cat[0])
    selected_item = win.select_from_list(items, -1, 0, 'Select a Item', win.list_header_line, False)
    if selected_item == None:
        return current_item
    return selected_item

def show_items_where_type_eq(win, db):
    global current_item
    types = db.get_types()
    selected_type = win.select_from_list(types, -1, 0, 'Select a Type', win.list_header_line, False)
    if selected_type == None:
        return current_item
    win.restart()
    items = db. get_items_by_type(selected_type[0])
    selected_item = win.select_from_list(items, -1, 0, 'Select a Item', win.list_header_line, False)
    if selected_item == None:
        return current_item
    return selected_item

def show_items_where_subtype_eq(win, db):
    global current_item
    stypes = db.get_subtypes()
    selected_stype = win.select_from_list(stypes, -1, 0, 'Select a SubType', win.list_header_line, False)
    if selected_stype == None:
        return current_item
    win.restart()
    items = db. get_items_by_stype(selected_stype[0])
    selected_item = win.select_from_list(items, -1, 0, 'Select a Item', win.list_header_line, False)
    if selected_item == None:
        return current_item
    return selected_item



def show_categories(win, db):
    cats = db.get_categories()
    selected_cat = win.select_from_list(cats, 1, 0, 'Category', win.list_header_line, False)

def show_types(win, db):
    types = db.get_types()
    selected_type = win.select_from_list(types, 1, 0, 'Types', win.list_header_line, False)

def show_subtypes(win, db):
    stypes = db.get_subtypes()
    selected_stype = win.select_from_list(stypes, 1, 0, 'SubTypes', win.list_header_line, False)

if __name__ == "__main__":
    curses.wrapper(main)