"""
File in charge linking of the disp file ot the module so that it could be imported as a module
"""

from .my_disp import Disp, TOML_CONF, OUT_STRING, OUT_DEFAULT, OUT_FILE, OUT_TTY, KEY_ANIMATION_DELAY, KEY_PRETTIFY_OUTPUT_IN_BLOCKS, KEY_ANIMATION_DELAY_BLOCKY, KEY_OUTPUT_MODE, KEY_PRETTIFY_OUTPUT

SUCCESS = 0
ERR = 84
ERROR = 84

SAVE_TO_FILE = False
FILE_NAME = "run_results.txt"
FILE_DESCRIPTOR = None


IDISP = Disp(
    TOML_CONF,
    SAVE_TO_FILE,
    FILE_NAME,
)

IDISPLAY = IDISP
IDISPTTY = IDISP
IDTTY = IDISP


OSTRING = OUT_STRING
ODEFAULT = OUT_DEFAULT
OFILE = OUT_FILE
OTTY = OUT_TTY

KOUTPUT_MODE = KEY_OUTPUT_MODE
KPRETTIFY_OUTPUT = KEY_PRETTIFY_OUTPUT
KANIMATION_DELAY = KEY_ANIMATION_DELAY
KANIMATION_DELAY_BLOCKY = KEY_ANIMATION_DELAY_BLOCKY
KPRETTIFY_OUTPUT_IN_BLOCKS = KEY_PRETTIFY_OUTPUT_IN_BLOCKS


class Display(Disp):
    """ A rebind of the class named Disp """


class DispTTY(Disp):
    """ A rebind of the class named Disp """


class DisplayTTY(Disp):
    """ A rebind of the class named Disp """
