# stuff_db.py --- stuff_db() and it's supporting functions are used to create a temporary database for testing purposes. 
# The database is created in a temporary directory and is deleted after the tests are completed. This allows for testing 
# without affecting the production database. Tis function can be used by any fixture code that needs a populated database 
# for testing purposes. It can also be usedwhile debugging the applicaction. See the class Database constructor for more 
# information on how to use this function.

from inventory.dbsqlite import Database
from inventory.asserts import assertIsInstance, assertIn, assertEqual, assertTrue
from sqlite3 import Connection, Cursor, Error

from inventory.models import Category, Type, Subtype, Item

# Number of categories, type and subtype
N_CATS = 5

# Number of items
N_ITEMS = 35

catnames = ["cat1", "cat2", "cat3", "cat4", "cat5"]
typenames = [("type1", 1), ("type2", 2), ("type3", 3), ("type4", 4), ("type5", 5)]
subtypenames = [("subtype1", 1), ("subtype2", 2), ("subtype3", 3), ("subtype4", 4), ("subtype5", 5)]

def stuff_db(db: Database) -> None:

    assertIsInstance(db.conn, Connection)
    assertIsInstance(db.cur, Cursor)

    stuff_cats(db)
    stuff_types(db)
    stuff_subtypes(db)
    stuff_items(db)

def stuff_cats(db: Database) -> None:
    try:
        for name in catnames:
            cat: Category | None = db.add_category(name)
            # test for success
            assertIsInstance(cat, Category)
            if cat is not None:
                assertEqual(cat.c_name, name)
    except Error:
        assertTrue(False) 
        
def stuff_types(db: Database) -> None:
    try:
        for name, cat_id in typenames:
            atype: Type | None = db.add_type(name, cat_id)
            # test for success
            assertIsInstance(atype, Type)
            if atype is not None:
                assertEqual(atype.t_name, name)
    except Error:
        assertTrue(False) 

def stuff_subtypes(db: Database) -> None:
    try:
        for name, type_id in subtypenames:
            stype: Subtype | None = db.add_subtype(name, type_id)
            # test for success
            assertIsInstance(stype, Subtype)
            if stype is not None:
                assertEqual(stype.st_name, name)
    except Error:
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
    except Error:
        assertTrue(False)