from typing import Callable, Any
import inventory.cnst as cnst
from inventory.screenprotocol import ScreenProtocol

# Screen sizes
SCREEN_MAXX = 80
SCREEN_MAXY = 25


class Page:
    def __init__(self, name: str, the_rows: list[str], nlines: int, position: tuple[int, int]):
        self.rows = the_rows
        self.linecnt = nlines
        self.cursor = position
        self.name = name

    def get_line(self, index: int) -> str:
        return self.rows[index]

    def str_in_line(self, string: str, index: int) -> bool:
        return string in self.rows[index]

    def find_in_page(self, string: str) -> bool:
        for y in range(self.linecnt):
            line: str = self.rows[y]
            x = line.find(string)
            if (x >= 0):
                return True
        return False

class ScreenFake(ScreenProtocol):
    def __init__(self):
        self.buffer: list[list[str]] = [[ ' ' for _ in range(SCREEN_MAXX) ] for _ in range(SCREEN_MAXY)]
        self.cursor: tuple[int, int] = (0, 0)  # (y, x)
        self.keypad_enabled: bool = False
        self.inbuf: list[str] = []  # Input buffer for getch and getkey
        self.pages: dict[str, Page] = {}    # captured screen dumps
        self.callbacks: dict[str, object] ={}  # registered callbacks, subtest to invoke after dumps



    def addstr(self, y: int, x: int, string: str, attr: int) -> None:
        for i, ch in enumerate(string):
            if x + i < SCREEN_MAXX:
                self.buffer[y][x + i] = ch
        self.cursor = (y, x + len(string))  # Move cursor to the end of the string

    def clear(self) -> None:
        self.buffer: list[list[str]]     = [[ ' ' for _ in range(SCREEN_MAXX) ] for _ in range(SCREEN_MAXY)]
        self.cursor= (0, 0)

    def clrtobot(self) -> None:
        y, x = self.cursor
        for i in range(y, SCREEN_MAXY):
            for j in range(x if i == y else 0, SCREEN_MAXX):
                self.buffer[i][j] = ' '

    def clrtoeol(self) -> None:
        y, x = self.cursor
        for j in range(x, SCREEN_MAXX):
            self.buffer[y][j] = ' '

    def clearpages(self):
        self.pages = {}

    subtest_cb: Callable[[str], None]

    def callback(self, name: str):
        self.subtest_cb(name)


    def register_cb(self, func: Callable[[str], None]):
       
        self.subtest_cb = func

    def dump(self, name: str) -> None:
        rows: list[str] = []
        # build the page, print it and save it in pages dictionary for later exam
        line = f"\r========================== {name} =================================\r"
        #page.append(line)
        #print(line)
        for row in self.buffer:
            line = ''.join(row)+"\r"
            rows.append(line)
            #print(line)

        line = "===========================================================\r"
       # page.append(line)
        #print(line)
        line = f"Cursor position: {self.cursor}"+"\r"
        #print(line)
        line = f"Keypad enabled: {self.keypad_enabled}"+"\r"
        #print(line)
        line = f"Input buffer: {self.inbuf}"+"\r"
        #print(line)
        # put the page in pages
        page = Page(name, rows, len(rows), self.cursor)
        self.pages[name] = page


        
    def getch(self) -> int:
        if not self.inbuf:
            self.dump()
            raise RuntimeError("Fake input buffer empty")
        ch = self.inbuf.pop(0)
        return ord(ch)
        
    def getkey(self) -> str:
        if not self.inbuf:
            self.dump("Buffer Empty")
            raise RuntimeError("Fake input buffer empty")
        nextcmd = self.inbuf.pop(0)
        if nextcmd[:4] == "DUMP":
            subcmds = nextcmd.split(sep=',')
            if len(subcmds) >= 2:
                self.dump(subcmds[1])
            else:
                raise RuntimeError("Dump with no name!")
            if len(subcmds) >= 3:
               self.callback(subcmds[2])
            nextcmd = self.inbuf.pop(0)
        return nextcmd

    def getpage(self, pagename: str) -> Page:
        return self.pages[pagename]
    
    def getmaxyx(self) -> tuple[int, int]:
        return (SCREEN_MAXY, SCREEN_MAXX)

    def getyx(self) -> tuple[int, int]:
        return self.cursor

    def input(self, inputs: list[str]) -> None:
        self.inbuf.extend(inputs)

    def keypad(self, flag: bool) -> None:
        self.keypad_enabled = flag

    def move(self, y: int, x: int) -> None:
        self.cursor = (y, x)

    def refresh(self) -> None:
        # No-op for fake screen
        pass
