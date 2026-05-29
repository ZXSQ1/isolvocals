from utils import error
from tqdm import tqdm
from os import listdir, path
from tempfile import TemporaryDirectory, NamedTemporaryFile
from json import loads
import subprocess
import env


def media_info(filename):
    """Gets information about the media file"""
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        filename,
    ]

    try:
        proc = subprocess.run(
            cmd, check=True,
            stdin=subprocess.DEVNULL,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        error(f"Media info failed: {e}")

    return loads(proc.stdout.decode())


def cut_media(filename, start_ms, segment_length_ms, out_filename):
    """Cuts a segment from the audio with a specified start and length""" 
    info = media_info(filename)
    duration_ms = int(float(info["format"]["duration"]) * 1000)
    
    if start_ms + segment_length_ms > duration_ms:
        error(f"Unable to cut audio file '{filename}': exceeds audio duration")

    cmd = [
        "ffmpeg",
        "-i", filename,
        "-c", "copy",
        "-ss", str(start_ms / 1000),
        "-t", str(segment_length_ms / 1000),
        "-map_metadata", "0",
        "-y", out_filename,
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


def split_media(filename, segment_length_ms, output_prefix):
    """Splits the given media file by segment length and yields each split
    output filename"""

    info = media_info(filename)
    ext = info["format"]["format_name"]
    ext = "" if ext == "" else f".{ext}"
    duration_ms = int(float(info["format"]["duration"]) * 1000)

    start_ms = 0
    segments = range(0, duration_ms, segment_length_ms)

    for idx, segment_start_ms in enumerate(segments):
        segment_eff_length_ms = segment_length_ms
        segment_text = str(idx).zfill(len(str(len(segments))))
        output_filename = f"{output_prefix}_{segment_text}{ext.lower()}"

        if idx == len(segments) - 1 and segment_start_ms < duration_ms:
            segment_eff_length_ms = duration_ms - segment_start_ms

        cut_media(filename, start_ms, segment_eff_length_ms, output_filename)
        yield output_filename

        start_ms += segment_eff_length_ms


def iter_media_segments(filename, segment_length_ms):
    """Returns a generator of the segment files in the temporary directory to be
    iterated over and the number of segments"""

    with TemporaryDirectory(delete=False) as tmpdir:
        output_prefix = f"{tmpdir}/segment"
        duration_ms = float(media_info(filename)["format"]["duration"]) * 1000
        
        return (
            split_media(filename, segment_length_ms, output_prefix),
            int(duration_ms / segment_length_ms) + \
                1 if duration_ms % segment_length_ms > 0 else 0
        )


def combine_media(out_filename, *audio_filenames, video=False):
    """Combines media files into one continuous file"""
    with NamedTemporaryFile('w', delete=False) as list_file:
        for audio_filename in audio_filenames:
            list_file.write(f"file '{path.abspath(audio_filename)}'\n")

        list_filename = list_file.name

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_filename,
        "-c", "copy",
        "-map_metadata", "0",
        out_filename,
    ]

    if video:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_filename,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-map_metadata", "0",
            out_filename,
        ]

    try:
        subprocess.run(
            cmd, check=True,
            stdout=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as e:
        error(f"Combining failed: {e}")


def add_audio_to_video(out_filename, audio_filename, video_filename):
    """Adds audio to video to output a file"""

    audio_info = media_info(audio_filename)
    video_info = media_info(video_filename)

    if audio_info["format"]["duration"] != video_info["format"]["duration"]:
        error("Audio and video must have same length")

    cmd = [
        "ffmpeg", "-y",
        "-i", video_filename,
        "-i", audio_filename,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-map_metadata", "0",
        "-shortest", out_filename,
    ]

    try:
        subprocess.run(
            cmd, check=True,
            stdout=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as e:
        error(f"Adding audio to video failed: {e}")
