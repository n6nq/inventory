# test_db1.py
import os
import pytest
import sqlite3
import tempfile    
from collections.abc import Iterator
from inventory.dbsqlite import Database
from inventory.models import Category, Type, Subtype, Item, String
from asserts import assertIsInstance, assertIn, assertEqual, assertTrue, assertFalse
from externals import errorHandler, prompter, silent

catnames = ["cat1", "cat2", "cat3", "cat4", "cat5"]
typenames = [("type1", 1), ("type2", 2), ("type3", 3), ("type4", 4), ("type5", 5)]
subtypenames = [("subtype1", 1), ("subtype2", 2), ("subtype3", 3), ("subtype4", 4), ("subtype5", 5)]
itemvalues = [ \
                (1, 1, 1, "X1", "closet", "some stuff1"), \
                (2, 2, 2, "X2", "closet", "some stuff2"), \
                (3, 3, 3, "X3", "closet", "some stuff3"), \
                (4, 4, 4, "X4", "closet", "some stuff4"), \
                (5, 5, 5, "X5", "closet", "some stuff5") ]

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
        for itemv in itemvalues:
            item: Item | None = db.add_item(itemv[0], itemv[1], itemv[2], itemv[3], itemv[4], itemv[5])
            # test for success
            assertIsInstance(item, Item)
            if item is not None:
                assertEqual(item.cat_id, itemv[0])
                assertEqual(item.type_id, itemv[1])
                assertEqual(item.sub_id, itemv[2])
    except sqlite3.Error:
        assertTrue(False)
        
# Arrange
@pytest.fixture(scope="module")
def db() -> Iterator[Database]:
    silent(True)
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test.db")
        database = Database(errorHandler, prompter, db_path)

        assertIsInstance(database.conn, sqlite3.Connection)
        assertIsInstance(database.cur, sqlite3.Cursor)

        stuff_cats(database)
        stuff_types(database)
        stuff_subtypes(database)
        stuff_items(database)

        try:
            yield database
        finally:
            database.conn.close()


def test_get_categories(db: Database) -> None:
    cats: list[Category] = db.get_categories()
    assertIsInstance(cats, list)
    assertEqual(len(cats), len(catnames))
    for i in range(len(cats)):
        cat = cats[i]
        assertIsInstance(cat, Category)
        assertIn(cat.c_name, catnames[i])

def test_get_types(db: Database) -> None:
    types: list[Type] = db.get_types()
    assertIsInstance(types, list)
    assertEqual(len(types), len(typenames))
    for i in range(len(types)):
        atype = types[i]
        assertIsInstance(atype, Type)
        assertIn(atype.t_name, typenames[i][0])

def test_get_subtypes(db: Database) -> None:
    subtypes: list[Subtype] = db.get_subtypes()
    assertIsInstance(subtypes, list)
    assertEqual(len(subtypes), len(subtypenames))
    for i in range(len(subtypes)):
        stype = subtypes[i]
        assertIsInstance(stype, Subtype)
        assertIn(stype.st_name, subtypenames[i][0])


# get_items(self) -> list[Item]:
def test_get_items(db: Database) -> None:
    items: list[Item] = db.get_items()
    assertIsInstance(items, list)
    assertEqual(len(items), len(itemvalues))
    for i in range(len(items)):
        item = items[i]
        assertIsInstance(item, Item)
        assertEqual(item.cat_id, itemvalues[i][0])
        assertEqual(item.type_id, itemvalues[i][1])
        assertEqual(item.sub_id, itemvalues[i][2])

# get_cat_for_id(self, cat_id: int) -> Category:
def test_get_cat_for_id(db: Database) -> None:
    cat = db.get_cat_for_id(1)
    assertIsInstance(cat, Category)
    assertEqual(cat.c_name, catnames[0])

# get_category_by_type(self, type_id: int) -> Category:
def test_get_category_by_type(db: Database) -> None:
    cat = db.get_category_by_type(1)
    assertIsInstance(cat, Category)
    assertEqual(cat.c_name, catnames[0])

# get_type_for_id(self, type_id: int) -> Type:
def test_get_type_for_id(db: Database) -> None:
    type = db.get_type_for_id(1)
    assertIsInstance(type, Type)
    assertEqual(type.t_name, typenames[0][0])

# get_types_for_cat(self, cat_id: int) -> list[Type]:
def test_get_types_for_cat(db: Database) -> None:
    types = db.get_types_for_cat(1)
    assertIsInstance(types, list)
    assertEqual(len(types), 1)
    assertEqual(types[0].t_name, typenames[0][0])

# get_subtype_for_id(self, stype_id: int) -> Subtype:
def test_get_subtype_for_id(db: Database) -> None:
    stype: Subtype | None = db.get_subtype_for_id(1)
    if stype is not None:
        assertIsInstance(stype, Subtype)
        assertEqual(stype.st_name, subtypenames[0][0])
    else:
        assertTrue(False)

# def get_subtypes_for_types(self, type_ids : list[int]) -> list[Subtype]:
def test_get_subtypes_for_types(db: Database) -> None:
    type_ids = [1, 2]
    subtypes = db.get_subtypes_for_types(type_ids)
    assertIsInstance(subtypes, list)
    assertEqual(len(subtypes), 2)
    assertEqual(subtypes[0].st_name, subtypenames[0][0])
    assertEqual(subtypes[1].st_name, subtypenames[1][0])

# get_item_by_id(self, id: int) -> Item | None:
def test_get_item_by_id(db: Database) -> None:
    item = db.get_item_by_id(1)
    if item is not None:
        assertIsInstance(item, Item)
        assertEqual(item.cat_id, itemvalues[0][0])
        assertEqual(item.type_id, itemvalues[0][1])
        assertEqual(item.sub_id, itemvalues[0][2])  
    else:
        assertTrue(False)

# get_items_by_cat(self, cat_id: int) -> list[Item]:
def test_get_items_by_cat(db: Database) -> None:
    items = db.get_items_by_cat(1)
    assertIsInstance(items, list)
    assertEqual(len(items), 1)
    item = items[0]
    assertIsInstance(item, Item)
    assertEqual(item.cat_id, itemvalues[0][0])
    assertEqual(item.type_id, itemvalues[0][1])
    assertEqual(item.sub_id, itemvalues[0][2])

# get_items_by_type(self, type_id: int) -> list[Item]:
def test_get_items_by_type(db: Database) -> None:
    items = db.get_items_by_type(1)
    assertIsInstance(items, list)
    assertEqual(len(items), 1)
    item = items[0]
    assertIsInstance(item, Item)
    assertEqual(item.cat_id, itemvalues[0][0])
    assertEqual(item.type_id, itemvalues[0][1])
    assertEqual(item.sub_id, itemvalues[0][2])

# get_items_by_stype(self, stype_id: int) -> list[Item]:
def test_get_items_by_stype(db: Database) -> None:
    items = db.get_items_by_stype(1)
    assertIsInstance(items, list)
    assertEqual(len(items), 1)
    item = items[0]
    assertIsInstance(item, Item)
    assertEqual(item.cat_id, itemvalues[0][0])
    assertEqual(item.type_id, itemvalues[0][1])
    assertEqual(item.sub_id, itemvalues[0][2])

# get_items_by_cat_type(self, cat_id: int, type_id: int) -> list[Item]:
def test_get_items_by_cat_type(db: Database) -> None:
    items = db.get_items_by_cat_type(1, 1)
    assertIsInstance(items, list)
    assertEqual(len(items), 1)
    item = items[0]
    assertIsInstance(item, Item)
    assertEqual(item.cat_id, itemvalues[0][0])
    assertEqual(item.type_id, itemvalues[0][1])
    assertEqual(item.sub_id, itemvalues[0][2])  

# get_items_by_cat_type_subtype(self, cat_id: int, type_id: int, subtype_id: int) -> list[Item]:
def test_get_items_by_cat_type_subtype(db: Database) -> None:
    items = db.get_items_by_cat_type_subtype(1, 1, 1)
    assertIsInstance(items, list)
    assertEqual(len(items), 1)
    item = items[0]
    assertIsInstance(item, Item)
    assertEqual(item.cat_id, itemvalues[0][0])
    assertEqual(item.type_id, itemvalues[0][1])
    assertEqual(item.sub_id, itemvalues[0][2])

# get_joined_items(self) -> list[String]:
def test_get_joined_items(db: Database) -> None:
    items = db.get_joined_items()
    assertIsInstance(items, list)
    assertEqual(len(items), len(itemvalues))
    for i in range(len(items)):
        j = i+1
        item = items[i]
        assertIsInstance(item, String)
        expected_str = f"{j},cat{j},type{j},subtype{j},X{j},closet,some stuff{j}" 
        assertEqual(item.string, expected_str)

# get_box_letters(self) -> list[String]:
def test_get_box_letters(db: Database) -> None:
    letters = db.get_box_letters()
    assertIsInstance(letters, list)
    assertEqual(len(letters), 1)
    expected_letters = ['X']
    for i in range(len(letters)):
        letter = letters[i]
        assertIsInstance(letter, String)
        assertEqual(letter.string, expected_letters[i])

# get_box_numbers(self, letter: str) -> list[String]:
def test_get_box_numbers(db: Database) -> None:
    box_numbers = db.get_box_numbers('X')
    assertIsInstance(box_numbers, list)
    assertEqual(len(box_numbers), 5)
    expected_box_numbers = ['1', '2', '3', '4', '5']
    for i in range(len(box_numbers)):
        box_number = box_numbers[i]
        assertIsInstance(box_number, String)
        assertEqual(box_number.string, expected_box_numbers[i])

# get_locations(self) -> list[String]:
def test_get_locations(db: Database) -> None:
    locations = db.get_locations()
    assertIsInstance(locations, list)
    assertEqual(len(locations), 1)
    expected_locations = ['closet']
    for i in range(len(locations)):
        location = locations[i]
        assertIsInstance(location, String)
        assertEqual(location.string, expected_locations[i])

# update_item(self, it: Item) -> None:
def test_update_item(db: Database) -> None:
    item = db.get_item_by_id(1)
    assertIsInstance(item, Item)

    original_description = ""
    new_description = "Updated description"

    if item is not None:
        original_description = item.descript
        item.descript = new_description

    if item is not None:
        assertTrue(db.update_item(item))
    else:
        assertTrue(False)  # Item should not be None for a valid ID

    updated_item = db.get_item_by_id(1)
    if updated_item is not None:
        assertIsInstance(updated_item, Item)
        assertEqual(updated_item.descript, new_description)
        # Restore original description
        updated_item.descript = original_description
        assertTrue(db.update_item(updated_item))        
    else:
        assertTrue(False)  # Updated item should not be None for a valid ID


    updated_item = db.get_item_by_id(1)
    if updated_item is not None:
        assertIsInstance(updated_item, Item)
        assertEqual(updated_item.descript, original_description)

# update_cat(self, cat_id: int, new_value: str) -> None:
def test_update_cat(db: Database) -> None:
    cat = db.get_cat_for_id(1)
    assertIsInstance(cat, Category)

    original_name = ""
    new_name = "Updated Category Name"

    original_name = cat.c_name

    assertTrue(db.update_cat(1, new_name))

    updated_cat = db.get_cat_for_id(1)

    assertIsInstance(updated_cat, Category)
    assertEqual(updated_cat.c_name, new_name)
    # Restore original name
    assertTrue(db.update_cat(1, original_name) )    

    updated_cat = db.get_cat_for_id(1)

    assertIsInstance(updated_cat, Category)
    assertEqual(updated_cat.c_name, original_name)

# update_type(self, type_id: int, new_value: str) -> None:
def test_update_type(db: Database) -> None:
    atype = db.get_type_for_id(1)
    assertIsInstance(atype, Type)

    original_name = ""
    new_name = "Updated Type Name"

    original_name = atype.t_name

    assertTrue(db.update_type(1, new_name))

    updated_type = db.get_type_for_id(1)

    assertIsInstance(updated_type, Type)
    assertEqual(updated_type.t_name, new_name)
    # Restore original name
    assertTrue(db.update_type(1, original_name))    

    updated_type = db.get_type_for_id(1)

    assertIsInstance(updated_type, Type)
    assertEqual(updated_type.t_name, original_name)

# update_subtype(self, subtype_id: int, new_value: str) -> None:
def test_update_subtype(db: Database) -> None:
    stype: Subtype | None = db.get_subtype_for_id(1)
    if stype is not None:
        assertIsInstance(stype, Subtype)
        original_name = stype.st_name
        new_name = "Updated Subtype Name"

        assertTrue(db.update_subtype(1, new_name))
        updated_subtype: Subtype | None = db.get_subtype_for_id(1)
        if updated_subtype is not None:
            assertIsInstance(updated_subtype, Subtype)
            assertEqual(updated_subtype.st_name, new_name)
            # Restore original name
            assertTrue(db.update_subtype(1, original_name))    
            updated_subtype = db.get_subtype_for_id(1)
            if updated_subtype is not None:
                assertIsInstance(updated_subtype, Subtype)
                assertEqual(updated_subtype.st_name, original_name)
            else:
                assertTrue(False)  # Updated subtype should not be None for a valid ID
        else:
            assertTrue(False)  # Updated subtype should not be None for a valid ID
    else:
        assertTrue(False)  # Subtype should not be None for a valid ID
    

# delete_stype(self, stype_id: int) -> None:
def test_delete_stype(db: Database) -> None:
    # Add a new subtype to delete
    new_stype: Subtype | None = db.add_subtype("temp_subtype", 1)
    assertIsInstance(new_stype, Subtype)
    if new_stype is not None:
        stype_id = new_stype.id
        # Ensure the subtype exists
        assertTrue(db.stype_exists(stype_id))
        # Delete the subtype
        assertTrue(db.delete_stype(stype_id))
        # Ensure the subtype no longer exists
        assertFalse(db.stype_exists(stype_id))
    else:
        assertTrue(False)  # New subtype should not be None
    
    # Now try to delete one that is referenced by an item (should raise an error)
    assertFalse(db.delete_stype(1))  # Delete will fail since it's referenced by an item

# delete_type(self, type_id: int) -> None:
def test_delete_type(db: Database) -> None:
    # Add a new type to delete
    new_type: Type | None = db.add_type("temp_type", 1)
    assertIsInstance(new_type, Type)
    if new_type is not None:
        type_id = new_type.id
        # Ensure the type exists
        assertTrue(db.type_exists(type_id))
        # Delete the type
        assertTrue(db.delete_type(type_id))
        # Ensure the type no longer exists
        assertFalse(db.type_exists(type_id))
    else:
        assertTrue(False)  # New type should not be None
    # Now try to delete one that is referenced by an item (should raise an error)
    assertFalse(db.delete_type(1))  # This should raise an error since it's referenced by an item

# delete_cat(self, cat_id: int) -> None:
def test_delete_cat(db: Database) -> None:
    # Add a new category to delete
    new_cat: Category | None = db.add_category("temp_category")
    assertIsInstance(new_cat, Category)
    if new_cat is not None:
        cat_id = new_cat.id
        # Ensure the category exists
        assertTrue(db.cat_exists(cat_id))
        # Delete the category
        assertTrue(db.delete_cat(cat_id))
        # Ensure the category no longer exists
        assertFalse(db.cat_exists(cat_id))
    else:
        assertTrue(False)  # New category should not be None
    # Now try to delete one that is referenced by an item (should raise an error)
    assertFalse(db.delete_cat(1))  # This should raise an error since it's referenced by an item

# delete_item(self, item_id: int) -> None:
def test_delete_item(db: Database) -> None:
    # Add a new item to delete
    new_item: Item | None = db.add_item(1, 1, 1, "temp_box", "temp_location", "temp_description")
    assertIsInstance(new_item, Item)
    if new_item is not None:
        item_id = new_item.id
        # Ensure the item exists
        assertIsInstance(db.get_item_by_id(item_id), Item)
        # Delete the item
        assertTrue(db.delete_item(item_id))
        # Ensure the item no longer exists
        assertIsInstance(db.get_item_by_id(item_id), type(None))
    else:
        assertTrue(False)  # New item should not be None

# check_cat(self, cat_id: int) -> bool:
# check_type(self, type_id: int) -> bool:

