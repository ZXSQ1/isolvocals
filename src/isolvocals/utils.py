from sys import stderr
from isolvocals import env
import click


def error(msg):
    click.echo(f"Error: {msg}", file=stderr, err=True)
    exit()


def info(msg):
    click.echo(msg, file=env.logfile)

