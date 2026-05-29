from pydub.utils import mediainfo
from utils import error
from tqdm import tqdm
from os import listdir, path
from tempfile import TemporaryDirectory, NamedTemporaryFile
import subprocess
import env


def cut_audio(filename, start_ms, segment_length_ms, out_filename):
    """Cuts a segment from the audio with a specified start and length""" 
    info = mediainfo(filename)
    duration_ms = int(float(info.get("duration", 0)) * 1000)
    
    if start_ms + segment_length_ms > duration_ms:
        error(f"Unable to cut audio file '{filename}': exceeds audio duration")

    cmd = [
        "ffmpeg", 
        "-i", filename,
        "-c", "copy",
        "-ss", str(start_ms / 1000),
        "-t", str(segment_length_ms / 1000),
        "-y", out_filename
    ]

    try:
        subprocess.run(
            cmd, check=True,
            stdout=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as e:
        error(f"Splitting failed: {e}")


def split_audio(filename, segment_length_ms, output_prefix):
    """Splits the given audio file by segment length and yields each split
    output filename"""

    info = mediainfo(filename)
    ext = info.get("format_name", "").lower()
    ext = "" if ext == "" else f".{ext}"
    duration_ms = int(float(info.get("duration", 0)) * 1000)

    start_ms = 0
    segments = range(0, duration_ms, segment_length_ms)

    for idx, segment_start_ms in enumerate(segments):
        segment_eff_length_ms = segment_length_ms
        segment_text = str(idx).zfill(len(str(len(segments))))
        output_filename = f"{output_prefix}_{segment_text}{ext.lower()}"

        if idx == len(segments) - 1 and segment_start_ms < duration_ms:
            segment_eff_length_ms = duration_ms - segment_start_ms

        cut_audio(filename, start_ms, segment_eff_length_ms, output_filename)
        yield output_filename

        start_ms += segment_eff_length_ms


def iter_audio_segments(filename, segment_length_ms):
    """Returns a generator of the segment files in the temporary directory to be
    iterated over and the number of segments"""

    with TemporaryDirectory(delete=False) as tmpdir:
        output_prefix = f"{tmpdir}/segment"
        duration_ms = int(float(mediainfo(filename).get("duration")) * 1000)
        
        return (
            split_audio(filename, segment_length_ms, output_prefix),
            int(duration_ms / segment_length_ms) + \
                1 if duration_ms % segment_length_ms > 0 else 0
        )


def combine_audio(out_filename, *audio_filenames, sr=48000, sample_bytes=2,
    channels=2, filetype='wav', delete=False):

    """Combines audio files into one continuous file"""
    with NamedTemporaryFile('w', delete=False) as list_file:
        for audio_filename in audio_filenames:
            list_file.write(f"file '{path.abspath(audio_filename)}'\n")

        list_filename = list_file.name

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_filename, "-c", "copy", out_filename,
    ]

    try:
        subprocess.run(
            cmd, check=True,
            stdout=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as e:
        error(f"Splitting failed: {e}")


def add_video(out_filename, audio_filename, video_filename):
    pass
