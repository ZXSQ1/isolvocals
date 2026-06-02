from sys import stderr
from isolvocals import env
from rich.live import Live
from rich.progress import Progress, BarColumn, TextColumn


def error(msg):
    env.console.print(f"Error: {msg}")
    exit()


def info(msg):
    if not env.verbose:
        return
    
    env.console.print(msg)


def progress(iterable, total, desc="Processing...", fps=10):
    """Make a progressbar generator out of an iterable."""
    progressbar = Progress(
        TextColumn("{task.description}"), BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
    )

    with Live(progressbar, console=env.console, refresh_per_second=fps):
        task = progressbar.add_task(desc, total=total)

        for item in iterable:
            progressbar.update(task, advance=1)
            yield item

