# __main__.py

import curses
from typing import cast, Callable

from inventory.main import main
from inventory.screenprotocol import ScreenProtocol

curses.wrapper(
    cast(Callable, main)
)

# import curses
# from typing import cast, Callable

# from inventory.main import main

# raise SystemExit(
#     curses.wrapper(cast(Callable[[curses.window], int], main))
# )

