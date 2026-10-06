import sqlite3
from collections.abc import Callable
from inventory.src.models import Category, Type, Subtype, Item, String


class Database():


    def __init__(self, errHandler: Callable[[str|None, list[str]|None], None], prompter: Callable[[str], None], dbname: str) -> None:
        self.errHandler = errHandler
        self.prompter = prompter
        try:
            self.conn = sqlite3.connect(dbname, autocommit=True)
            self.conn.execute("PRAGMA foreign_keys = ON;")
            self.cur = self.conn.cursor()
            self.ifDBNewBuild()
        except sqlite3.Error as e:
            self.handleDBError(e)

    def ifDBNewBuild(self) -> None:
        try:
            self.cur.execute("select * from category;")
        except sqlite3.Error as e:
            self.prompter("Database not found, creating new database..."+e.sqlite_errorname+" ("+str(e.sqlite_errorcode)+")")
            self.buildDB()

    def buildDB(self) -> None:
        try:
            self.cur.execute('create table category (id integer primary key, c_name varchar(50) not null unique);')
            self.cur.execute('create table type (id integer primary key, t_name varchar(50) not null , cat int references category(id));')
            self.cur.execute('create table subtype (id integer primary key, st_name varchar(50) not null , atype int references type(id));')
            self.cur.execute('create table item (id integer primary key, cat int references category(id), atype int references type(id), subtype int references subtype(id), box varchar(10), loc varchar(50), descript varchar(200));')
        except sqlite3.Error as e:
            self.handleDBError(e)
            
    def handleDBError(self, e: sqlite3.Error) -> None:
        code = getattr(e, "sqlite_errorcode", None)
        name = getattr(e, "sqlite_errorname", None)
        message = f"{name} ({code}): {e}" if name is not None else str(e)
        self.errHandler(message, None)


    def add_category(self, c_name: str) -> Category | None:
        row = None
        cat: Category | None = None 
        try:
            self.cur.execute('insert into category (c_name) values (?) returning id, c_name;', (c_name,))
            row = self.cur.fetchone()
            if row is None:
                self.prompter('Failed to add category: ' + c_name)
                return None
            cat = Category(id=row[0], c_name=row[1])
        except sqlite3.Error as e:
            self.handleDBError(e)

        return cat

    def add_item(self, cat_id: int, type_id: int, subtype_id: int, box: str, loc: str, descript: str) -> Item | None:
        row = None
        try:
            self.cur.execute('insert into item (cat, atype, subtype, box, loc, descript) values (?, ?, ?, ?, ?, ?) returning id, cat, atype, subtype, box, loc, descript;', 
                             (cat_id, type_id, subtype_id, box, loc, descript))
            row = self.cur.fetchone()
        except sqlite3.Error as e:
            self.handleDBError(e)

        if row is None:
            self.prompter('Failed to add item with cat_id: ' + str(cat_id) + ', type_id: ' + str(type_id) + ', subtype_id: ' + str(subtype_id))
            return None 

        cat = self.get_cat_for_id(cat_id)
        type = self.get_type_for_id(type_id)
        subtype = self.get_subtype_for_id(subtype_id)
        itm = Item(id=row[0], cat_id=row[1], cat_str=cat.c_name if cat else '', type_id=row[2], type_str=type.t_name if type else '',
                   sub_id=row[3], sub_str=subtype.st_name if subtype else '', box=row[4], loc=row[5], descript=row[6])
        return itm

    def add_type(self, t_name: str, cat_id: int) -> Type | None:
        atype: Type | None = None
        try:
            self.cur.execute('insert into type (t_name, cat) values (?, ?) returning id, t_name, cat;', (t_name, cat_id))
            row = self.cur.fetchone()
            atype = Type(id=row[0], t_name=row[1], cat_id=row[2])
            self.prompter('Added type: ' + t_name + ' with id: ' + str(row[0]))
        except sqlite3.Error as e:
            self.handleDBError(e)
        return atype

    
    def add_subtype(self, st_name: str, type_id:int) -> Subtype | None:
        asubtype: Subtype | None = None
        try:
            self.cur.execute('insert into subtype (st_name, atype) values (?, ?) returning id, st_name, atype;', (st_name, type_id))
            row = self.cur.fetchone()
            self.prompter('Added subtype: ' + st_name + ' with id: ' + str(row[0]))
            asubtype = Subtype(id=row[0], st_name=row[1], atype=row[2])
        except sqlite3.Error as e:
            self.handleDBError(e)
        return asubtype

    def delete_item(self, item_id: int) -> bool:
        try:
            self.cur.execute("delete from item where id = ?", (item_id,))
            return True
        except sqlite3.Error as e:
            self.handleDBError(e)
        return False

    # def update_item(self, item_id: int, cat_id: int, type_id: int, subtype_id: int, boxid: str, loc: str, descript: str) -> None:
    #     try:
    #         self.cur.execute("update item set (cat, atype, subtype, box, loc, descript) = (?, ?, ?, ?, ?, ?) where rowid = ?", 
    #                     (cat_id, type_id, subtype_id, boxid, loc, descript, item_id)) 
    #         # nothing to fetch
    #     except sqlite3.Error as e:
    #         self.handleDBError(e)
    #     return None

    def update_item(self, it: Item) -> bool:
        try:
            self.cur.execute("update item set (cat, atype, subtype, box, loc, descript) = (?, ?, ?, ?, ?, ?) where id = ?", 
                        (it.cat_id, it.type_id, it.sub_id, it.box, it.loc, it.descript, it.id)) 
            return True
        except sqlite3.Error as e:
            self.handleDBError(e)
        return False


    def update_cat(self, cat_id: int, new_value: str) -> bool:
        try:
            self.cur.execute('update category set c_name = ? where id = ?', (new_value, cat_id))
            return True
        except sqlite3.Error as e:
            self.handleDBError(e)
        return False

    def update_type(self, type_id: int, new_value: str) -> bool:
        try:
            self.cur.execute('update type set t_name = ? where id = ?', (new_value, type_id))
            return True
        except sqlite3.Error as e:
            self.handleDBError(e)
        return False

    def update_subtype(self, subtype_id: int, new_value: str) -> bool:
        try:
            self.cur.execute('update subtype set st_name = ? where id = ?', (new_value, subtype_id))
            return True
        except sqlite3.Error as e:
            self.handleDBError(e)
        return False

    def cat_exists(self, cat_id: int) -> bool:
        self.cur.execute("select * from category where id = ?", (cat_id,))
        row = self.cur.fetchone()
        return row is not None

    def cat_ok_to_delete(self, cat_id: int) -> bool:
        items: list[Item] = self.get_items_by_cat(cat_id)
        types: list[Type] = self.get_types_for_cat(cat_id)
        t_ids: list[int] = []
        for atype in types:
            t_ids.append(atype.id)
        stypes = self.get_subtypes_for_types(t_ids)
        if len(items) > 0 or len(types) > 0 or len(stypes) > 0:
            cat = self.get_cat_for_id(cat_id)
            warnings = ["Before you can delete Category "+cat.str_all()+", you need to delete or modify the following:"]
            if len(items) > 0:
                warnings.append("items:")
                for item in items:
                    warnings.append(item.str_all())
            if len(types) > 0:
                warnings.append('Types:')
                for atype in types:
                    warnings.append(atype.str_all())
            if len(stypes) > 0:
                warnings.append("SubTypes:")
                for subtype in stypes:
                    warnings.append(subtype.str_all())
            self.errHandler(None, warnings)
            return False
        return True

    def type_exists(self, type_id: int) -> bool:
        self.cur.execute("select * from type where id = ?", (type_id,))
        row = self.cur.fetchone()
        return row is not None

    def type_ok_to_delete(self, type_id: int) -> bool:
        items = self.get_items_by_type(type_id)
        cat = self.get_category_by_type(type_id)
        stypes = self.get_subtypes_for_types([type_id])
        warnings: list[str] = []
        retvalue = True
        atype = self.get_type_for_id(type_id)
        if cat:
            warnings.append("Type "+atype.str_all()+" refers upward to Category "+cat.str_all())
        if len(items) > 0 or len(stypes) > 0:
            warnings.append("Before you can delete Type " + atype.str_all() + ", you need to delete or modify the following:")
            if len(items) > 0:
                warnings.append("items:")
                for item in items:
                    warnings.append(item.str_all())
            if len(stypes) > 0:
                warnings.append("SubTypes:",)
                for stype in stypes:
                    warnings.append(stype.str_all())
            retvalue = False
        self.errHandler(None, warnings)
        return retvalue
    
    def stype_exists(self, stype_id: int) -> bool:
        self.cur.execute("select * from subtype where id = ?", (stype_id,))
        row = self.cur.fetchone()
        return row is not None
         
    def stype_ok_to_delete(self, stype_id: int) -> bool:
        warnings: list[str] = []

        # does subtype exist?
        stype = self.get_subtype_for_id(stype_id)

        if stype is None:
            warnings.append("SubType with id "+str(stype_id)+" does not exist. Cannot delete.")
            self.errHandler("NORAISE", warnings)
            return False
        
        items = self.get_items_by_stype(stype_id)
        atype = self.get_type_for_id(stype.atype)
        cat = self.get_cat_for_id(atype.cat_id)

        if len(items) > 0:
            warnings: list[str] = ["The following items refer to SubType "+stype.str_all()+":"]
            for item in items:
                warnings.append(item.str_all())
            
            warnings.append("")
            warnings.append("They must be deleted or they must reference a different subtype")
            warnings.append("before SubType "+stype.str_all()+" can be deleted.")

            warnings.append("")
            warnings.append("The parents of SubType "+stype.str_all()+" are Type "+repr(atype)+" and Category "+cat.str_all()+".")
            warnings.append("They will not be affected by deleting or modifing the SubType.")
            self.errHandler("NORAISE", warnings)
            return False
        return True
                

    def delete_cat(self, cat_id: int) -> bool:
        if self.cat_ok_to_delete(cat_id):
            try:
                self.cur.execute("delete from category where id = ?", (cat_id,))
                # nothing to fetch
                return True
            except sqlite3.Error as e:
                self.handleDBError(e)
        return False

    def delete_type(self, type_id: int) -> bool:
        if self.type_ok_to_delete(type_id):
            try:
                self.cur.execute('delete from type where id = ?', (type_id,))
                #nothing to fetch
                return True
            except sqlite3.Error as e:
                self.handleDBError(e)
        return False

    def delete_stype(self, stype_id: int) -> bool:
        if self.stype_ok_to_delete(stype_id):
            try:
                self.cur.execute('delete from subtype where id = ?', (stype_id,))
                return True
            except sqlite3.Error as e:
                self.handleDBError(e)
        return False

    def get_box_letters(self) -> list[String]:
        letters: list[String] = []
        try:
            self.cur.execute('SELECT distinct(substring(box,1,1)) FROM item ORDER BY 1 ASC;')
            rows = self.cur.fetchall()
            for row in rows:
                letters.append(String(id = 0, string=row[0]))
        except sqlite3.Error as e:
            self.handleDBError(e)

        return letters

    def get_box_numbers(self, letter: str) -> list[String]:
        numbers: list[String] = []
        try:
            self.cur.execute('SELECT distinct(substring(box,2)) FROM item where substring(box,1,1) = ? ORDER BY 1 ASC;', (letter,))
            rows = self.cur.fetchall()
            for row in rows:
                numbers.append(String(id = 0, string=row[0]))
        except sqlite3.Error as e:
            self.handleDBError(e)
   
        return numbers

    def get_cat_for_id(self, cat_id: int) -> Category:           #TODO: Unify all get_XXXX that return a single object to return None if not found, instead of raising an exception
        try:
            self.cur.execute("select id, c_name from category where id = ?", (cat_id,))
            row = self.cur.fetchone()
            cat = Category(id=row[0], c_name=row[1])
            return cat
        except sqlite3.Error as e:
            return Category(id=-1, c_name="Missing category for cat_id "+str(cat_id)+": "+str(e)) 

    def get_category_by_type(self, type_id: int) -> Category:
         try:
             self.cur.execute("select id, t_name, cat from type where id = ?", (type_id,))
             trow = self.cur.fetchone()
             self.cur.execute("select id, c_name from category where id = ?", (trow[2],))
             row = self.cur.fetchone()
             acat = Category(id=row[0], c_name=row[1])
             return acat
         except sqlite3.Error as e:
             return Category(id=-1, c_name="Missing category for type_id "+str(type_id)+": "+str(e))

    def get_categories(self) -> list[Category]:
        categories: list[Category] = []
        try:
            self.cur.execute('select id, c_name from category order by c_name;')
            rows = self.cur.fetchall()
            for row in rows:
                cat = Category(id=row[0], c_name=row[1])
                categories.append(cat)
        except sqlite3.Error as e:
            self.handleDBError(e)
        return categories

    def get_items(self) -> list[Item]:
        items: list[Item] = []
        try:
            self.cur.execute('select item.id, category.id, category.c_name, type.id, type.t_name, subtype.id, subtype.st_name, box, loc, descript from item '
	                            '  join category on item.cat = category.id '
	                            '  join type on item.atype = type.id '
	                            '  join subtype on item.subtype = subtype.id '
                                '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;')
            rows = self.cur.fetchall()

            for row in rows:
                itm = Item(id=row[0], cat_id=row[1], cat_str=row[2], type_id=row[3], type_str=row[4],
                        sub_id=row[5], sub_str=row[6], box=row[7], loc=row[8], descript=row[9])
                items.append(itm)
        except sqlite3.Error as e:
            self.handleDBError(e)
        # if show:
        #     for row in rows:
        #         self.win.putstr(str(row[0])+', '+str(row[1])+', '+str(row[2])+', '+str(row[3])+', '+row[4]+', '+row[5]+', '+row[6]+'\n')
        return items

    def get_item_by_id(self, id: int) -> Item | None:
        item: Item | None = None
        try:
            self.cur.execute('select item.id, category.id, category.c_name, type.id, type.t_name, subtype.id, subtype.st_name, box, loc, descript from item '
	                            '  join category on item.cat = category.id '
	                            '  join type on item.atype = type.id '
	                            '  join subtype on item.subtype = subtype.id '
                                '  where item.id = ?'
                                '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;', (id,))
            row = self.cur.fetchone()
            if row:
                item = Item(id=row[0], cat_id=row[1], cat_str=row[2], type_id=row[3], type_str=row[4],
                    sub_id=row[5], sub_str=row[6], box=row[7], loc=row[8], descript=row[9])
            return item
        except  sqlite3.Error as e:
            self.handleDBError(e)

    def get_items_by_cat(self, cat_id: int) -> list[Item]:
        items: list[Item] = []
        try:
            self.cur.execute('select item.id, category.id, category.c_name, type.id, type.t_name, subtype.id, subtype.st_name, box, loc, descript from item '
	                            '  join category on item.cat = category.id '
	                            '  join type on item.atype = type.id '
	                            '  join subtype on item.subtype = subtype.id '
                                '  where item.cat = ?'
                                '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;', (cat_id,))
            rows = self.cur.fetchall()

            for row in rows:
                itm = Item(id=row[0], cat_id=row[1], cat_str=row[2], type_id=row[3], type_str=row[4],
                           sub_id=row[5], sub_str=row[6], box=row[7], loc=row[8], descript=row[9])
                items.append(itm)
        except sqlite3.Error as e:
            self.handleDBError(e)
        return items

    def get_items_by_type(self, type_id: int) -> list[Item]:
        items: list[Item] = []
        try:
            self.cur.execute('select item.id, category.id, category.c_name, type.id, type.t_name, subtype.id, subtype.st_name, box, loc, descript from item '
	                            '  join category on item.cat = category.id '
	                            '  join type on item.atype = type.id '
	                            '  join subtype on item.subtype = subtype.id '
                                '  where item.atype = ?'
                                '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;', (type_id,))
            rows = self.cur.fetchall()
            for row in rows:
                itm = Item(id=row[0], cat_id=row[1], cat_str=row[2], type_id=row[3], type_str=row[4],
                           sub_id=row[5], sub_str=row[6], box=row[7], loc=row[8], descript=row[9])
                items.append(itm)
        except sqlite3.Error as e:
            self.handleDBError(e)
        return items

    def get_items_by_stype(self, stype_id: int) -> list[Item]:
        items: list[Item] = []
        try:
            self.cur.execute('select item.id, category.id, category.c_name, type.id, type.t_name, subtype.id, subtype.st_name, box, loc, descript from item '
	                            '  join category on item.cat = category.id '
	                            '  join type on item.atype = type.id '
	                            '  join subtype on item.subtype = subtype.id '
                                '  where item.subtype = ?'
                                '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;', (stype_id,))
            rows = self.cur.fetchall()
            for row in rows:
                itm = Item(id=row[0], cat_id=row[1], cat_str=row[2], type_id=row[3], type_str=row[4],
                           sub_id=row[5], sub_str=row[6], box=row[7], loc=row[8], descript=row[9])
                items.append(itm)
        except sqlite3.Error as e:
            self.handleDBError(e)
        return items

    def get_items_by_cat_type(self, cat_id: int, type_id: int) -> list[Item]:
        items: list[Item] = []
        try:
            self.cur.execute('select item.id, category.id, category.c_name, type.id, type.t_name, subtype.id, subtype.st_name, box, loc, descript from item '
	                            '  join category on item.cat = category.id '
	                            '  join type on item.atype = type.id '
	                            '  join subtype on item.subtype = subtype.id '
                                '  where item.cat = ? and item.atype = ?'
                                '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;', (cat_id, type_id))
            rows = self.cur.fetchall()
            for row in rows:
                itm = Item(id=row[0], cat_id=row[1], cat_str=row[2], type_id=row[3], type_str=row[4],
                           sub_id=row[5], sub_str=row[6], box=row[7], loc=row[8], descript=row[9])
                items.append(itm)
        except sqlite3.Error as e:
            self.handleDBError(e)
        return items

    def get_items_by_cat_type_subtype(self, cat_id: int, type_id: int, subtype_id: int) -> list[Item]:
        items: list[Item] = []
        try:
            self.cur.execute('select item.id, category.id, category.c_name, type.id, type.t_name, subtype.id, subtype.st_name, box, loc, descript from item '
	                            '  join category on item.cat = category.id '
	                            '  join type on item.atype = type.id '
	                            '  join subtype on item.subtype = subtype.id '
                                '  where item.cat = ? and item.atype = ? and item.subtype = ?'
                                '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;', (cat_id, type_id, subtype_id))
            rows = self.cur.fetchall()
            items = []
            for row in rows:
                itm = Item(id=row[0], cat_id=row[1], cat_str=row[2], type_id=row[3], type_str=row[4],
                           sub_id=row[5], sub_str=row[6], box=row[7], loc=row[8], descript=row[9])
                items.append(itm)
        except sqlite3.Error as e:
            self.handleDBError(e)
        return items

    def get_joined_items(self) -> list[String]:
        items: list[String] = []
        try:
            self.cur.execute('select item.id, category.c_name, type.t_name, subtype.st_name, box, loc, descript from item '
	                            '  join category on item.cat = category.id '
	                            '  join type on item.atype = type.id '
	                            '  join subtype on item.subtype = subtype.id '
                                '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;')
            rows = self.cur.fetchall()
            for row in rows:
                items.append(String(id = row[0], string = str(row[0])+","+",".join(row[1:])))
        except sqlite3.Error as e:
            self.handleDBError(e)
        return items

    def get_locations(self) -> list[String]:
        locs: list[String] = []
        try:
            self.cur.execute('select distinct(loc) from item order by loc;')
            rows = self.cur.fetchall()
            for row in rows:
                locs.append(String(string=row[0]))
        except sqlite3.Error as e:
            self.handleDBError(e)

        return locs

    def get_subtypes(self) -> list[Subtype]:
        stypes: list[Subtype] = []
        try:
            self.cur.execute('select id, st_name, atype from subtype order by st_name;')
            rows = self.cur.fetchall()
            for row in rows:
                stype = Subtype(id=row[0], st_name=row[1], atype=row[2])
                stypes.append(stype)
        except sqlite3.Error as e:
            self.handleDBError(e)

        return stypes

    def get_subtypes_for_types(self, type_ids : list[int]) -> list[Subtype]:
        stypes: list[Subtype] = []
        try:
            if len(type_ids) == 0:
                return stypes
            else:
                placeholders = ",".join("?" for _ in type_ids)
                sql = f"select id, st_name, atype from subtype where atype in ({placeholders}) order by atype"
                self.cur.execute(sql, type_ids)

            rows = self.cur.fetchall()
            for row in rows:
                stypes.append(Subtype(id=row[0],st_name=row[1],atype=row[2]))
        except sqlite3.Error as e:
            self.handleDBError(e)
        return stypes
    
    def get_subtype_for_id(self, stype_id: int) -> Subtype | None:
        try:
            self.cur.execute("select id, st_name, atype from subtype where id = ?", (stype_id,))
            row = self.cur.fetchone()
            if row:
                return Subtype(id=row[0], st_name=row[1], atype=row[2])
        except sqlite3.Error as e:
            self.handleDBError(e)
        return None

    def get_types(self) -> list[Type]:
        types: list[Type] = []
        try:
            self.cur.execute('select id, t_name, cat from type order by t_name;')
            rows = self.cur.fetchall()
            for row in rows:
                atype = Type(id=row[0], t_name=row[1], cat_id=row[2])
                types.append(atype)
        except sqlite3.Error as e:
            self.handleDBError(e)

        return types

    def get_types_for_cat(self, cat_id: int) -> list[Type]:
        types: list[Type] = []
        try:
            self.cur.execute('select id, t_name, cat from type where cat = ? order by t_name;', (cat_id,))
            rows = self.cur.fetchall()
            for row in rows:
                atype = Type(id=row[0], t_name=row[1], cat_id=row[2])
                types.append(atype)
        except sqlite3.Error as e:
            self.handleDBError(e)
        return types

    def get_type_for_id(self, type_id: int) -> Type:
        try:
            self.cur.execute('select id, t_name, cat from type where id = ?;', (type_id,))
            row = self.cur.fetchone()
            if row:
                return Type(id=row[0], t_name=row[1], cat_id=row[2])
        except sqlite3.Error as e:
            self.handleDBError(e)
        raise ValueError("Type not found")


# cur.execute("insert into category (c_name) values (?)", ("testcat",))
# cur.execute("select max(id) from category;")
# row = cur.fetchone()
# newcat = row[0]
# print(row)
# print()
# cur.execute("insert into type (t_name, cat) values (?, ?)", ("testtype", newcat))
# cur.execute("select max(id) from type;")
# row = cur.fetchone()
# newtype = row[0]
# print(row)
# print()
# cur.execute("insert into subtype (st_name, atype) values (?, ?)", ("testsub", newtype))
# cur.execute("select max(id) from subtype;")
# row = cur.fetchone()
# newsubtype = row[0]
# print(row)
# print()
# cur.execute("insert into item (cat, atype, subtype, box, loc, descript) values (?, ?, ?, ?, ?, ?)", (newcat, newtype, newsubtype, "B1", "closet", "a silly test item"))
# cur.execute("select * from item;")

# row = cur.fetchone()
# print(row)
# print()