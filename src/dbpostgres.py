#import types
from xxlimited import Str

import psycopg2
import cnst
from collections.abc import Callable
#from pydantic.types import AnyType
#import window
from models import Category, Type, Subtype, Item, String


class Database():


    def __init__(self, errHandler: Callable[[str|None, list[str]|None], None], prompter: Callable[[str], None], pgaddress: str, pgport: str) -> None:
        self.errHandler = errHandler
        self.prompter = prompter
        try:
            connstr = "postgresql://postgres:Spl1tL1ckSt1ck@"+pgaddress+":"+pgport+"/Inventory"
            self.conn = psycopg2.connect(connstr)
            self.conn.set_session(autocommit=True)
            self.cur = self.conn.cursor()
        except psycopg2.Error as e:
            self.handleDBError(e)

    def handleDBError(self, e:  psycopg2.Error) -> None:
        if type(e) == psycopg2.Error or type(e) == psycopg2.OperationalError:
            self.errHandler(e.args[0], None)
        else:
            self.errHandler(e.pgerror, None)

    def add_category(self, c_name: str) -> Category | None:
        row = None
        try:
            self.cur.execute('insert into category (c_name) values (%s) returning id, c_name;', (c_name,))
            row = self.cur.fetchone()
        except psycopg2.Error as e:
            self.handleDBError(e)

        if row is None:
            self.prompter('Failed to add category: ' + c_name)
            return None

        cat = Category(id=row[0], c_name=row[1])
        return cat

    def add_item(self, cat_id: int, type_id: int, subtype_id: int, box: str, loc: str, descript: str) -> Item | None:
        row = None
        try:
            self.cur.execute('insert into item (cat, atype, subtype, box, loc, descript) values (%s, %s, %s, %s, %s, %s) returning id, cat, atype, subtype, box, loc, descript;', 
                             (cat_id, type_id, subtype_id, box, loc, descript))
            row = self.cur.fetchone()
        except psycopg2.Error as e:
            self.handleDBError(e)

        if row is None:
            self.prompter('Failed to add item with cat_id: ' + str(cat_id) + ', type_id: ' + str(type_id) + ', subtype_id: ' + str(subtype_id))
            return None 

        itm = Item(id=row[0], cat_id=row[1], cat_str='', type_id=row[2], type_str='',
                   sub_id=row[3], sub_str='', box=row[4], loc=row[5], descript=row[6])
        return itm

    def add_type(self, t_name: str, cat_id: int) -> Type:
        try:
            self.cur.execute('insert into type (t_name, cat) values (%s, %s) returning id, t_name, cat;', (t_name, cat_id))
            row = self.cur.fetchone()
        except psycopg2.Error as e:
            self.handleDBError(e)
        self.prompter('Added type: ' + t_name + ' with id: ' + str(row[0]))
        atype = Type(id=row[0], t_name=row[1], cat_id=row[2])
        return atype


    def add_subtype(self, st_name: str, type_id:int) -> Subtype:
        try:
            self.cur.execute('insert into subtype (st_name, atype) values (%s, %s) returning id, st_name, atype;', (st_name, type_id))
            row = self.cur.fetchone()
        except psycopg2.Error as e:
            self.handleDBError(e)
        self.prompter('Added subtype: ' + st_name + ' with id: ' + str(row[0]))
        asubtype = Subtype(id=row[0], st_name=row[1], atype=row[2])
        return asubtype

    def delete_item(self, item_id: int) -> None:
        try:
            self.cur.execute("delete from item where id = %s", (item_id,))
            # nothing to fetch
        except psycopg2.Error as e:
            self.handleDBError(e)
        return None

    def update_item(self, item_id: int, cat_id: int, type_id: int, subtype_id: int, boxid: str, loc: str, descript: str) -> None:
        try:
            self.cur.execute("update item set (cat, atype, subtype, box, loc, descript) = (%s, %s, %s, %s, %s, %s) where id = %s", 
                        (cat_id, type_id, subtype_id, boxid, loc, descript, item_id)) 
            # nothing to fetch
        except psycopg2.Error as e:
            self.handleDBError(e)
        return None

    def update_item(self, it: Item) -> None:
       try:
            self.cur.execute("update item set (cat, atype, subtype, box, loc, descript) = (%s, %s, %s, %s, %s, %s) where id = %s", 
                        (it.cat_id, it.type_id, it.sub_id, it.box, it.loc, it.descript, it.id)) 
            # nothing to fetch
       except psycopg2.Error as e:
            self.handleDBError(e)
       return None


    def update_cat(self, cat_id: int, new_value: str) -> None:
        try:
            self.cur.execute('update category set c_name = %s where id = %s', (new_value, cat_id))
        except psycopg2.Error as e:
            self.handleDBError(e)
        return None

    def update_type(self, type_id: int, new_value: str) -> None:
        try:
            self.cur.execute('update type set t_name = %s where id = %s', (new_value, type_id))
        except psycopg2.Error as e:
            self.handleDBError(e)
        return None

    def update_subtype(self, subtype_id: int, new_value: str) -> None:
        try:
            self.cur.execute('update subtype set st_name = %s where id = %s', (new_value, subtype_id))
        except psycopg2.Error as e:
            self.handleDBError(e)
        return None

    def check_cat(self, cat_id: int) -> bool:
        irows: list[Item] = self.get_items_by_cat(cat_id)
        trows: list[Type] = self.get_types_for_cat(cat_id)
        t_ids: list[int] = []
        for atype in trows:
            t_ids.append(atype.id)
        strows = self.get_subtypes_for(t_ids)
        if len(irows) > 0 or len(trows) > 0 or len(strows) > 0:
            cat = self.get_cat_for_id(cat_id)
            warnings = ["Before you can delete Category "+repr(cat)+", you need to delete or modify the following:"]
            if len(irows) > 0:
                warnings.append("items:")
                for item in irows:
                    warnings.append(item.str_all())
            if len(trows) > 0:
                warnings.append('Types:')
                for atype in trows:
                    warnings.append(atype.str_all())
            if len(strows) > 0:
                warnings.append("SubTypes:")
                for subtype in strows:
                    warnings.append(subtype.str_all())
            self.errHandler(None, warnings)
            return False
        return True

    def check_type(self, type_id: int) -> bool:
        win = self.win
        irows = self.get_items_by_type(type_id)
        crow = self.get_category_by_type(type_id)
        assert(type(crow) ==  tuple)
        strows = self.get_subtypes_for([type_id])
        warnings = []
        retvalue = True
        atype = self.get_type_for_id(type_id)
        if len(crow) > 0:
            warnings.append(("Type "+repr(atype)+" refers upward to Category "+repr(crow),))
        if len(irows) > 0 or len(strows) > 0:
            warnings.append(("Before you can delete Type "+repr(atype)+", you need to delete or modify the following:",))
            if len(irows) > 0:
                warnings.append(("items:",))
                for row in irows:
                    warnings.append(Item(id=row[0], cat=row[1], atype=row[2],
                               subtype=row[3], box=row[4], loc=row[5], descript=row[6]))
            if len(strows) > 0:
                warnings.append(("SubTypes:",))
                for row in strows:
                    warnings.append(Subtype(id=row[0], type=row[1], st_name=row[2]))
            retvalue = False
        win.select_from_list(warnings, cnst.PRINTALL, 0, "Warnings", win.what_line, False)
        return retvalue
                
    def check_stype(self, stype_id: int) -> bool:
        win = self.win
        irows = self.get_items_by_stype(stype_id)
        stype = self.get_subtype_for_id(stype_id)
        atype = self.get_type_for_id(stype[2])
        cat = self.get_cat_for_id(atype[2])
        assert(type(cat) ==  tuple)
        assert(type(atype) == tuple)
        assert(type(stype) == tuple)
        assert(type(irows) == list)
        if len(irows) > 0:
            warnings = [("The following items refer to SubType "+repr(stype)+":",)]
            for row in irows:
                warnings.append(row)
            warnings.append(("",))
            warnings.append(("They must be deleted or they must reference a diffent subtype",))
            warnings.append(("before SubType "+repr(stype)+" can be deleted.",))
            warnings.append(("",))
            warnings.append(("The parents of SubType "+repr(stype)+" are Type "+repr(atype)+" and Category "+repr(cat)+".",))
            warnings.append(("They will not be affected by deleting or modifing the SubType.",))
            win.select_from_list(warnings, -1, 0, "Warnings", win.what_line, False)
            return False
        return True
                

    def delete_cat(self, cat: Category) -> None:
        if self.check_cat(cat.id):
            try:
                self.cur.execute("delete from category where id = %s", (cat_id,))
                # nothing to fetch
            except psycopg2.Error as e:
                self.handleDBError(e)
        return None

    def delete_type(self, type_id: int) -> None:
        if self.check_type(type_id):
            try:
                self.cur.execute('delete from type where id = %s', (type_id,))
                #nothing to fetch
            except psycopg2.Error as e:
                self.handleDBError(e)
        return None

    def delete_stype(self, stype_id: int) -> None:
        if self.check_stype(stype_id):
            try:
                self.cur.execute('delete from subtype where id = %s', (stype_id,))
                #nothing to fetch
            except psycopg2.Error as e:
                self.handleDBError(e)
        return None

    def get_box_letters(self) -> list[String]:
        try:
            self.cur.execute('SELECT distinct(substring(box,1,1)) FROM public.item ORDER BY 1 ASC;')
            rows = self.cur.fetchall()
        except psycopg2.Error as e:
            self.handleDBError(e)
        letters = []
        for row in rows:
            letters.append(String(id = 0, string=row[0]))
        return letters

    def get_box_numbers(self, letter: str) -> list[String]:
        try:
            self.cur.execute('SELECT distinct(substring(box,2)) FROM public.item where substring(box,1,1) = %s ORDER BY 1 ASC;', (letter,))
            rows = self.cur.fetchall()
        except psycopg2.Error as e:
            self.handleDBError(e)
        numbers = []
        for row in rows:
            numbers.append(String(id = 0, string=row[0])    )
        return numbers

    def get_cat_for_id(self, cat_id: int) -> Category | None:
        try:
            self.cur.execute("select * from category where id = %s", (cat_id,))
            row = self.cur.fetchone()
            cat = Category(id=row[0], c_name=row[1])
            return cat
        except psycopg2.Error as e:
            self.handleDBError(e)
        return None

    def get_category_by_type(self, type_id: int) -> Category | None:
         try:
             self.cur.execute("select * from type where id = %s", (type_id,))
             trow = self.cur.fetchone()
             self.cur.execute("select * from category where id = %s", (trow[2],))
             row = self.cur.fetchone()
             acat = Category(id=row[0], c_name=row[1])
             return acat
         except psycopg2.Error as e:
             self.handleDBError(e)
         return None

    def get_categories(self) -> list[Category]:
        try:
            self.cur.execute('select * from category order by c_name;')
            rows = self.cur.fetchall()
            categories = []
            for row in rows:
                cat = Category(id=row[0], c_name=row[1])
                categories.append(cat)
        except psycopg2.Error as e:
            self.handleDBError(e)
        # if show:
        #     self.win.putstr('id, c_name\n')
        #     for row in rows:
        #         self.win.putstr(str(row[0])+', '+row[1]+'\n')
        return categories

    def get_items(self) -> list[Item]:
        # if show:
        #     self.win.putstr('id, cat, atype, subtype, box, loc, descript\n')
        try:
            self.cur.execute('select item.id, category.id, category.c_name, type.id, type.t_name, subtype.id, subtype.st_name, box, loc, descript from item '
	                            '  join category on item.cat = category.id '
	                            '  join type on item.atype = type.id '
	                            '  join subtype on item.subtype = subtype.id '
                                '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;')
            rows = self.cur.fetchall()
            items = []
            for row in rows:
                itm = Item(id=row[0], cat_id=row[1], cat_str=row[2], type_id=row[3], type_str=row[4],
                        sub_id=row[5], sub_str=row[6], box=row[7], loc=row[8], descript=row[9])
                items.append(itm)
        except psycopg2.Error as e:
            self.handleDBError(e)
        # if show:
        #     for row in rows:
        #         self.win.putstr(str(row[0])+', '+str(row[1])+', '+str(row[2])+', '+str(row[3])+', '+row[4]+', '+row[5]+', '+row[6]+'\n')
        return items

    def get_item_by_id(self, id):
        try:
            self.cur.execute('select item.id, category.id, category.c_name, type.id, type.t_name, subtype.id, subtype.st_name, box, loc, descript from item '
	                            '  join category on item.cat = category.id '
	                            '  join type on item.atype = type.id '
	                            '  join subtype on item.subtype = subtype.id '
                                '  where item.id = %s'
                                '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;', (id,))
            row = self.cur.fetchone()
            item = Item(id=row[0], cat_id=row[1], cat_str=row[2], type_id=row[3], type_str=row[4],
                    sub_id=row[5], sub_str=row[6], box=row[7], loc=row[8], descript=row[9])
            return item
        except psycopg2.Error as e:
            self.handleDBError(e)

    def get_items_by_cat(self, cat: int) -> list[Item]:
        try:
            self.cur.execute('select item.id, category.id, category.c_name, type.id, type.t_name, subtype.id, subtype.st_name, box, loc, descript from item '
	                            '  join category on item.cat = category.id '
	                            '  join type on item.atype = type.id '
	                            '  join subtype on item.subtype = subtype.id '
                                '  where item.cat = %s'
                                '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;', (cat,))
            rows = self.cur.fetchall()
            items = []
            for row in rows:
                itm = Item(id=row[0], cat_id=row[1], cat_str=row[2], type_id=row[3], type_str=row[4],
                           sub_id=row[5], sub_str=row[6], box=row[7], loc=row[8], descript=row[9])
                items.append(itm)
        except psycopg2.Error as e:
            self.handleDBError(e)
        return items

    def get_items_by_type(self, type_id):
        try:
            self.cur.execute('select item.id, category.id, category.c_name, type.id, type.t_name, subtype.id, subtype.st_name, box, loc, descript from item '
	                            '  join category on item.cat = category.id '
	                            '  join type on item.atype = type.id '
	                            '  join subtype on item.subtype = subtype.id '
                                '  where item.atype = %s'
                                '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;', (type_id,))
            rows = self.cur.fetchall()
            items = []
            for row in rows:
                itm = Item(id=row[0], cat_id=row[1], cat_str=row[2], type_id=row[3], type_str=row[4],
                           sub_id=row[5], sub_str=row[6], box=row[7], loc=row[8], descript=row[9])
                items.append(itm)
        except psycopg2.Error as e:
            self.handleDBError(e)
        return items

    def get_items_by_stype(self, stype_id):
        try:
            self.cur.execute('select item.id, category.id, category.c_name, type.id, type.t_name, subtype.id, subtype.st_name, box, loc, descript from item '
	                            '  join category on item.cat = category.id '
	                            '  join type on item.atype = type.id '
	                            '  join subtype on item.subtype = subtype.id '
                                '  where item.subtype = %s'
                                '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;', (stype_id,))
            rows = self.cur.fetchall()
            items = []
            for row in rows:
                itm = Item(id=row[0], cat_id=row[1], cat_str=row[2], type_id=row[3], type_str=row[4],
                           sub_id=row[5], sub_str=row[6], box=row[7], loc=row[8], descript=row[9])
                items.append(itm)
        except psycopg2.Error as e:
            self.handleDBError(e)
        return items

    def get_items_by_cat_type(self, cat, atype):
        try:
            self.cur.execute('select item.id, category.id, category.c_name, type.id, type.t_name, subtype.id, subtype.st_name, box, loc, descript from item '
	                            '  join category on item.cat = category.id '
	                            '  join type on item.atype = type.id '
	                            '  join subtype on item.subtype = subtype.id '
                                '  where item.cat = %s and item.atype = %s'
                                '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;', (cat, atype))
            rows = self.cur.fetchall()
            items = []
            for row in rows:
                itm = Item(id=row[0], cat_id=row[1], cat_str=row[2], type_id=row[3], type_str=row[4],
                           sub_id=row[5], sub_str=row[6], box=row[7], loc=row[8], descript=row[9])
                items.append(itm)
        except psycopg2.Error as e:
            self.handleDBError(e)
        return items

    def get_items_by_cat_type_subtype(self, cat, atype, asubtype):
        try:
            self.cur.execute('select item.id, category.id, category.c_name, type.id, type.t_name, subtype.id, subtype.st_name, box, loc, descript from item '
	                            '  join category on item.cat = category.id '
	                            '  join type on item.atype = type.id '
	                            '  join subtype on item.subtype = subtype.id '
                                '  where item.cat = %s and item.atype = %s and item.subtype = %s'
                                '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;', (cat, atype, asubtype))
            rows = self.cur.fetchall()
            items = []
            for row in rows:
                itm = Item(id=row[0], cat_id=row[1], cat_str=row[2], type_id=row[3], type_str=row[4],
                           sub_id=row[5], sub_str=row[6], box=row[7], loc=row[8], descript=row[9])
                items.append(itm)
        except psycopg2.Error as e:
            self.handleDBError(e)
        return items

    def get_joined_items(self, show=False):
        if show:
            self.win.putstr('id, cat, atype, subtype, box, loc, descript\n')
        try:
                self.cur.execute('select item.id, category.c_name, type.t_name, subtype.st_name, box, loc, descript from item '
	                             '  join category on item.cat = category.id '
	                             '  join type on item.atype = type.id '
	                             '  join subtype on item.subtype = subtype.id '
                                 '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;')
                rows = self.cur.fetchall()
        except psycopg2.Error as e:
            self.handleDBError(e)
        if show:
            for row in rows:
                self.win.putstr(str(row[0])+', '+str(row[1])+', '+str(row[2])+', '+str(row[3])+', '+row[4]+', '+row[5]+', '+row[6]+'\n')
        return rows

    def get_locations(self, show=False):
        if show:
            self.win.putstr('boxid')
        try:
            self.cur.execute('select distinct(loc) from item order by loc;')
            rows = self.cur.fetchall()
        except psycopg2.Error as e:
            self.handleDBError(e)
        locs = []
        for row in rows:
            locs.append(String(string=row[0]))
            if show:
                self.win.putstr(str(row[0])+'\n')

        return locs

    def get_subtypes(self, show=False):
        try:
            self.cur.execute('select * from subtype order by st_name;')
            rows = self.cur.fetchall()
            stypes =[]
            for row in rows:
                stype = Subtype(id=row[0], st_name=row[1], atype=row[2])
                stypes.append(stype)
        except psycopg2.Error as e:
            self.handleDBError(e)
        if show:
            for stype in stypes:
                self.win.putstr(stype.str_all()+'\n')
        return stypes

    def get_subtypes_for(self, type_ids : list[int]) -> list[Subtype]:
        stypes: list[Subtype] = []
        try:
            #if type(type_ids) == int:
                #type_ids = [type_ids]
            #    self.cur.execute('select * from subtype where atype = %s order by st_name;', (type_ids,))
            if len(type_ids) == 0:
                return stypes
            else:
                sqlstr = self.cur.mogrify('select * from subtype where atype in %s order by atype;', (type_ids,))
                self.cur.execute(sqlstr)

            rows = self.cur.fetchall()
            for row in rows:
                stypes.append(Subtype(id=row[0],st_name=row[1],atype=row[2]))
        except psycopg2.Error as e:
            self.handleDBError(e)
        return stypes
    
    def get_subtype_for_id(self, stype_id):
        assert(type(stype_id) == int)
        try:
            self.cur.execute("select * from subtype where id = %s", (stype_id,))
            return self.cur.fetchone()
        except psycopg2.Error as e:
            self.handleDBError(e)

    def get_types(self, show=False):
        #self.win.putstr('id, t_name, cat\n')
        try:
                self.cur.execute('select * from type order by t_name;')
                rows = self.cur.fetchall()
                types = []
                for row in rows:
                    atype = Type(id=row[0], t_name=row[1], cat_id=row[2])
                    types.append(atype)
        except psycopg2.Error as e:
            self.handleDBError(e)
        if show:
            for atype in types:
                self.win.putstr(atype.str_all()+'\n')
        return types

    def get_types_for_cat(self, cat_id: int) -> list[Type]:
        try:
            self.cur.execute('select * from type where cat = %s order by t_name;', (cat_id,))
            rows = self.cur.fetchall()
            types = []
            for row in rows:
                atype = Type(id=row[0], t_name=row[1], cat_id=row[2])
                types.append(atype)
        except psycopg2.Error as e:
            self.handleDBError(e)
        return types

    def get_type_for_id(self, type_id):
        try:
            self.cur.execute('select * from type where id = %s;', (type_id,))
            rows = self.cur.fetchone()
        except psycopg2.Error as e:
            self.handleDBError(e)
        return rows



# cur.execute("insert into category (c_name) values (%s)", ("testcat",))
# cur.execute("select max(id) from category;")
# row = cur.fetchone()
# newcat = row[0]
# print(row)
# print()
# cur.execute("insert into type (t_name, cat) values (%s, %s)", ("testtype", newcat))
# cur.execute("select max(id) from type;")
# row = cur.fetchone()
# newtype = row[0]
# print(row)
# print()
# cur.execute("insert into subtype (st_name, atype) values (%s, %s)", ("testsub", newtype))
# cur.execute("select max(id) from subtype;")
# row = cur.fetchone()
# newsubtype = row[0]
# print(row)
# print()
# cur.execute("insert into item (cat, atype, subtype, box, loc, descript) values (%s, %s, %s, %s, %s, %s)", (newcat, newtype, newsubtype, "B1", "closet", "a silly test item"))
# cur.execute("select * from item;")

# row = cur.fetchone()
# print(row)
print()