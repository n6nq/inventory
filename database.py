import psycopg2
import cnst
import window

class Database():
    
    def __init__(self, awin):
        self.win = awin
        try:
            self.conn = psycopg2.connect("dbname=Inventory user=postgres password=Spl1tL1ckSt1ck")
            self.conn.set_session(autocommit=True)
            self.cur = self.conn.cursor()
        except psycopg2.Error as e:
            self.handleDBError(e)

    def handleDBError(self, e):
        win = self.win
        i = win.what_line
        win.restart()
        #win.clrtoend(i, 1)
        if type(e) == psycopg2.ProgrammingError:
            win.str_at(1,1, e.args[0])
        else:
            win.str_at(i, 1, e.pgerror)
        win.prompt('Press any key to continue...')
        win.getch(cnst.ANY)
        win.restart()

        # self.cur.execute(
        #     "select category.c_name, type.t_name, subtype.st_name, item.box, item.loc, item.descript " 
        #     "from item "
        #     "inner join category on item.cat = category.id "
        #     "inner join type     on item.atype = type.id "
        #     "inner join subtype  on item.subtype = subtype.id;")
        # for row in self.cur.fetchall():
        #     self.win.putstr(repr(row) + '\n')
        
        # show = True
        # self.get_categories(show)
        # self.get_types(show)
        # self.get_subtypes(show)
        # self.get_items(show)
        # if show:
        #     self.win.putstr('Press any key...')
        #     self.win.getch(cnst.ANY)

    def add_category(self, c_name):
        try:
            self.cur.execute('insert into category (c_name) values (%s) returning id, c_name;', (c_name,))
            row = self.cur.fetchone()
        except psycopg2.Error as e:
            self.handleDBError(e)
        self.win.str_at(self.win.prompt_line,1,'Added category: ' + c_name + ' with id: ' + str(row[0]))
        return row

    def add_item(self, cat_id, type_id, subtype_id, box, loc, descript):
        try:
            self.cur.execute('insert into item (cat, atype, subtype, box, loc, descript) values (%s, %s, %s, %s, %s, %s) returning id, cat, atype, subtype, box, loc, descript;', 
                             (cat_id, type_id, subtype_id, box, loc, descript))
            row = self.cur.fetchone()
        except psycopg2.Error as e:
            self.handleDBError(e)
        sself.win.str_at(self.win.prompt_line,1,'Added item with id: ' + str(row[0]))
        return row

    def add_type(self, t_name, cat_id):
        try:
            self.cur.execute('insert into type (t_name, cat) values (%s, %s) returning id, t_name, cat;', (t_name, cat_id))
            row = self.cur.fetchone()
        except psycopg2.Error as e:
            self.handleDBError(e)
        self.win.str_at(self.win.prompt_line-1,1,'Added type: ' + t_name + ' with id: ' + str(row[0]))
        return row

    def add_subtype(self, st_name, type_id):
        try:
            self.cur.execute('insert into subtype (st_name, atype) values (%s, %s) returning id, st_name, atype;', (st_name, type_id))
            row = self.cur.fetchone()
        except psycopg2.Error as e:
            self.handleDBError(e)
        self.win.str_at(self.win.prompt_line,1,'Added subtype: ' + st_name + ' with id: ' + str(row[0]))
        return row

    def delete_item(self, item_id):
        try:
            self.cur.execute("delete from item where id = %s", (item_id,))
            # nothing to fetch
        except psycopg2.Error as e:
            self.handleDBError(e)
        return None

    def update_item(self, item_id, cat_id, type_id, subtype_id, boxid, loc, descript):
        try:
            self.cur.execute("update item set (cat, atype, subtype, box, loc, descript) = (%s, %s, %s, %s, %s, %s) where id = %s", 
            (cat_id, type_id, subtype_id, boxid, loc, descript, item_id)) 
            # nothing to fetch
        except psycopg2.Error as e:
            self.handleDBError(e)
        return None

    def update_cat(self, cat_id, new_value):
        try:
            self.cur.execute('update category set c_name = %s where id = %s', (new_value, cat_id))
        except psycopg2.Error as e:
            self.handleDBError(e)
        return None

    def update_type(self, type_id, new_value):
        try:
            self.cur.execute('update type set t_name = %s where id = %s', (new_value, type_id))
        except psycopg2.Error as e:
            self.handleDBError(e)
        return None

    def update_subtype(self, subtype_id, new_value):
        try:
            self.cur.execute('update subtype set st_name = %s where id = %s', (new_value, subtype_id))
        except psycopg2.Error as e:
            self.handleDBError(e)
        return None

    def check_cat(self, cat_id):
        win = self.win
        irows = self.get_items_by_cat(cat_id)
        trows = self.get_types_for_cat(cat_id)
        t_ids = []
        for row in trows:
            t_ids.append(row[0])
        strows = self.get_subtypes_for(tuple(t_ids))
        if len(irows) > 0 or len(trows) > 0 or len(strows) > 0:
            cat = self.get_cat_for_id(cat_id)
            warnings = [("Before you can delete Category "+repr(cat)+", you need to delete or modify the following:",)]
            if len(irows) > 0:
                warnings.append(("items:",))
                for row in irows:
                    warnings.append(row)
            if len(trows) > 0:
                warnings.append(('Types:',))
                for row in trows:
                    warnings.append(row)
            if len(strows) > 0:
                warnings.append(("SubTypes:",))
                for row in strows:
                    warnings.append(row)
            win.select_from_list(warnings, -1, 0, "Warnings", win.what_line, False)
            return False
        return True

    def check_type(self, type_id):
        win = self.win
        irows = self.get_items_by_type(type_id)
        crow = self.get_category_by_type(type_id)
        assert(type(crow) ==  tuple)
        strows = self.get_subtypes_for(type_id)
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
                    warnings.append(row)
            if len(strows) > 0:
                warnings.append(("SubTypes:",))
                for row in strows:
                    warnings.append(row)
            retvalue = False
        win.select_from_list(warnings, -1, 0, "Warnings", win.what_line, False)
        return retvalue
                
    def check_stype(self, stype_id):
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
                

    def delete_cat(self, cat_id):
        if self.check_cat(cat_id):
            try:
                self.cur.execute("delete from category where id = %s", (cat_id,))
                # nothing to fetch
            except psycopg2.Error as e:
                self.handleDBError(e)
        return None

    def delete_type(self, type_id):
        if self.check_type(type_id):
            try:
                self.cur.execute('delete from type where id = %s', (type_id,))
                #nothing to fetch
            except psycopg2.Error as e:
                self.handleDBError(e)
        return None

    def delete_stype(self, stype_id):
        if self.check_stype(stype_id):
            try:
                self.cur.execute('delete from subtype where id = %s', (stype_id,))
                #nothing to fetch
            except psycopg2.Error as e:
                self.handleDBError(e)
        return None

    def get_box_letters(self):
        try:
            self.cur.execute('SELECT distinct(substring(box,1,1)) FROM public.item ORDER BY 1 ASC;')
            rows = self.cur.fetchall()
        except psycopg2.Error as e:
            self.handleDBError(e)
        return rows

    def get_box_numbers(self, letter):
        try:
            self.cur.execute('SELECT distinct(substring(box,2)) FROM public.item where substring(box,1,1) = %s ORDER BY 1 ASC;', (letter,))
            rows = self.cur.fetchall()
        except psycopg2.Error as e:
            self.handleDBError(e)
        return rows

    def get_cat_for_id(self,cat_id):
        try:
            self.cur.execute("select * from category where id = %s", (cat_id,))
            row = self.cur.fetchone()
            return row
        except psycopg2.Error as e:
            self.handleDBError(e)
        return None

    def get_category_by_type(self, type_id):
         try:
             self.cur.execute("select * from type where id = %s", (type_id,))
             trow = self.cur.fetchone()
             self.cur.execute("select * from category where id = %s", (trow[2],))
             row = self.cur.fetchone()
             return row
         except psycopg2.Error as e:
             self.handleDBError(e)
         return None

    def get_categories(self, show=False):
        try:
                self.cur.execute('select * from category order by c_name;')
                rows = self.cur.fetchall()
        except psycopg2.Error as e:
            self.handleDBError(e)
        if show:
            self.win.putstr('id, c_name\n')
            for row in rows:
                self.win.putstr(str(row[0])+', '+row[1]+'\n')
        return rows

    def get_items(self, show=False):
        if show:
            self.win.putstr('id, cat, atype, subtype, box, loc, descript\n')
        try:
                self.cur.execute('select * from item order by cat asc;')
                rows = self.cur.fetchall()
        except psycopg2.Error as e:
            self.handleDBError(e)
        if show:
            for row in rows:
                self.win.putstr(str(row[0])+', '+str(row[1])+', '+str(row[2])+', '+str(row[3])+', '+row[4]+', '+row[5]+', '+row[6]+'\n')
        return rows

    def get_plain_item_by_id(self, id):
        try:
            self.cur.execute('select * from item where id = %s', (id,))
            return self.cur.fetchone()
        except psycopg2.Error as e:
            self.handleDBError(e)

    def get_items_by_cat(self, cat):
        try:
            self.cur.execute('select item.id, category.c_name, type.t_name, subtype.st_name, box, loc, descript from item '
	                            '  join category on item.cat = category.id '
	                            '  join type on item.atype = type.id '
	                            '  join subtype on item.subtype = subtype.id '
                                '  where item.cat = %s'
                                '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;', (cat,))
            rows = self.cur.fetchall()
        except psycopg2.Error as e:
            self.handleDBError(e)
        return rows

    def get_items_by_type(self, type_id):
        try:
                self.cur.execute('select item.id, category.c_name, type.t_name, subtype.st_name, box, loc, descript from item '
	                             '  join category on item.cat = category.id '
	                             '  join type on item.atype = type.id '
	                             '  join subtype on item.subtype = subtype.id '
                                 '  where item.atype = %s'
                                 '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;', (type_id,))
                rows = self.cur.fetchall()
        except psycopg2.Error as e:
            self.handleDBError(e)
        return rows

    def get_items_by_stype(self, stype_id):
        try:
                self.cur.execute('select item.id, category.c_name, type.t_name, subtype.st_name, box, loc, descript from item '
	                             '  join category on item.cat = category.id '
	                             '  join type on item.atype = type.id '
	                             '  join subtype on item.subtype = subtype.id '
                                 '  where item.subtype = %s'
                                 '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;', (stype_id,))
                rows = self.cur.fetchall()
        except psycopg2.Error as e:
            self.handleDBError(e)
        return rows

    def get_items_by_cat_type(self, cat, atype):
        try:
                self.cur.execute('select item.id, category.c_name, type.t_name, subtype.st_name, box, loc, descript from item '
	                             '  join category on item.cat = category.id '
	                             '  join type on item.atype = type.id '
	                             '  join subtype on item.subtype = subtype.id '
                                 '  where item.cat = %s and item.atype = %s'
                                 '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;', (cat, atype))
                rows = self.cur.fetchall()
        except psycopg2.Error as e:
            self.handleDBError(e)
        return rows

    def get_items_by_cat_type_subtype(self, cat, atype, asubtype):
        try:
                self.cur.execute('select item.id, category.c_name, type.t_name, subtype.st_name, box, loc, descript from item '
	                             '  join category on item.cat = category.id '
	                             '  join type on item.atype = type.id '
	                             '  join subtype on item.subtype = subtype.id '
                                 '  where item.cat = %s and item.atype = %s and item.subtype = %s'
                                 '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;', (cat, atype, asubtype))
                rows = self.cur.fetchall()
        except psycopg2.Error as e:
            self.handleDBError(e)
        return rows

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
        if show:
            for row in rows:
                self.win.putstr(str(row[0])+'\n')
        return rows

    def get_subtypes(self, show=False):
        try:
                self.cur.execute('select * from subtype order by st_name;')
                rows = self.cur.fetchall()
        except psycopg2.Error as e:
            self.handleDBError(e)
        if show:
            for row in rows:
                self.win.putstr(str(row[0])+', '+row[1]+', '+str(row[2])+'\n')
        return rows

    def get_subtypes_for(self, type_ids):
        try:
            if type(type_ids) == int:
                #type_ids = [type_ids]
                self.cur.execute('select * from subtype where atype = %s order by st_name;', (type_ids,))
            elif len(type_ids) == 0:
                return []
            elif type(type_ids) == tuple:
                sqlstr = self.cur.mogrify('select * from subtype where atype in %s order by atype;', (type_ids,))
                self.cur.execute(sqlstr)
            else:
                assert(False)
            return self.cur.fetchall()
        except psycopg2.Error as e:
            self.handleDBError(e)

    def get_subtype_for_id(self, stype_id):
        assert(type(stype_id) == int)
        try:
            self.cur.execute("select * from subtype where id = %s", (stype_id,))
            return self.cur.fetchone()
        except psycopg2.Error as e:
            handleDBError(e)

    def get_types(self, show=False):
        #self.win.putstr('id, t_name, cat\n')
        try:
                self.cur.execute('select * from type order by t_name;')
                rows = self.cur.fetchall()
        except psycopg2.Error as e:
            self.handleDBError(e)
        if show:
            for row in rows:
                self.win.putstr(str(row[0])+', '+row[1]+', '+str(row[2])+'\n')
        return rows

    def get_types_for_cat(self, cat_id):
        try:
            self.cur.execute('select * from type where cat = %s order by t_name;', (cat_id,))
            rows = self.cur.fetchall()
        except psycopg2.Error as e:
            self.handleDBError(e)
        return rows

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