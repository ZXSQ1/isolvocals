from sys import stderr
from colors import red, yellow
import env


def error(msg):
    if env.colored:
        print(red("[ERROR]"), msg, file=stderr)
    else:
        print(f"[ERROR] {msg}", file=stderr)

    exit(1)


def info(msg):
    if env.colored:
        print(yellow("[INFO]"), msg, file=env.logfile)
    else:
        print(f"[INFO] {msg}", file=env.logfile)


def file_ext(filename):
    return filename.split(".")[-1]
