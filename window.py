# The command window class. Implemented with windows cmd window.
# May be implemented with windows-curses later.
import ctypes
import sys
import curses
import msvcrt
from scanf import scanf
import time

class CmdWindow:

    def __init__(self,stdscr):
        self.stdscr = stdscr
        self.curx = 0
        self.cury = 0
        self.title = 'Not set yet'
        self.saved_cursor = (1,1)
        self.lasthl = (False, None, None, None, None)
        ## Initialize the command window's virtual terminal processing mode
        # kernel32 = ctypes.windll.kernel32
        # handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        # mode = ctypes.c_uint()
        # kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        # kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING

    def bell(self):
        curses.beep()
        #self.putstr('\07')

    def choice_at(self, line, col, choices, clear):
        letters = ''
        ln = line
        cl = col
        nchoices = len(choices)
        choicen = 0
        if clear:
            self.clrln(line)

        for choice in choices:
            choicen += 1
            letters += choice[0]
            self.stdscr.addstr(ln, cl, choice[0], curses.A_BOLD)
            rest = choice[1:]
            if choicen != nchoices:
                rest += ', '
            self.stdscr.addstr(ln, cl+1, rest, curses.A_NORMAL)
            cl += len(choice)+2
            self.stdscr.refresh()
        
        while(True):
            c = self.getch().upper()
            if c in letters:             
                self.clrln(ln)
                return c
            else:
                self.str_at(ln+1, 1, 'Unknown choice '+c+'. Press a key to try again.')
                self.getch()
                self.clrln(ln+1)

    def clear(self):
        self.putstr('\x1B[2J')
        self.lasthl = (False, None, None, None, None)

    def clrln(self, line):
        self.stdscr.move(line, 1)
        self.stdscr.clrtoeol()
        self.stdscr.refresh()
        #self.putstr('\x1B[0K')

    def clrtoend(self, line, col):
        self.stdscr.move(line, col)
        self.stdscr.clrtobot()
        self.stdscr.refresh()
        #self.putstr('\x1B[0J')
        self.lasthl = (False, None, None, None, None)

    def double_check_list(self, members, candidate, which_col):
        for member in members:
            if member[which_col] == candidate:
                return member
        return None

    def getch(self):
        c = self.stdscr.getch()
        c = chr(c)
        # while msvcrt.kbhit():
        #     c = msvcrt.getch()
        # c = msvcrt.getch().decode('utf-8')
        return c

    def getloc(self):
        loc = self.stdscr.getyx()
        # locstr = ''
        # self.putstr('\x1B[6n')
        # time.sleep(0.25)
        # while msvcrt.kbhit():
        #     c = msvcrt.getch()
        #     locstr += c.decode('utf-8')
        # loc = scanf('\x1B[%d;%dR', locstr)
        # if loc == None:
        #     return (0, 0)
        self.cury = loc[0]
        self.curx = loc[1]
        return loc

    def getstr(self):
        newstr = ''
        c = 0
        while True:
            c = self.getch()
            if c == '\n':
                return newstr
            newstr += c
            self.putstr(c)

    def getstr_at(self,line,col,prompt):
        self.clrtoend(line, col)
        if prompt:
            self.str_at(line, col, prompt + ': ')
        newstr = self.getstr()
        self.clrln(line)
        return newstr

    def high_lite_lst_mbr(self, members, startline, index, mindex, hlen):
        self.unhighlight(mindex)
        member = members[index][mindex]
        hlchars = member[0:hlen]
        self.str_at(startline+index, 1, hlchars, curses.A_BOLD)
        self.lasthl = (True, members, startline, index, hlen)
        

    def move(self, y, x):

        seq = '\x1B[' + repr(y) + ';' + repr(x) + 'H'
        self.putstr(seq)

    def putstr(self, astr):
        self.stdscr.addstr(astr)
        self.stdscr.refresh()

    def restart(self):
        self.stdscr.clear()
        self.stdscr.addstr(1,1, self.title)
        self.stdscr.refresh()
        self.lasthl = (False, None, None, None, None)   #TODO do we still need this

    def restore_loc(self):
        self.stdscr.move(self.saved_cursor[0], self.saved_cursor[1])
        #self.putstr('\x1B8')
        
    def save_loc(self):
        self.saved_cursor = self.stdscr.getyx()
        #self.putstr('\x1B7')

    def set_heading(self, title, startline):
        # Clear the screen from startline and set the title of the list
        #members.append((-1, 'new '+title))
        self.clrtoend(startline, 1)
        self.str_at(startline,1, 'Choose a '+title)

    def paint_list(self, startline, members, mindex):
        headline = startline
        startline += 1
        nextline = startline
        for member in members:
            if mindex == -1:
                rowstr = member[0]
                for i in range(1,len(member)):
                    rowstr += ', '
                    rowstr += member[i]
                self.str_at(nextline, 1, rowstr)
            else:
                self.str_at(nextline,1, member[mindex])
            nextline += 1

        return startline, headline, nextline

    #==========================================================================================
    # select_from_list - select from a list of choices provided by the caller or accept a new 
    # choice provided by the user. 
    # Inputs: 
    # startline = The line on which to start the list, the heading is placed on the start line, 
    # start_line is bumped by 1 when returned by paint_list
    # title = is name of the objects in the list
    # members = a list of objects that will be chosen from. Each member is a tuple with any number 
    # of columns. One column or all columns can be displayed
    # mindex = is the 0 based index of the column will be displayed and chosen from. mindex can 
    # also carry special values to sleect special behaviors. Behaviors are implemented by paint_list. 
    # Currently only one, -1 means display all columns. This will also affect list search matching.
    # When a specific column has been specified, matching is always done from the first character. 
    # When all columns are displayed, the match can occur anywhere in anycolumn.set

    def select_from_list(self, startline, title, members, mindex):
        # Clear the screen from startline and set the title of the list
        self.set_heading(title, startline)

        # Position to start of list and paint it
        startline, headline, nextline = self.paint_list(startline, members, mindex)

        # Collect user user input and search letter by letter
        searchstr = ''
        while True:
            # Add instructions to the end of the list
            self.str_at(nextline,1,'Type characters to find, Enter to select...')
            c = self.getch()
            if c == '\n' or c == '\t':
                self.clrtoend(headline, 1)
                return members[i]
            elif c == '\x1b':
                self.clrtoend(headline, 1)
                return (-2, 'Escaped')
            found = False
            searchstr += c.upper()
            for i in range(len(members)):
                member = members[i][mindex].upper()
                # if we find a match, highlight it
                if member.find(searchstr) == 0:
                    found = True
                    hlen = len(searchstr)
                    self.high_lite_lst_mbr(members, startline, i, mindex, hlen)
                    break
            if not found:
                self.unhighlight(mindex)
                searchstr = searchstr.lower()
                self.str_at(nextline,1, 'New '+title+'? Continue, Enter to complete, Escape to start over: '+searchstr)
                while True:
                    c = self.getch()
                    if c == '\n':
                        self.clrtoend(headline, 1)
                        return (-1, searchstr)
                    elif c == '\x1B':
                        self.clrln(nextline)
                        searchstr = ''
                        break
                    self.putstr(c)
                    searchstr += c
                
          
        print(searchstr)

    def set_title(self, str):
        self.title = str

    def str_at(self, line, col, msg, attrib = curses.A_NORMAL):
        self.stdscr.addstr(line, col, msg, attrib)
        self.stdscr.refresh()
        #self.move(x, y)
        #self.putstr(msg)

    def title(self, msg):
        self.move(0, 0)
        self.clrln()
        self.putstr(msg)

    def unhighlight(self, mindex):
        if self.lasthl[0]:  # is there a highlight on the screen?
            old_members = self.lasthl[1]
            old_startline = self.lasthl[2]
            old_index = self.lasthl[3]
            old_hlen = self.lasthl[4]
            member = old_members[old_index][mindex]
            hlchars = member[0:old_hlen]
            self.str_at(old_startline+old_index, 1, hlchars, curses.A_NORMAL)



