# cnst.py -- Text filtering constants


ALL = 511       # All is all below expect any
A_Z	= 1         # All alpha charaters a to z
NL	= 2         # New line \n
TAB = 4         # tab is \t
ESC	= 8         # esc is \x1b
UP	= 16        # up is KEY_UP or KEY_A2
DOWN = 32       # down is KEY_DOWN or KEY_C2
LEFT = 64       # left is KEY_LEFT or KEY_B1
RIGHT = 128     # right is KEY_RIGHT or KEy_B3
PRINTABLE = 256    # ctrl_a is \x01
NUMBER = 512       # number is \d 
SPACE = 1024
BS = 2048
F2F3 = 4096
ANY  = 8192

NEWOBJ  = -1    # return values from select_from_list which 
CANCELED = -2   # normally returns

OBJID   = 0
OBJNAME = 1

# Item tuple
ID = 0
CAT = 1
TYPE = 2
SUB = 3
BOX = 4
LOC = 5
DESC = 6

# list display stype
DSPLYALL = -1
DSPLYSTR = 0
DSPLYNAME = 1
DSPLYRAWSTR = 2

# used values from curses and screenfake.py
A_BOLD = 2097152
A_NORMAL = 0
A_REVERSE = 262144
BACKSPACE = 127
CTRL_H = '\x08'
CTRL_J = 10
#DOWN = 258
ENTER = 10
ESCAPE = '\x1b'
KEY_A2 = 450
KEY_B1 = 452
KEY_B3 = 454
KEY_BACKSPACE = 263
KEY_C2 = 456
KEY_DOWN = 258
KEY_ENTER = 343
KEY_F2 = 266
KEY_F3 = 267
KEY_UP = 259
#LEFT = 260
PADENTER = 10
#RIGHT = 261
#UP = 259