import os, sys
curdir = os.path.dirname(os.path.realpath(__file__))
cpath = os.path.dirname(curdir)
root_directory = os.path.dirname(cpath)

if not root_directory in sys.path:
    sys.path.append(root_directory)