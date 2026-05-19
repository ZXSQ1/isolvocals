
import click
from normal import normalize_audio


@click.command()
@click.option("--filetype", "-f", type=click.Choice([
    "auto", "mp3", "wav", "ogg", "mp4", "webm"]), default="auto",
    help="The media file's format.")
@click.option("--model", "-m", type=click.Choice([
    "ast", "distilhubert", "whispertiny"]), default="whispertiny",
    help="The model used for music detection.")
@click.option("--simulate", "-s", is_flag=True, default=False,
    help="Print the timestamp ranges where music is detected.")
@click.option("--output-filename", "-o", default="", type=str,
    help="The output filename.")
@click.option("--to-stdout", is_flag=True, default=False,
    help="Prints raw output to standard output.")
@click.argument("filename", type=str, required=True)
def main(filetype, model, simulate, output_filename, to_stdout, filename):
    """A script that mutes audio in a file when music is detected."""
    [print(i) for i in normalize_audio(filename)]


if __name__ == "__main__":
    main()
