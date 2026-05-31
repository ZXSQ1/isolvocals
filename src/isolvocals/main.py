import logging
import warnings
from isolvocals import env
logging.basicConfig(stream=env.logfile, level=logging.INFO)
warnings.simplefilter("ignore", UserWarning)

from isolvocals.models import DeepFilterNetIsolator
from sys import stdout
from os.path import exists, isfile, dirname
from isolvocals.media import media_type, media_convert
from isolvocals.utils import error, info
from tempfile import NamedTemporaryFile
import click


@click.command()
@click.option(
    "--model", "-m",
    type=click.Choice(["deepfilternet"]), 
    default="deepfilternet",
    help="The model used for music detection."
)

@click.option(
    "--out-filename", "-o",
    default="",
    type=str,
    help="The output filename."
)

@click.option(
    "--to-stdout", "-t",
    is_flag=True,
    default=False,
    help="Prints raw output to standard output."
)

@click.option(
    "--chunk-length", "-l",
    default=5000,
    type=int,
    help="The duration of each processed chunk (in milliseconds)."
)

@click.option(
    "--quiet", "-q",
    is_flag=True,
    default=not env.verbose,
    help="Remove information messages."
)

@click.option(
    "--progress", "-p",
    is_flag=True,
    default=env.progress,
    help="Progress in processing."
)

@click.option(
    "--progress-char",
    default=env.progress_char,
    type=str,
    help="Determine the progress bar fill character."
)

@click.option(
    "--progress-header",
    default=env.progress_header,
    type=str,
    help="Determine the header text of the progress bar."
)

@click.argument(
    "filename",
    type=str,
    required=True
)

def main(model, out_filename, to_stdout, chunk_length, quiet, progress,
    progress_char, progress_header, filename):

    """A terminal tool for playing media music-free."""
    if quiet:
        env.verbose = False 

    if out_filename and to_stdout or not (out_filename or to_stdout):
        error("Must specify either --out-filename or --to-stdout.")

    if progress and not to_stdout:
        env.progress = True 

    if len(progress_char) > 0:
        if len(progress_char) > 1:
            error("Progress character must be only one character.")

        env.progress_char = progress_char

    if not exists(filename):
        error(f"File '{filename}' does not exist.")

    if not isfile(filename):
        error(f"File '{filename}' is not a regular file.")

    if filename == "-":
        error(f"Input file must be a regular file.")

    if out_filename != "":
        if exists(out_filename) and not isfile(out_filename):
            error(f"File '{out_filename}' is not a regular file.")

        if not exists(dirname(out_filename)):
            error(f"File parent directory '{out_filename} does not exist.'")

    if media_type(filename) != "audio":
        error("Sorry, no support for formats other than audio :(")
        
    isolator = DeepFilterNetIsolator(chunk_length)
    file = stdout.buffer if out_filename == "" else NamedTemporaryFile(
        "wb", delete=False, suffix=".wav",
    )

    isolator.process(filename, file)    

    if out_filename != "":
        media_convert(file.name, out_filename)


if __name__ == "__main__":
    main()
