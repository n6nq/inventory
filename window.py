# The command window class. Implemented with windows cmd window.
# May be implemented with windows-curses later.
import ctypes
import sys
import msvcrt
from scanf import scanf
import time

class CmdWindow:

    def __init__(self):
        self.curx = 0
        self.cury = 0
        self.title = 'Not set yet'
        self.lasthl = (False, None, None, None, None)
        # Initialize the command window's virtual terminal processing mode
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING

    def bell(self):
        self.putstr('\07')

    def choice_at(self, line, col, choices, clear):
        letters = ''
        choicestr = ''
        for choice in choices:
            letters += choice[0]
            choicestr += '\x1B[1m'+choice[0]+'\x1B[0m'+choice[1:]+' '
        if clear:
            self.clrln(line)
        
        while(True):
            self.str_at(line, col, choicestr)
            c = self.getch().upper()
            self.clrln(line)
            if c in letters:             
                return c
            else:
                self.str_at(line, col, 'Unknown choice '+c+'. Press a key to try again.')
                self.getch()
                self.clrln(line)

    def clear(self):
        self.putstr('\x1B[2J')
        self.lasthl = (False, None, None, None, None)

    def clrln(self, y):
        self.move(y, 1)
        self.putstr('\x1B[0K')

    def clrtoend(self, line, col):
        self.move(line, col)
        self.putstr('\x1B[0J')
        self.lasthl = (False, None, None, None, None)

    def double_check_list(self, members, candidate, which_col):
        for member in members:
            if member[which_col] == candidate:
                return member
        return None

    def getch(self):
        while msvcrt.kbhit():
            c = msvcrt.getch()
        c = msvcrt.getch().decode('utf-8')
        return c

    def getloc(self):
        '''Disabled for now. Windows Cmd window does not reliably
        support this function. Too bad.'''
        #assert(False)
        locstr = ''
        self.putstr('\x1B[6n')
        time.sleep(0.25)
        while msvcrt.kbhit():
            c = msvcrt.getch()
            locstr += c.decode('utf-8')
        loc = scanf('\x1B[%d;%dR', locstr)
        if loc == None:
            return (0, 0)
        self.cury = loc[0]
        self.curx = loc[1]
        return loc

    def getstr(self):
        newstr = ''
        c = 0
        while True:
            c = self.getch()
            if c == '\r':
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
        self.str_at(startline+index, 1, '\x1B[1m'+hlchars+'\x1B[0m')
        self.lasthl = (True, members, startline, index, hlen)
        

    def move(self, y, x):

        seq = '\x1B[' + repr(y) + ';' + repr(x) + 'H'
        self.putstr(seq)

    def putstr(self, astr):
        print(astr, end='', flush=True)

    def restart(self):
        self.clear()
        self.str_at(1,1, self.title)
        self.lasthl = (False, None, None, None, None)

    def restore_loc(self):
        self.putstr('\x1B8')
        
    def save_loc(self):
        self.putstr('\x1B7')

    # def select_from_list(self, startline, title, members):
    #     # Clear the screen from startline and set the title of the list
    #     members.append((-1, 'new '+title))
    #     self.move(startline,1)
    #     self.clrtoend()
    #     self.str_at(startline,1, 'Choose a '+title+' or type \'new\'')
    #     # Position to start of list and paint it
    #     headline = startline
    #     startline += 1
    #     nextline = startline
    #     for member in members:
    #         self.str_at(nextline,1, member[1])
    #         nextline += 1
    #     # Collect user user input and search letter by letter
    #     searchstr = ''
    #     while True:
    #         # Add instructions to the end of the list
    #         self.str_at(nextline,1,'Type characters to find, Enter to select...')
    #         c = self.getch()
    #         if c == '\r' or c == '\t':
    #             self.move(headline,1)
    #             self.clrtoend()
    #             return i
    #         found = False
    #         searchstr += c
    #         for i in range(len(members)):
    #             member = members[i][1]
    #             # if we find a match, highlight it
    #             if member.find(searchstr) == 0:
    #                 found = True
    #                 hlen = len(searchstr)
    #                 self.high_lite_lst_mbr(members, startline, i, hlen)
    #                 break
    #         if not found:
    #             self.str_at(nextline,1, searchstr + ' was not found. Try \'new\'. Type any key to try again.')
    #             self.unhighlight()
    #             searchstr = ''
    #             self.getch()
    #             self.clrln(nextline)
          
    #     print(searchstr)

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
            self.str_at(nextline,1, member[mindex])
            nextline += 1

        return startline, headline, nextline

    def select_from_list(self, startline, title, members, mindex):
        # Clear the screen from startline and set the title of the list
        self.set_heading(title, startline)
                # members.append((-1, 'new '+title))
                # self.move(startline,1)
                # self.clrtoend()
                # self.str_at(startline,1, 'Choose a '+title+' or type \'new\'')

        # Position to start of list and paint it
        startline, headline, nextline = self.paint_list(startline, members, mindex)
                # headline = startline
                # startline += 1
                # nextline = startline
                # for member in members:
                #     self.str_at(nextline,1, member[mindex])
                #     nextline += 1

        # Collect user user input and search letter by letter
        searchstr = ''
        while True:
            # Add instructions to the end of the list
            self.str_at(nextline,1,'Type characters to find, Enter to select...')
            c = self.getch()
            if c == '\r' or c == '\t':
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
                    if c == '\r':
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

    def str_at(self, x, y, msg):
        self.move(x, y)
        self.putstr(msg)

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
            self.str_at(old_startline+old_index, 1, '\x1B[0m'+hlchars)



