from isolvocals.utils import error
from os import listdir, path
from tempfile import TemporaryDirectory, NamedTemporaryFile
from json import loads
from sys import stderr
from isolvocals import env
import subprocess


def run_proc(cmd, err_msg):
    """General function to run ffmpeg processes, returning command output and
    exitting on errors."""
    try:
        proc = subprocess.run(
            cmd, check=True,
            stdin=subprocess.DEVNULL,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        error(f"{err_msg}: {e}")

    return proc


def media_info(filename):
    """Gets information about the media file."""
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json", "-show_format",
        "-show_streams", filename,
    ]

    proc = run_proc(cmd, "Media info failed")
    return loads(proc.stdout.decode())


def extract_pcm(filename, sr=48000, chan=2, forma_t="s16le", codec="pcm_s16le"):
    """Extracts PCM with given options and returns bytes."""
    cmd = [
        "ffmpeg", "-y", "-i", filename, "-ar", str(sr), "-ac", str(chan),
        "-f", forma_t, "-acodec", codec, "pipe:1",
    ]

    return run_proc(cmd, "Extracting PCM failed").stdout


def media_convert(filename, out_filename):
    cmd = [
        "ffmpeg", "-y", "-i", filename, out_filename,
    ]

    return run_proc(cmd, "Conversion failed")


def from_pcm(filename, sr=48000, chan=2, pcm_format="s16le", forma_t="wav"): 
    """Converts PCM to certain format and returns bytes."""

    cmd = [
        "ffmpeg", "-y", "-f", forma_t, "-ar", str(sr), "-ac", chan,
        "-i", filename, "pipe:1", "-f", forma_t,
    ]

    return run_proc(cmd, err_msg).stdout


def cut_media(filename, start_ms, segment_length_ms, out_filename):
    """Cuts a segment from the audio with a specified start and length.""" 
    info = media_info(filename)
    duration_ms = int(float(info["format"]["duration"]) * 1000)
    
    if start_ms + segment_length_ms > duration_ms:
        error(f"Unable to cut audio file '{filename}': exceeds audio duration")

    cmd = [
        "ffmpeg", "-y", "-i", filename, "-c", "copy",
        "-ss", str(start_ms / 1000), "-t", str(segment_length_ms / 1000),
        "-map_metadata", "0", out_filename,
    ]

    run_proc(cmd, "Cutting media file failed")


def split_media(filename, segment_length_ms, output_prefix):
    """Splits the given media file by segment length and yields each split
    output filename."""

    info = media_info(filename)
    filename_ext = filename.split(".")[-1]
    exts = info["format"]["format_name"].split(",")
    ext = filename_ext if filename_ext in exts else exts.split(",")[0]
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
    iterated over and the number of segments."""

    with TemporaryDirectory(delete=False) as tmpdir:
        output_prefix = f"{tmpdir}/segment"
        duration_ms = float(media_info(filename)["format"]["duration"]) * 1000
        
        return (
            split_media(filename, segment_length_ms, output_prefix),
            int(duration_ms / segment_length_ms) + \
                1 if duration_ms % segment_length_ms > 0 else 0
        )


def combine_media(out_filename, *audio_filenames, video=False):
    """Combines media files into one continuous file."""
    with NamedTemporaryFile('w', delete=False) as list_file:
        for audio_filename in audio_filenames:
            list_file.write(f"file '{path.abspath(audio_filename)}'\n")

        list_filename = list_file.name

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_filename,
        "-c", "copy", "-map_metadata", "0", out_filename,
    ]

    if video:
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_filename,
            "-c:v", "libx264", "-c:a", "aac", "-map_metadata", "0",
            out_filename,
        ]

    run_proc(cmd, "Combining media files failed") 


def add_audio_to_video(out_filename, audio_filename, video_filename):
    """Adds audio to video to output a file."""

    audio_info = media_info(audio_filename)
    video_info = media_info(video_filename)

    if audio_info["format"]["duration"] != video_info["format"]["duration"]:
        error("Audio and video must have same length")

    cmd = [
        "ffmpeg", "-y", "-i", video_filename, "-i", audio_filename,
        "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0",
        "-map_metadata", "0", "-shortest", out_filename,
    ]

    run_proc(cmd, "Adding audio to video failed")


def extract_media(filename, out_filename, isolate="video"):
    """Extracts audio or video from a media file; 'isolate' parameter can either
    be 'video' or 'audio'."""

    if isolate not in ["video", "audio"]:
        error("Can only extract 'audio' or 'video' from a media file: invalid "
            "'isolate' parameter value")

    cmd = [
        "ffmpeg", "-y", "-i", filename, "-map", "0:a:0", "-map", "0:m:?",
        output_filename,
    ]

    if isolate == "video":
        cmd = [
            "ffmpeg", "-y", "-i", filename, "-map", "0:v", "-map", "0:s?",
            "-map", "0:t?", "-c", "copy", out_filename,
        ]

    run_proc(cmd, "Extracting audio/video failed")


def media_type(filename):
    """Returns 'video' if the media file is a video, 'audio' if it is an audio,
    'unknown' if it is not recognizable."""
    info = media_info(filename)
    codecs = []

    for stream in info["streams"]:
        codecs.append(stream["codec_type"])

    if "video" in codecs and "audio" in codecs:
        return "video"
    elif "audio" in codecs:
        return "audio"
    else:
        return "unknown"
