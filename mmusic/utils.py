from sys import stderr
from colors import red

def error(msg):
    print(red("[ERROR]"), msg, file=stderr)
    exit(1)
