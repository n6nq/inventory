# screenprotocol.py  -- make curses and my test window interchangeable by defining the interface that will be used 
# by the rest of the program.  This is a protocol class, not a concrete class.

from typing import Protocol

    
class ScreenProtocol(Protocol):

    def addstr(self, y: int, x: int, string: str, attr: int) -> None: ...

    def clear(self) -> None:
        ...

    def clrtobot(self) -> None:
        ...

    def clrtoeol(self) -> None:
        ...
        
    def getch(self) -> int:
        ...

    def getkey(self) -> str:
        ...

    def getmaxyx(self) -> tuple[int, int]:
        ...

    def getyx(self) -> tuple[int, int]:
        ...

    def keypad(self, flag: bool) -> None:
        ...

    def move(self, y: int, x: int) -> None:
        ...

    def refresh(self) -> None:
        ...

    