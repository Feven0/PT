import os, sys
curdir = os.path.dirname(os.path.realpath(__file__))
root_directory = os.path.dirname(curdir)
#root_directory = cpath

if not root_directory in sys.path:
    sys.path.append(root_directory)