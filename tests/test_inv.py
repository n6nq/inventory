# test_db1.py
from typing import Callable
import pytest
import sqlite3
from inventory.dbsqlite import Database
from inventory.models import Category, Type, Subtype, Item
from asserts import assertIsInstance, assertEqual, assertTrue
from inventory.main import run_app
from inventory.screenfake import ScreenFake, Page
from inventory.window import CmdWindow
from externals import errorHandler, prompter
import inventory.cnst as cnst
from pytest import TempPathFactory

# Number of categories, type and subtype
N_CATS = 5

# Number of items
N_ITEMS = 35

catnames = ["cat1", "cat2", "cat3", "cat4", "cat5"]
typenames = [("type1", 1), ("type2", 2), ("type3", 3), ("type4", 4), ("type5", 5)]
subtypenames = [("subtype1", 1), ("subtype2", 2), ("subtype3", 3), ("subtype4", 4), ("subtype5", 5)]

def stuff_cats(db: Database) -> None:
    try:
        for name in catnames:
            cat: Category | None = db.add_category(name)
            # test for success
            assertIsInstance(cat, Category)
            if cat is not None:
                assertEqual(cat.c_name, name)
    except sqlite3.Error:
        assertTrue(False) 
        
def stuff_types(db: Database) -> None:
    try:
        for name, cat_id in typenames:
            atype: Type | None = db.add_type(name, cat_id)
            # test for success
            assertIsInstance(atype, Type)
            if atype is not None:
                assertEqual(atype.t_name, name)
    except sqlite3.Error:
        assertTrue(False) 

def stuff_subtypes(db: Database) -> None:
    try:
        for name, type_id in subtypenames:
            stype: Subtype | None = db.add_subtype(name, type_id)
            # test for success
            assertIsInstance(stype, Subtype)
            if stype is not None:
                assertEqual(stype.st_name, name)
    except sqlite3.Error:
        assertTrue(False) 
        
def stuff_items(db: Database) -> None:
    try:
        for i in range(1, N_ITEMS +1):
            cts = N_CATS if (i % N_CATS) == 0 else (i % N_CATS)     # cat, type, subtype index, there are only 5 of 
            item: Item | None = db.add_item(cts, cts, cts, f"X{cts}", "closet", f"some stuff{i}")
            # test for success
            assertIsInstance(item, Item)
            if item is not None:
                assertEqual(item.cat_id, cts)
                assertEqual(item.type_id, cts)
                assertEqual(item.sub_id, cts)
                assertEqual(item.descript, f"some stuff{i}")
    except sqlite3.Error:
        assertTrue(False)

class TstBits:
    def __init__(self, db: Database, win: CmdWindow, screen: ScreenFake):
        self.db = db
        self.win = win
        self.screen = screen

global_tstbits = None

# Arrange
@pytest.fixture(scope="module")
def tstbits(tmp_path_factory: TempPathFactory):
    temp_dir = tmp_path_factory.mktemp("inventory")
    db_path = temp_dir / "test.db"

    database = Database(errorHandler, prompter, str(db_path))
    assertIsInstance(database.conn, sqlite3.Connection)
    assertIsInstance(database.cur, sqlite3.Cursor)

    stuff_cats(database)
    stuff_types(database)
    stuff_subtypes(database)
    stuff_items(database)


    screen = ScreenFake()
    win = CmdWindow(screen)
    yield TstBits(database, win, screen)


def test_0_home(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    db: Database = tstbits.db
    win: CmdWindow = tstbits.win

    screen.input(["DUMP,page0","e"])  # Simulate pressing 'f' 'a' to Find All items,then move down one
    run_app(win,db)
    page: Page = screen.getpage("page0")
    assertTrue(page.str_in_line("Inventory", 0))
    assertTrue(page.str_in_line("Ver 0.01", 0))
    assertTrue(page.str_in_line("Empty", 1))
    assertTrue(page.str_in_line("Choose one:", -1))
    assertTrue(page.str_in_line("Exit", -1))   

subtestcallbacks: dict[str, Callable[[TstBits], None]] = {}

bits: TstBits 

def subTestCallback(name: str):
    global bits
    assert subtestcallbacks[name], f"{name} not in subtestcallbacks! test program error"
    
    subtestcallbacks[name](bits)
    

def test_1_new_item(tstbits: TstBits):
    global bits, subtestcallbacks
    bits = tstbits
    screen: ScreenFake = tstbits.screen
    db: Database = tstbits.db
    win: CmdWindow = tstbits.win
    screen.register_cb(subTestCallback)
    screen.input(["i","DUMP,page0,newItemSub0"])	# jump to the new item input page, callback newItemSub0() to check it
    subtestcallbacks["newItemSub0"] = newItemSub0   # setup the callback
    run_app(win,db)
    # we are back from all the callbacks, so clean callback dictionary
    subtestcallbacks = {}
    screen.clearpages()

def newItemSub0(tstbits: TstBits) -> None:
    screen = tstbits.screen
    page: Page = screen.getpage("page0")        # checking the newItem page0
    assertTrue(page.str_in_line("Item:", 1))
    assertTrue(page.str_in_line("Category", 2))
    assertTrue(page.str_in_line(">", 3))
    assertTrue(page.str_in_line("Search", -1))
    assertTrue(page.str_in_line("ESC=Cancel", -1))
    screen.input(["KEY_ENTER","DUMP,page1,newItemSub1"])    # KEY_ENTER selects the first category and jumps to the type page
    subtestcallbacks["newItemSub1"] = newItemSub1           # callback newItemSub1 will check the type page
    return  #to app execution

def newItemSub1(tstbits: TstBits) -> None:
    screen = tstbits.screen
    page: Page = screen.getpage("page1")	
    assertTrue(page.str_in_line("cat1", 1))
    assertTrue(page.str_in_line("Type", 2))
    assertTrue(page.str_in_line("> type1", 3))
    assertTrue(page.str_in_line("Search:", -1))
    screen.input(["KEY_ENTER","DUMP,page2,newItemSub2"])
    subtestcallbacks["newItemSub2"] = newItemSub2
    return

def newItemSub2(tstbits: TstBits) -> None:
    screen = tstbits.screen
    page: Page = screen.getpage("page2")
    assertTrue(page.str_in_line("type1", 1))
    assertTrue(page.str_in_line("Subtype", 2))
    assertTrue(page.str_in_line("subtype1", 3))
    assertTrue(page.str_in_line("Search", -1))
    screen.input(["KEY_ENTER","DUMP,page3,newItemSub3"])
    subtestcallbacks["newItemSub3"] = newItemSub3
    return

def newItemSub3(tstbits: TstBits) -> None:
    screen = tstbits.screen
    page: Page = screen.getpage("page3")
    assertTrue(page.str_in_line("subtype1", 1))
    assertTrue(page.str_in_line("Box Letters", 2))
    assertTrue(page.str_in_line("X", 3))
    assertTrue(page.str_in_line("Search:", -1))
    screen.input(["KEY_ENTER","DUMP,page4,newItemSub4"])
    subtestcallbacks["newItemSub4"] = newItemSub4
    return

def newItemSub4(tstbits: TstBits) -> None:
    screen = tstbits.screen
    page: Page = screen.getpage("page4")
    assertTrue(page.str_in_line("subtype1", 1))
    assertTrue(page.str_in_line("Box Numbers", 2))
    assertTrue(page.str_in_line("> 1", 3))
    assertTrue(page.str_in_line("Search:", -1))
    screen.input(["KEY_ENTER","DUMP,page5,newItemSub5"])
    subtestcallbacks["newItemSub5"] = newItemSub5
    return

def newItemSub5(tstbits: TstBits) -> None:
    screen = tstbits.screen
    page: Page = screen.getpage("page5")
    assertTrue(page.str_in_line("X1", 1))
    assertTrue(page.str_in_line("Locations", 2))
    assertTrue(page.str_in_line("> closet", 3))
    assertTrue(page.str_in_line("Search:", -1))
    screen.input(["KEY_ENTER","DUMP,page6,newItemSub6"])
    subtestcallbacks["newItemSub6"] = newItemSub6
    return

def newItemSub6(tstbits: TstBits) -> None:
    screen = tstbits.screen
    page: Page = screen.getpage("page6")
    assertTrue(page.str_in_line("closet", 1))
    assertTrue(page.str_in_line("description:", 2))
    assertTrue(page.str_in_line("          ", -1))
    screen.input(["s","o","m","e"," ","s","t","u","f","f","3","5","KEY_BACKSPACE","6","KEY_ENTER","DUMP,page7,newItemSub7","e"]) # app exit choice
    subtestcallbacks["newItemSub7"] = newItemSub7
    return
    
def newItemSub7(tstbits: TstBits) -> None:
    screen = tstbits.screen
    page: Page = screen.getpage("page7")
    assertTrue(page.str_in_line("Current_item:", 1))
    assertTrue(page.str_in_line("some stuff36", 1))
    assertTrue(page.str_in_line("Choose one:", -1))
    return

def test_2_find_all_items(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    db: Database = tstbits.db
    win: CmdWindow = tstbits.win


    screen.input(["f", "a","DUMP,find_all0","s","t","u","f","f","5","DUMP,find_all1","KEY_ENTER","e"])  # Simulate pressing 'f' 'a' to Find All items,then move down one
    run_app(win,db)
    screen.dump("find_all2")
    page: Page = screen.getpage("find_all0")
    assertTrue(page.str_in_line(">", 3))
    page = screen.getpage("find_all1")
    assertTrue(page.str_in_line(">", 7))
    page = screen.getpage("find_all2")
    assertTrue(page.str_in_line("stuff5",1))

    #subtestcallbacks = {}
    screen.clearpages()

def test_3_find_all_items(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    db: Database = tstbits.db
    win: CmdWindow = tstbits.win

    screen.input(["f","a","s","t","u","f","f","3","2","DUMP,find_all3","KEY_ENTER","e"])  # Simulate pressing 'f' 'a' to Find All items,then move down one
    run_app(win,db)
    screen.dump("find_all4")
    page: Page = screen.getpage("find_all3")
    assertTrue(page.str_in_line(">", 23))
    assertTrue(page.str_in_line("stuff32", 23))
    page = screen.getpage("find_all4")
    assertTrue(page.str_in_line("stuff32", 1))
    
    #subtestcallbacks = {}
    screen.clearpages()

def test_4_new_item(tstbits: TstBits) -> None:	        #only goes to Item choice
    global bits, subtestcallbacks
    bits = tstbits                                      # set global bits for the callbacks
    screen: ScreenFake = tstbits.screen
    db: Database = tstbits.db
    win: CmdWindow = tstbits.win

    screen.input(["n","DUMP,page0,newSub0","i","DUMP,page1,newSub1",cnst.ESCAPE,cnst.ESCAPE,"e"])
    subtestcallbacks["newSub0"] = newSub0
    subtestcallbacks["newSub1"] = newSub1
    run_app(win,db)

    subtestcallbacks = {}
    screen.clearpages()

def newSub0(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    page: Page = screen.getpage("page0")

    assertTrue(page.str_in_line("A new which?", 1))
    assertTrue(page.str_in_line("Choose one:", -1))
    assertTrue(page.str_in_line("Subtype, Return, Esc", -1))

def newSub1(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    page: Page = screen.getpage("page1")
    assertTrue(page.str_in_line("Item:", 1))
    assertTrue(page.str_in_line("Category", 2))
    assertTrue(page.str_in_line("> cat1", 3))
    assertTrue(page.str_in_line("Search:", -1))
    assertTrue(page.str_in_line("ESC=Cancel", -1))


def test_5_new_cat(tstbits: TstBits) -> None:
    global bits, subtestcallbacks
    bits = tstbits
    screen: ScreenFake = tstbits.screen
    db: Database = tstbits.db
    win: CmdWindow = tstbits.win


    screen.input(["n","DUMP,page0,newcatSub0","c","DUMP,page1,newcatSub1"])
    subtestcallbacks["newcatSub0"] = newcatSub0
    subtestcallbacks["newcatSub1"] = newcatSub1
    subtestcallbacks["newcatSub2"] = newcatSub2
    subtestcallbacks["newcatSub3"] = newcatSub3
    run_app(win,db)
	# clean up
    subtestcallbacks = {}
    screen.clearpages()

def newcatSub0(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    page: Page = screen.getpage("page0")

    assertTrue(page.str_in_line("A new which?", 1))
    assertTrue(page.str_in_line("Choose one:", -1))
    assertTrue(page.str_in_line("Subtype, Return, Esc", -1))
	
def newcatSub1(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    page: Page = screen.getpage("page1")

    assertTrue(page.str_in_line("If your new Category", 1))
    assertTrue(page.str_in_line(" Otherwise,", 2))
    assertTrue(page.str_in_line("Category", 3))
    assertTrue(page.str_in_line("Search:", -1))
    screen.input(["c","a","t","6","DUMP,page2,newcatSub2"])
    screen.input(["KEY_ENTER","s","c","c","a","t","6","DUMP,page3,newcatSub3"])	

def newcatSub2(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    page: Page = screen.getpage("page2")
    assertTrue(page.str_in_line(" New Category?",-1))
    assertTrue(page.str_in_line("cat6", -1))
	
def newcatSub3(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    page: Page = screen.getpage("page3")

    assertTrue(page.str_in_line("Show which?:", 1))
    assertTrue(page.str_in_line("Category", 2))
    assertTrue(page.find_in_page("> cat6"))
    assertTrue(page.str_in_line("Search: cat6", -1))
    screen.input([cnst.ESCAPE,"e"])


def test_6_new_type(tstbits: TstBits) -> None:
    global bits, subtestcallbacks
    bits = tstbits
    screen: ScreenFake = tstbits.screen
    db: Database = tstbits.db
    win: CmdWindow = tstbits.win


    screen.input(["n","DUMP,page0,newtypeSub0","t","DUMP,page1,newtypeSub1"])
    subtestcallbacks["newtypeSub0"] = newtypeSub0
    subtestcallbacks["newtypeSub1"] = newtypeSub1
    subtestcallbacks["newtypeSub2"] = newtypeSub2
    subtestcallbacks["newtypeSub3"] = newtypeSub3
    run_app(win,db)
	# clean up
    subtestcallbacks = {}
    screen.clearpages()

def newtypeSub0(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    page: Page = screen.getpage("page0")

    assertTrue(page.str_in_line("A new which?", 1))
    assertTrue(page.str_in_line("Choose one:", -1))
    assertTrue(page.str_in_line("Subtype, Return, Esc", -1))
	
def newtypeSub1(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    page: Page = screen.getpage("page1")

    assertTrue(page.str_in_line("A new Type must belong", 1))
    assertTrue(page.str_in_line(" Please select", 2))
    assertTrue(page.str_in_line("Category", 3))
    assertTrue(page.str_in_line("Search:", -1))
    screen.input(["c","a","t","6","DUMP,page2,newtypeSub2"])

    screen.input(["KEY_ENTER","DUMP,page3,newtypeSub3"])	

def newtypeSub2(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    page: Page = screen.getpage("page2")
    assertTrue(page.str_in_line(" Search: cat6",-1))
    assertTrue(page.find_in_page("> cat6"))

def newtypeSub3(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    page: Page = screen.getpage("page3")

    assertTrue(page.str_in_line("If your new Type", 1))
    assertTrue(page.str_in_line("Type", 2))
    assertTrue(page.str_in_line("Search:", -1))
    assertTrue(page.str_in_line("ESC=Cancel)", -1))
    screen.input(["t","y","p","e","6","KEY_ENTER","e"])

def test_7_new_subtype(tstbits: TstBits) -> None:
    global bits, subtestcallbacks
    bits = tstbits
    screen: ScreenFake = tstbits.screen
    db: Database = tstbits.db
    win: CmdWindow = tstbits.win


    subtestcallbacks["newsubtypeSub0"] = newsubtypeSub0
    subtestcallbacks["newsubtypeSub1"] = newsubtypeSub1
    subtestcallbacks["newsubtypeSub2"] = newsubtypeSub2
    subtestcallbacks["newsubtypeSub3"] = newsubtypeSub3
    subtestcallbacks["newsubtypeSub4"] = newsubtypeSub4
    subtestcallbacks["newsubtypeSub5"] = newsubtypeSub5
    screen.input(["DUMP,page0,newsubtypeSub0"])
    run_app(win,db)
	# clean up
    subtestcallbacks = {}
    screen.clearpages()

def newsubtypeSub0(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    page: Page = screen.getpage("page0")

    assertTrue(page.str_in_line("Current_item: Empty", 1))
    assertTrue(page.str_in_line("Choose one:", -1))
    assertTrue(page.str_in_line("Delete, Exit, Esc", -1))
    screen.input(["n","DUMP,page1,newsubtypeSub1"])
	
def newsubtypeSub1(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    page: Page = screen.getpage("page1")

    assertTrue(page.str_in_line("A new which?:", 1))
    assertTrue(page.str_in_line("Choose one: Item, Category,", -1))
    screen.input(["s","c","a","t","6","DUMP,page2,newsubtypeSub2"])

    

def newsubtypeSub2(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    page: Page = screen.getpage("page2")
    assertTrue(page.str_in_line("A new SubType must belong",1))
    assertTrue(page.str_in_line("the new Subtype's parent Category",2))
    assertTrue(page.str_in_line("Category",3))
    assertTrue(page.find_in_page("> cat6"))
    assertTrue(page.str_in_line(" Search: cat6",-1))
    screen.input(["KEY_ENTER","t","y","p","e","6","DUMP,page3,newsubtypeSub3"])

def newsubtypeSub3(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    page: Page = screen.getpage("page3")

    assertTrue(page.str_in_line("A new SubType must belong to an existing Type.", 1))
    assertTrue(page.str_in_line("Type", 2))
    assertTrue(page.find_in_page("> type6"))
    assertTrue(page.str_in_line("Search: type6", -1))
    assertTrue(page.str_in_line("ESC=Cancel)", -1))
    screen.input(["KEY_ENTER","s","u","b","t","y","p","e","6","DUMP,page4,newsubtypeSub4"])

def newsubtypeSub4(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    page: Page = screen.getpage("page4")

    assertTrue(page.str_in_line("If your new SubType", 1))
    assertTrue(page.str_in_line("Otherwise,", 2))
    assertTrue(page.str_in_line("New Subtype?", -1))
    assertTrue(page.str_in_line("subtype6", -1))
    screen.input(["KEY_ENTER","s","s","s","u","b","t","y","p","e","6","DUMP,page5,newsubtypeSub5"])

def newsubtypeSub5(tstbits: TstBits) -> None:
    screen: ScreenFake = tstbits.screen
    page: Page = screen.getpage("page5")

    assertTrue(page.find_in_page("> subtype6"))
    screen.input(["KEY_ENTER","e"])