import logging
import warnings
import env
logging.basicConfig(stream=env.logfile, level=logging.INFO)
warnings.simplefilter("ignore", UserWarning)

from models import DeepFilterNetIsolator
from sys import stdout
import click


@click.command()
@click.option("--model", "-m", type=click.Choice([
    "ast", "silerovad"]), default="ast",
    help="The model used for music detection.")
@click.option("--simulate", "-s", is_flag=True, default=False,
    help="Print the timestamp ranges where music is detected.")
@click.option("--output-filename", "-o", default="", type=str,
    help="The output filename.")
@click.option("--to-stdout", is_flag=True, default=False,
    help="Prints raw output to standard output.")
@click.argument("filename", type=str, required=True)
def main(model, simulate, output_filename, to_stdout, filename):
    """A terminal tool for playing media music-free."""
    pass


if __name__ == "__main__":
    main()
