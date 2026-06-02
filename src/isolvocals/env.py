from sys import stderr
from rich import console

verbose = True
progress = True
progress_header = "Processing audio chunks"
console = console.Console(file=stderr)

dependencies = ["ffmpeg", "ffprobe"]
