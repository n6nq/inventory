# cnst.py -- Text filtering constants

from pickle import OBJ


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
ANY  = 2048

NEWOBJ  = -1    # if id col is -1, it is a new object that is not in the database yet.
#ESCAPED  = -2   # if id col is -2, no object was selected  obsolete

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
