# test_db1.py
import pytest
import sqlite3
from pytest import TempPathFactory
from inventory.dbsqlite import Database
from inventory.models import Category, Type, Subtype, Item
from externals import errorHandler, prompter, silent
from asserts import assertIsInstance, assertIn, assertEqual, assertTrue



# Arrange
@pytest.fixture(scope="module")
def db(tmp_path_factory: TempPathFactory):
    silent(True)
    temp_dir = tmp_path_factory.mktemp("inventory")
    db_path = temp_dir / "test.db"
    
    database = Database(errorHandler, prompter, str(db_path))

    assert isinstance(database.conn, sqlite3.Connection)
    assert isinstance(database.cur, sqlite3.Cursor)

    yield database


def test_a_schema_integrity(db: Database) -> None:
    # Good to go?
    assertIsInstance(db.conn, sqlite3.Connection)

    # insert subtype
    try:
        db.cur.execute('insert into subtype (st_name, atype) values ("subtype1", 1);')
        #	fail on type
    except sqlite3.Error as e:
        assertIsInstance(e, sqlite3.IntegrityError)
        assertIn('FOREIGN KEY constraint failed', str(e))

    # insert type
    try:
        db.cur.execute('insert into type (t_name, cat) values ("type1", 1)')
    #	fail on category
    except sqlite3.Error as e:
        assertIsInstance(e, sqlite3.IntegrityError)
        assertIn('FOREIGN KEY constraint failed', str(e))

    # insert category
    try:
        db.cur.execute('insert into category (c_name) values ("category1") returning id, c_name;')
    #	test for success
        row = db.cur.fetchone()
        assertEqual(row[1], "category1")
    except sqlite3.Error as e:
        assertTrue(False)
        #assertIsInstance(e, sqlite3.IntegrityError)
        #assertIn('FOREIGN KEY constraint failed', str(e))

    # insert type
    try:
        db.cur.execute('insert into type (t_name, cat) values ("type1", 1) returning id, t_name')
    #	test for success
        row = db.cur.fetchone()
        assertEqual(row[1], "type1")
    except sqlite3.Error as e:
        assertTrue(False)

    # insert subtype
    try:
        db.cur.execute('insert into subtype (st_name, atype) values ("subtype1", 1) returning id, st_name;')
    #	test for success
        row = db.cur.fetchone()
        assertEqual(row[1], "subtype1")
    except sqlite3.Error as e:
        assertTrue(False)

    # insert item correct cat, type, subtype
    try:
        db.cur.execute("insert into item (cat, atype, subtype, box, loc, descript) values (1, 1, 1, 'Box1', 'Location1', 'Description1') returning id, cat, atype, subtype;")
    #	test for success
        row = db.cur.fetchone()
        assertEqual(row[1], 1)
        assertEqual(row[2], 1)
        assertEqual(row[3], 1)
    except sqlite3.Error as e:
        assertTrue(False)

    # insert item wrong cat, type, subtype
    try:
        db.cur.execute("insert into item (cat, atype, subtype, box, loc, descript) values (2, 1, 1, 'Box1', 'Location1', 'Description1');")
    #	fail on category
    except sqlite3.Error as e:
        assertIsInstance(e, sqlite3.IntegrityError)
        assertIn("FOREIGN KEY constraint failed", str(e))

    # insert item correct cat, wrong type, subtype
    try:
        db.cur.execute("insert into item (cat, atype, subtype, box, loc, descript) values (1, 2, 1, 'Box1', 'Location1', 'Description1');")
        #	fail on type
    except sqlite3.Error as e:
        assertIsInstance(e, sqlite3.IntegrityError)
        assertIn("FOREIGN KEY constraint failed", str(e))

    # insert item correct cat, type, wrong subtype
    try:
        db.cur.execute("insert into item (cat, atype, subtype, box, loc, descript) values (1, 1, 2, 'Box1', 'Location1', 'Description1');")
    #	fail on subtype
    except sqlite3.Error as e:
        assertIsInstance(e, sqlite3.IntegrityError)
        assertIn("FOREIGN KEY constraint failed", str(e))

    # insert item correct cat, type, subtype
    try:
        db.cur.execute("insert into item (cat, atype, subtype, box, loc, descript) values (1, 1, 1, 'Box1', 'Location1', 'Description1') returning id, cat, atype, subtype;")
        row = db.cur.fetchone()
        assertEqual(row[1], 1)
        assertEqual(row[2], 1)
        assertEqual(row[3], 1)
    except sqlite3.Error as e:
        assertTrue(False)

def test_b_schema_thru_db(db: Database) -> None:
    # Good to go?
    assertIsInstance(db.conn, sqlite3.Connection)

    # insert subtype
    try:
        db.add_subtype("subtype2", 2)
        #	fail on type
    except sqlite3.Error as e:
        assertIsInstance(e, sqlite3.IntegrityError)
        assertIn('FOREIGN KEY constraint failed', str(e))

    # insert type
    try:
        db.add_type("type2", 2)
    #	fail on category
    except sqlite3.Error as e:
        assertIsInstance(e, sqlite3.IntegrityError)
        assertIn('FOREIGN KEY constraint failed', str(e))

    # insert category
    try:
        cat: Category | None = db.add_category("category2")
    #	test for success
        assertIsInstance(cat, Category)
        if cat is not None:
            assertEqual(cat.c_name, "category2")
    except sqlite3.Error as e:
        assertTrue(False)
        #assertIsInstance(e, sqlite3.IntegrityError)
        #assertIn('FOREIGN KEY constraint failed', str(e))

    # insert type
    try:
        atype: Type | None = db.add_type("type2", 2)
    #	test for success
        assertIsInstance(atype, Type)
        if atype is not None:
            assertEqual(atype.t_name, "type2")
    except sqlite3.Error as e:
        assertIsInstance(e, sqlite3.IntegrityError)
        assertIn('FOREIGN KEY constraint failed', str(e))

    # insert subtype
    try:
        asubtype: Subtype | None = db.add_subtype("subtype2", 2)
    #	test for success
        assertIsInstance(asubtype, Subtype)
        if asubtype is not None:	
            assertEqual(asubtype.st_name, "subtype2")
    except sqlite3.Error as e:
        assertIsInstance(e, sqlite3.IntegrityError)
        assertIn('FOREIGN KEY constraint failed', str(e))

    # insert item correct cat, type, subtype
    try:
        item: Item | None = db.add_item(2, 2, 2, 'Box2', 'Location2', 'Description2')
    #	test for success
        assertIsInstance(item, Item)	
    except sqlite3.Error as e:
        assertIsInstance(e, sqlite3.OperationalError)
        assertIn("blah", str(e))

    # insert item wrong cat, type, subtype
    try:
        db.add_item(3, 2, 2, 'Box2', 'Location2', 'Description2')
    #	fail on category
    except sqlite3.Error as e:
        assertIsInstance(e, sqlite3.IntegrityError)
        assertIn("FOREIGN KEY constraint failed", str(e))

    # insert item correct cat, wrong type, subtype
    try:
        db.add_item(2, 3, 2, 'Box2', 'Location2', 'Description2')
        #	fail on type
    except sqlite3.Error as e:
        assertIsInstance(e, sqlite3.IntegrityError)
        assertIn("FOREIGN KEY constraint failed", str(e))

    # insert item correct cat, type, wrong subtype
    try:
        item: Item | None = db.add_item(2, 2, 3, 'Box2', 'Location2', 'Description2')
    #	fail on subtype
    except sqlite3.Error as e:
        assertIsInstance(e, sqlite3.IntegrityError)
        assertIn("FOREIGN KEY constraint failed", str(e))


