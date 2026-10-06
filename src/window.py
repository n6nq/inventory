# The command window class. Implemented with windows cmd window.
# May be implemented with windows-curses later.

import curses
from collections.abc import Sequence
import inventory.src.cnst as cnst
from inventory.src.models import ListMemberProtocol, String


class MyCurses:
    PADENTER = 10
    KEY_A2 = 450
    KEY_B1 = 452
    KEY_B3 = 454
    KEY_C2 = 456

class CmdWindow:

    def __init__(self,stdscr: curses.window) -> None:
        self.stdscr = stdscr
        self.curx: int = 0
        self.cury = 0
        self.title: str = 'Not set yet'
        self.saved_cursor: tuple[int,int] = (1,1)
        self.stdscr.clear()
        self.title_line: int = 0
        self.what_line: int = 1
        self.item_line: int = 1
        self.list_header_line: int = 2
        self.description_line: int = 2
        self.prompt_line = curses.LINES - 1     # the lines are zero-based indexing
        # self.lasthl = (False, [(0,0,0)], 0, 0, 0)

    def bell(self) -> None:
       curses.beep()
        #self.putstr('\07')

    def choice_at(self, line: int, col:int, choices:list[str], clear: bool) -> str:
        letters = ''
        nchoices = len(choices)
        choicen = 0
        if clear:
            self.clrln(line)

        self.str_at(line, col, "Choose one: ")
        ncol = self.getloc()[1]   #[1] picks off the col from a location which (y, x) or (line, col)

        for choice in choices:
            amp_at = choice.find('&')
            if amp_at == -1:
                self.str_at(line, col, 'A choice string does not have an &! ' + repr(choices) + ' Any key to exit.')
                self.getch(cnst.ANY)
                exit()
            first = choice[0:amp_at]
            boldChar = choice[amp_at+1]
            rest = choice[amp_at+2:]

            choicen += 1
            letters += boldChar

            self.str_at(line, ncol, first, curses.A_NORMAL)
            ncol += len(first)
            self.str_at(line, ncol, boldChar, curses.A_BOLD)
            ncol += 1
            if choicen != nchoices:
                rest += ', '
            self.str_at(line, ncol, rest, curses.A_NORMAL)
            ncol += len(rest)
        self.str_at(line, ncol, ', Esc', curses.A_NORMAL)

        while(True):
            c = self.getch(cnst.A_Z | cnst.ESC).upper()
            if c in letters or c == cnst.ESCAPE:             
                self.clrln(line)
                return c
            else:
                self.str_at(line-1, 1, 'Unknown choice '+c+'. Press a key to try again.')
                self.getch(cnst.ANY)
                self.clrln(line-1)

    def clear(self) -> None:
        self.putstr('\x1B[2J')
        # self.lasthl = (False, list[tuple[str]], 0, 0, 0)

    def clrln(self, line: int) -> None:
        self.stdscr.move(line, 1)
        self.stdscr.clrtoeol()
        self.stdscr.refresh()
        #self.putstr('\x1B[0K')

    def clrtoend(self, line: int, col: int) -> None:
        self.stdscr.move(line, col)
        self.stdscr.clrtobot()
        self.stdscr.refresh()
        #self.putstr('\x1B[0J')
        # self.lasthl = (False, list[tuple[str]], 0, 0, 0)

    def double_check_list(self, members: list[tuple[str]], candidate: str, which_col: int) -> tuple[str] | None:
        for member in members:
            if member[which_col] == candidate:
                return member
        return None

    def errorHandler(self, msg: str | None, msgs: list[str] | None) -> None:
        self.restart()
        if msg != None and msg != "NORAISE":
            self.str_at(self.what_line, 1, msg)
        elif msgs != None:
            self.select_from_list(msgs, cnst.DSPLYRAWSTR, None, "Warnings", self.what_line, False)
        self.prompt('Press any key to continue...')
        self.getch(cnst.ANY)
        self.restart()

    def prompter(self, msg: str) -> None:
        self.str_at(self.prompt_line, 1, msg)

    def getch(self, which: int) -> str:
        while True:
            key = self.stdscr.getkey()
            if which & cnst.ANY:
                return key
            elif which & cnst.A_Z and key.isalpha():
                return key
            elif which & cnst.NUMBER and key.isdigit():
                return key
            elif which & cnst.SPACE and key == ' ':
                return key
            elif which & cnst.NL and key == '\n':
                return key
            elif which & cnst.TAB and key == '\t':
                return key
            elif which & cnst.ESC and key == '\x1b':
                return key
            elif which & cnst.UP and key == 'KEY_UP' or key == 'KEY_A2':
                return key
            elif which & cnst.DOWN and key == 'KEY_DOWN' or key == 'KEY_C2':
                return key
            elif which & cnst.LEFT and key == 'KEY_LEFT' or key == 'KEY_B1':
                return key
            elif which & cnst.RIGHT and key == 'KEY_RIGHT' or key == 'KEY_B3':
                return key
            elif which & cnst.PRINTABLE and key.isprintable():
                return key
            elif which & cnst.BS and key == '\x08':
                return key
            else:
                self.bell()

    def getloc(self) -> tuple[int, int]:
        loc = self.stdscr.getyx()
        self.cury = loc[0]
        self.curx = loc[1]
        return loc

    def getstr(self) -> str | None:
        loc = self.getloc()
        newstr = ''
        c = ''
        while True:
            c = self.getch(cnst.NL | cnst.BS | cnst.PRINTABLE | cnst.SPACE)
            if c == '\n':
                return newstr
            elif c == '\x1b':
                return None
            elif c == cnst.BACKSPACE:
                newstr = newstr[:-1]
                self.stdscr.move(loc[0],loc[1])
                self.stdscr.clrtoeol()
                self.putstr(newstr)
                continue
            newstr += c
            self.putstr(c)
        return newstr

    def getstr_at(self, line: int, col: int, prompt: str) -> str | None:
        self.clrtoend(line, col)
        if prompt:
            self.str_at(line, col, prompt + ': ')
        newstr = self.getstr()
        self.clrln(line)
        return newstr

    def item_choice_str(self, astr: str) -> None:
        self.clrtoend(self.item_line, 1)
        self.str_at(self.item_line, 1, astr)
        self.stdscr.refresh()                   #TODO redundant

    # def high_lite_lst_mbr(self, members: list[tuple[str]], startline: int, index: int, mindex: int, hlen: int) -> None:
    #     self.unhighlight(mindex)
    #     member = members[index][mindex]
    #     hlchars = member[0:hlen]
    #     self.str_at(startline+index, 1, hlchars, curses.A_BOLD) #todo need to account for what column we are searching
    #     self.lasthl = (True, members, startline, index, hlen)
        

    def move(self, y: int, x: int) -> None:
        seq = '\x1B[' + repr(y) + ';' + repr(x) + 'H'
        self.putstr(seq)

    def prompt(self, prompt: str) -> None:
        self.clrtoend(self.prompt_line, 1)
        self.str_at(self.prompt_line, 1, prompt)
        self.stdscr.refresh()

    def putstr(self, astr: str) -> None:
        self.stdscr.addstr(astr)
        self.stdscr.refresh()

    def restart(self) -> None:
        self.stdscr.clear()
        self.str_at(self.title_line,1, self.title)
        self.stdscr.refresh()
        # self.lasthl = (False, list[tuple[str]], 0, 0, 0)   #TODO do we still need this

    def restore_loc(self) -> None:
        self.stdscr.move(self.saved_cursor[0], self.saved_cursor[1])
        #self.putstr('\x1B8')
        
    def save_loc(self) -> None:
        self.saved_cursor = self.stdscr.getyx()
        #self.putstr('\x1B7')

    def set_list_heading(self, title: str) -> None:
        # Clear the screen from startline and set the title of the list
        #members.append((-1, 'new '+title))
        self.clrtoend(self.list_header_line, 1)
        self.str_at(self.list_header_line,1, 'Choose a '+title)

    #==========================================================================================
    # select_from_list - select from a list of choices provided by the caller or accept a new 
    # choice provided by the user. 
    # Inputs: 
    # startline = The line on which to start the list, the heading is placed on the start line, 
    # start_line is bumped by 1 when returned by paint_list
    # title = is name of the objects in the list
    # members = a list of objects that will be chosen from. Each member is a ListMember with any number 
    # of columns. One column or all columns can be displayed
    # mindex = is the 0 based index of the column will be displayed and chosen from. mindex can 
    # also carry special values to select special behaviors. Behaviors are implemented by paint_list. 
    # Currently only one, -1 means display all columns. This will also affect list search matching.
    # When a specific column has been specified, matching is always done from the first character. 
    # When all columns are displayed, the match can occur anywhere in any column.
    # Returns: 0-n if a list member is selected, cnst.NEWOBJ if a new object is created, or cnst.CANCELED 
    # if the user cancels the selection.
 
    def select_from_list(self, members: Sequence[ListMemberProtocol], display_what: int, preselect: str | int, list_header: str, header_at: int, new_allowed: bool) -> int:
        """
        Displays a scrollable, selectable list of ListMembers in the terminal using curses.
        Highlights the current selection with a '>' marker. If display_what == -1,
        shows all ListMembers joined by commas.
        Returns the selected index or cnst.CANCELED  or cnst.NEWOBJ, search_buffer if a new object is created.
        Assumes self.stdscr is a curses window object.
        """
        curses.curs_set(0)
        self.stdscr.keypad(True)
        height, width = self.stdscr.getmaxyx()
        max_list_lines = height - (header_at + 1 + 1)  # Header_at + 1(zero base) + input line
        if type(preselect) is int:
            for i in range(0,len(members)):
                if members[i].id == preselect:
                    selected_index = i
                    break
            else: 
                selected_index = 0
        elif type(preselect) is str:
            selected_index = -1
            for i, member in enumerate(members):
                if member.has_str(preselect):
                    selected_index = i
                    break
            else:
                selected_index = 0
        else:
            selected_index = 0

        scroll_pos = 0
        search_buffer = ""
        search_direction = None
        match_positions: list[int] = []
        match_cursor = 0


        while True:
            self.clrtoend(header_at, 1)

            # Title and header
            #self.str_at(0, 2, self.title[:width-4], curses.A_BOLD)
            self.str_at(header_at, 2, list_header[:width-4], curses.A_BOLD)

            # Determine visible range
            visible_items = members[scroll_pos:scroll_pos + max_list_lines]

            #self.str_at(height - 2, 2, f"Selected index: {selected_index}, Scroll pos: {scroll_pos}"[:width-4])

            for i, item in enumerate(visible_items):
                y = i + header_at + 1           # list starts on the next line after the header
                actual_index = scroll_pos + i
                
                match display_what:
                    case cnst.DSPLYALL:
                        display_text = item.str_all()
                    case cnst.DSPLYNAME:
                        display_text = item.str_name()
                    case cnst.DSPLYSTR:
                        display_text = item.str_name()
                    case cnst.DSPLYRAWSTR:
                        display_text = str(item)
                    case _:
                        assert(False)           # programming error, should not happen

                prefix = "> " if actual_index == selected_index else "  "

                if actual_index == selected_index and search_buffer:
                    query = search_buffer.lower()
                    display_lower = display_text.lower()

                    # Find all match positions
                    match_positions = []
                    start = 0
                    while True:
                        idx = display_lower.find(query, start)
                        if idx == -1:
                            break
                        match_positions.append(idx)
                        start = idx + 1  # Allow overlapping matches if needed

                    # If cursor is unset, initialize based on direction
                    if match_cursor == -1:
                        if search_direction == 'backward':
                            match_cursor = len(match_positions) - 1
                        else:
                            match_cursor = 0

                    if match_positions:
                        match_start = match_positions[match_cursor % len(match_positions)]
                        before = display_text[:match_start]
                        match = display_text[match_start:match_start + len(query)]
                        after = display_text[match_start + len(query):]

                        x = 2
                        self.str_at(y, x, prefix)
                        x += len(prefix)
                        self.str_at(y, x, before[:width - x - 1])
                        x += len(before)
                        self.str_at(y, x, match[:width - x - 1], curses.A_REVERSE)
                        x += len(match)
                        self.str_at(y, x, after[:width - x - 1])
                    else:
                        self.str_at(y, 2, (prefix + display_text)[:width-4])
                else:
                    self.str_at(y, 2, (prefix + display_text)[:width-4])

            # Input prompt
            input_prompt = f"Search: {search_buffer}  (↑↓ to scroll, F3=Next, F2=Prev, Enter=Select, ESC=Cancel)"
            self.str_at(self.prompt_line, 2, input_prompt[:width-4])

            self.stdscr.refresh()

            key = self.stdscr.getch()
            #key_name = curses.keyname(key)
            if key == curses.KEY_UP or key == MyCurses.KEY_A2: # type: ignore[attr-defined]
                match_cursor = 0        # when using arrow keys, searches will always start from the left
                search_direction = None
                if selected_index > 0:
                    selected_index -= 1
                    if selected_index < scroll_pos:
                        scroll_pos -= 1

            elif key == curses.KEY_DOWN or key == MyCurses.KEY_C2: 
                match_cursor = 0        # when using arrow keys, searches will always start from the left
                search_direction = None
                if selected_index < len(members) - 1:
                    selected_index += 1
                    if selected_index >= scroll_pos + max_list_lines:
                        scroll_pos += 1


            elif key in (ord('\n'), curses.KEY_ENTER, MyCurses.PADENTER):  # type: ignore[attr-defined]
                if len(members) == 0:
                    return cnst.CANCELED
                return selected_index

            elif key  == 27:  # Q or q or ESC
                return cnst.CANCELED

            elif key in (curses.KEY_BACKSPACE, 127, 8):
                search_buffer = search_buffer[:-1]

            elif 32 <= key <= 126:  # Printable ASCII, including space
                #if len(members) == 0:
                #    return cnst.CANCELED



                search_buffer += chr(key)

                query = search_buffer.lower()

                # Check if current selection still matches
                if len(members) == 0:
                    current_text = ''
                else:
                    current_item = members[selected_index]
                    if display_what == cnst.DSPLYALL:
                        current_text = current_item.str_all()
                    elif display_what ==  cnst.DSPLYNAME:
                        current_text = current_item.str_name()
                    elif display_what ==  cnst.DSPLYSTR:
                        current_text = current_item.str_name()
                    else:
                        assert(False)

                if query not in current_text.lower():
                    # Search forward from next index
                    list_len = len(members)
                    start = 1 if list_len == 0 else (selected_index + 1) % len(members)
                    #start = (selected_index + 1) % len(members)
                    match_index = None

                    for i in range(len(members)):
                        idx = (start + i) % len(members)
                        test_item = members[idx]
                        if display_what == cnst.DSPLYALL:
                            display_text = test_item.str_all()
                        elif display_what ==  cnst.DSPLYNAME:
                            display_text = test_item.str_name()
                        elif display_what ==  cnst.DSPLYSTR:
                            display_text = test_item.str_name()
                        else:
                            assert(False)

                        if query in display_text.lower():
                            match_index = idx
                            break

                    if match_index is not None:
                        selected_index = match_index

                        # Adjust scroll only if needed

                        if selected_index < scroll_pos:
                            scroll_pos = selected_index
                        elif selected_index >= scroll_pos + max_list_lines:
                            scroll_pos = selected_index - max_list_lines + 1

                    else:
                        self.clrtoend(header_at, 1)
                        if not new_allowed:
                            self.str_at(self.prompt_line, 1, 'New '+list_header+' are not allowed when searching? Escape to select existing '+ list_header+'.')
                            while True:
                                c = self.getch(cnst.ESC)
                                if c == '\x1B':
                                    self.clrln(height-2)    #todo  nothing there, not needed.
                                    search_buffer = ''
                                    break
                                else:
                                    curses.beep()
                        else:
                            self.str_at(self.prompt_line, 1, 'New '+list_header+'? Continue, Enter to complete, Escape to start over: ' + search_buffer)
                            loc = self.getloc()
                            loc = (loc[0], loc[1]-len(search_buffer))
                            while True:
                                c = self.getch(cnst.PRINTABLE | cnst.NL | cnst.ESC | cnst.BS | cnst.LEFT)
                                if c == '\n':
                                    self.clrtoend(header_at, 1)
                                    new_obj = String(id=cnst.NEWOBJ, string=search_buffer)    
                                    members.append(new_obj)
                                    return cnst.NEWOBJ
                                
                                elif c == '\x1B':
                                    self.clrln(height-2)
                                    search_buffer = ''
                                    break
                                elif c == cnst.BACKSPACE or c == 'KEY_LEFT':
                                    search_buffer = search_buffer[:-1]
                                    self.stdscr.move(loc[0],loc[1])
                                    self.stdscr.clrtoeol()
                                    self.putstr(search_buffer)
                                    continue

                                self.putstr(c)
                                search_buffer += c


            elif key == curses.KEY_F3:
                search_direction = 'forward'
                if match_positions and match_cursor + 1 < len(match_positions):
                    match_cursor += 1
                else:
                    # Jump to next line with match
                    match_cursor = 0    # when jumping to a new line
                    query = search_buffer.lower()
                    for i in range(len(members)):
                        idx = (selected_index + 1 + i) % len(members)
                        if display_what == -1:
                            display_text = ", ".join(str(x) for x in members[idx])
                        else:
                            try:
                                display_text = str(members[idx][display_what])
                            except IndexError:
                                display_text = ""
                        if query in display_text.lower():
                            selected_index = idx
                            scroll_pos = max(0, selected_index - max_list_lines // 2)
                            match_cursor = 0
                            break
                    else:
                        curses.beep()

            elif key == curses.KEY_F2:
                search_direction = 'backward'
                if match_positions and match_cursor > 0:
                    # Move to previous within the same line
                    match_cursor -= 1
                else:
                    # Search backward for previous line with a match
                    #match_cursor = len(match_positions) - 1 # start with the last match in the new line
                    query = search_buffer.lower()
                    found = False
                    for i in range(1, len(members)):
                        idx = (selected_index - 1) % len(members)
                        if display_what == -1:
                            display_text = ", ".join(str(x) for x in members[idx])
                        else:
                            try:
                                display_text = str(members[idx][display_what])
                            except IndexError:
                                display_text = ""
                        if query in display_text.lower():
                            selected_index = idx
                            scroll_pos = max(0, selected_index - max_list_lines // 2)
                            match_cursor = -1    #YIKES
                            found = True
                            break
                    if not found:
                        curses.beep()

            elif key == 10 or key == MyCurses.PADENTER:  # type: ignore[attr-defined]
                return selected_index

            elif key in (ord('q'), ord('Q')):
                return cnst.CANCELED


    def set_title(self, astr: str) -> None:
        self.title = astr

    def str_at(self, line: int, col: int, msg: str, attrib: int = curses.A_NORMAL) -> None:
        self.stdscr.addstr(line, col, msg, attrib)
        self.stdscr.refresh()




