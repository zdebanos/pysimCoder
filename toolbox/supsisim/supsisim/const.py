import os

GRID = 10
PW = 6

BWmin = 80
BHmin = 60
BHstep = 20

PD = 40
NW = 4
LW =2
DP = 100.0

DB = 4

VERSION = 0.95

# Version of the .dgm file format, independent of VERSION.
# Should be bumped everytime a crucial change is made.
DGM_FORMAT_VERSION = 1

path = os.environ.get('PYSUPSICTRL') + '/'
respath = path+'resources/'
pycmd = 'jupyter qtconsole &'
pyrun = 'python3'
TEMP = '.'

