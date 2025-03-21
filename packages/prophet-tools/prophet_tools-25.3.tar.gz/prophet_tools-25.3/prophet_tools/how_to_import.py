import os
import sys

parent_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)

import tools.prophet_tools.my_functions as mf
# from tools.my_functions import list_of_files, copy_to_clipboard