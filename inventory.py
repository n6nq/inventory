import psycopg2
from window import CmdWindow
from database import Database

def main():
    win = CmdWindow()
    # Print first screen
    win.set_title('Inventory program, Ver 0.01')
    win.restart()
    win.str_at(2,10, 'Press any key to continue...')
    #win.bell()
    win.getch()
    win.clrln(2)
    win.save_loc()

    db = Database(win)
    win.restore_loc()
    win.restart()

    while(True):
        win.restart()
        choice = win.choice_at(2, 1, ['New','Find','Show','Delete','Exit'], True)

        match choice:
            case 'N':
                new_item(win, db)
            case 'F':
                find_something(win, db)
            case 'D':
                delete_something(win, db)
            case 'S':
                show_something(win, db)
            case 'E':
                exit()
            case _:
                print('handle_not_choice')

def new_item(win, db):
    # Paint the item line
    item_at = win.getloc()
    win.str_at(item_at[0], 1, 'Item: ')
    item_at = win.getloc()
    choice_line = item_at[0] + 1

    # Get an existing or new category
    cats = db.get_categories()
    selected_cat = win.select_from_list(choice_line, 'Category', cats, 1)
    if selected_cat[0] == -1:
        newcatname = selected_cat[1]
        selected_cat = db.add_category(newcatname)
    elif selected_cat[0] == -2:                     # todo
        return
    cat_id = selected_cat[0]
    win.str_at(item_at[0], item_at[1], selected_cat[1]+', ')
    item_at = win.getloc()

    # Get an existing or new type
    types = db.get_types_for(cat_id)
    selected_type = win.select_from_list(choice_line, 'Type', types, 1)
    if selected_type[0] == -1:
        newtypename = selected_type[1]
        selected_type = db.add_type(newtypename, cat_id)
    elif selected_type[0] == -2:                     # todo
        return
    type_id = selected_type[0]
    win.str_at(item_at[0], item_at[1], selected_type[1]+', ')
    item_at = win.getloc()

    # Get an existing or new subtype
    subtypes = db.get_subtypes_for(type_id)
    selected_stype = win.select_from_list(choice_line, 'subtype', subtypes, 1)
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
    selected_letter = win.select_from_list(choice_line, 'letter', letters, 0)
    if selected_letter[0] == -1:
        newletter = selected_letter[1][0].upper()
        newnumber = '1'
    elif selected_letter[0] == -2:                     # todo
        return
    else:
        newletter = selected_letter[0]
        numbers = db.get_box_numbers(selected_letter[0])
        selected_number = win.select_from_list(choice_line, 'number', numbers, 0)
        if selected_number[0] == -1:
            newnumber = selected_number[1]
        elif selected_number[0] == -2:                     # todo
            return
        else:
            newnumber = selected_number[0]
    boxid  = newletter + newnumber
    win.str_at(item_at[0], item_at[1], boxid+', ')
    item_at = win.getloc()

    # Get boxes location
    locations = db.get_locations()
    selected_location = win.select_from_list(choice_line, 'location',locations, 0)
    if selected_location[0] == -1:
        loc = selected_location[1]
    else:
        loc = selected_location[0]
    win.str_at(item_at[0], item_at[1], loc+', ')
    item_at = win.getloc()

    # Get item description
    descript = win.getstr_at(choice_line, 1, 'Enter item description')
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
    choice = win.choice_at(2, 1, ['Items','Categories','Types','Subtypes','Return'], True)
    match choice:
        case 'I':
            show_items(win, db)
        case 'C':
            show_categories(win, db)
        case 'T':
            show_types(win, db)
        case 'S':
            show_subtypes(win, db)
        case 'R':
            return
        case _:
            print('handle_not_choice')


def show_items(win, db):
    win.restart()
    win.str_at(2, 1, 'Showing which items?')
    choice = win.choice_at(2, 1, ['All','Category =','Type =','Subtype =','Exit'], True)
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
    selected_item = win.select_from_list(3, 'item',items, -1)

def show_categories(win, db):
    pass


def show_types(win, db):
    pass


def show_subtypes(win, db):
    pass


    
    
    
    
    pass

main()
exit()


cur.execute("insert into category (c_name) values (%s)", ("testcat",))
cur.execute("select max(id) from category;")
row = cur.fetchone()
newcat = row[0]
print(row)
print()
cur.execute("insert into type (t_name, cat) values (%s, %s)", ("testtype", newcat))
cur.execute("select max(id) from type;")
row = cur.fetchone()
newtype = row[0]
print(row)
print()
cur.execute("insert into subtype (st_name, atype) values (%s, %s)", ("testsub", newtype))
cur.execute("select max(id) from subtype;")
row = cur.fetchone()
newsubtype = row[0]
print(row)
print()
cur.execute("insert into item (cat, atype, subtype, box, loc, descript) values (%s, %s, %s, %s, %s, %s)", (newcat, newtype, newsubtype, "B1", "closet", "a silly test item"))
cur.execute("select * from item;")

row = cur.fetchone()
print(row)
print()

