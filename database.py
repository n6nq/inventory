import psycopg2
import cnst

class Database():
    
    def __init__(self, awin):
        self.win = awin
        self.conn = psycopg2.connect("dbname=Inventory user=postgres password=Spl1tL1ckSt1ck")
        self.conn.set_session(autocommit=True)
        print(repr(self.conn))

        self.cur = self.conn.cursor()

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
        self.cur.execute('insert into category (c_name) values (%s) returning id, c_name;', (c_name,))
        row = self.cur.fetchone()
        self.win.putstr('Added category: ' + c_name + ' with id: ' + str(row[0]) + '\n')
        return row

    def add_item(self, cat_id, type_id, subtype_id, box, loc, descript):
        self.cur.execute('insert into item (cat, atype, subtype, box, loc, descript) values (%s, %s, %s, %s, %s, %s) returning id;', 
                         (cat_id, type_id, subtype_id, box, loc, descript))
        row = self.cur.fetchone()
        self.win.putstr('Added item with id: ' + str(row[0]) + '\n')
        return row

    def add_type(self, t_name, cat_id):
        self.cur.execute('insert into type (t_name, cat) values (%s, %s) returning id, t_name, cat;', (t_name, cat_id))
        row = self.cur.fetchone()
        self.win.putstr('Added type: ' + t_name + ' with id: ' + str(row[0]) + '\n')
        return row

    def add_subtype(self, st_name, type_id):
        self.cur.execute('insert into subtype (st_name, atype) values (%s, %s) returning id, st_name, atype;', (st_name, type_id))
        row = self.cur.fetchone()
        self.win.putstr('Added subtype: ' + st_name + ' with id: ' + str(row[0]) + '\n')
        return row

    def get_box_letters(self):
        self.cur.execute('SELECT distinct(substring(box,1,1)) FROM public.item ORDER BY 1 ASC;')
        rows = self.cur.fetchall()
        return rows

    def get_box_numbers(self, letter):
        self.cur.execute('SELECT distinct(substring(box,2)) FROM public.item where substring(box,1,1) = %s ORDER BY 1 ASC;', (letter,))
        rows = self.cur.fetchall()
        return rows

    def get_categories(self, show=False):
        if show:
            self.win.putstr('id, c_name\n')
        self.cur.execute('select * from category order by c_name;')
        rows = self.cur.fetchall()
        if show:
            for row in rows:
                self.win.putstr(str(row[0])+', '+row[1]+'\n')
        return rows

    def get_items(self, show=False):
        if show:
            self.win.putstr('id, cat, atype, subtype, box, loc, descript\n')
        self.cur.execute('select * from item order by cat asc;')
        rows = self.cur.fetchall()
        if show:
            for row in rows:
                self.win.putstr(str(row[0])+', '+str(row[1])+', '+str(row[2])+', '+str(row[3])+', '+row[4]+', '+row[5]+', '+row[6]+'\n')
        return rows

    def get_joined_items(self, show=False):
        if show:
            self.win.putstr('id, cat, atype, subtype, box, loc, descript\n')
        self.cur.execute('select category.c_name, type.t_name, subtype.st_name, box, loc, descript from item '
	                     '  join category on item.cat = category.id '
	                     '  join type on item.atype = type.id '
	                     '  join subtype on item.subtype = subtype.id '
                         '  order by category.c_name asc, type.t_name asc, subtype.st_name asc;')
        rows = self.cur.fetchall()
        if show:
            for row in rows:
                self.win.putstr(str(row[0])+', '+str(row[1])+', '+str(row[2])+', '+str(row[3])+', '+row[4]+', '+row[5]+', '+row[6]+'\n')
        return rows

    def get_locations(self, show=False):
        if show:
            self.win.putstr('boxid')
        self.cur.execute('select distinct(loc) from item order by loc;')
        rows = self.cur.fetchall()
        if show:
            for row in rows:
                self.win.putstr(str(row[0])+'\n')
        return rows

    def get_subtypes(self, show=False):
        self.win.putstr('id, at_name, atype\n')
        self.cur.execute('select * from subtype order by st_name;')
        rows = self.cur.fetchall()
        if show:
            for row in rows:
                self.win.putstr(str(row[0])+', '+row[1]+', '+str(row[2])+'\n')
        return rows

    def get_subtypes_for(self, type_id, show=False):
        if show:
            self.win.putstr('id, st_name, atype\n')
        self.cur.execute('select * from subtype where atype = %s order by st_name;', (type_id,))
        rows = self.cur.fetchall()
        if show:
            for row in rows:
                self.win.putstr(str(row[0])+', '+row[1]+', '+str(row[2])+'\n')
        return rows

    def get_types(self, show=False):
        self.win.putstr('id, t_name, cat\n')
        self.cur.execute('select * from type order by t_name;')
        rows = self.cur.fetchall()
        if show:
            for row in rows:
                self.win.putstr(str(row[0])+', '+row[1]+', '+str(row[2])+'\n')
        return rows

    def get_types_for(self, cat_id, show=False):
        if show:
            self.win.putstr('id, t_name, cat\n')
        self.cur.execute('select * from type where cat = %s order by t_name;', (cat_id,))
        rows = self.cur.fetchall()
        if show:
            for row in rows:
                self.win.putstr(str(row[0])+', '+row[1]+', '+str(row[2])+'\n')
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