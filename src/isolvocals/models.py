from df.enhance import init_df, load_audio, enhance, save_audio
from isolvocals.media import iter_media_segments, extract_pcm, media_info
from tqdm import tqdm
from isolvocals.utils import error
from io import BytesIO
from isolvocals import env
import click
import numpy as np
import tempfile
import wave
import torch


class DeepFilterNetIsolator():
    """The vocals isolator for the DeepFilterNet model."""

    def __init__(self, chunk_length_ms=5000):
        self.model, self.state, _ = init_df(log_level="CRITICAL")
        self.chunk_length_ms = chunk_length_ms

    def process(self, filename, outfile):
        """Removes music from the given WAVE audio file and outputs to a given
        file path  or stream, writes WAVE 48kHz signed int 16-bit little-endian
        stereo to given binary output file."""

        file = open(outfile, "wb") if isinstance(outfile, str) else outfile 
        segment_filenames, segment_number = iter_media_segments(
            filename, self.chunk_length_ms,
        )

        if env.progress:
            segment_filenames = tqdm(
                segment_filenames, desc=env.progress_header, file=env.logfile,
                total=segment_number, ascii=f" {env.progress_char}",
            )

        info = media_info(filename)
        frame_rate = 48000
        nframes = int(float(info["format"]["duration"]) * frame_rate)

        try:
            with wave.open(file, "w") as f:
                f.setnchannels(2)
                f.setsampwidth(2)
                f.setframerate(48000)
                f.setnframes(nframes)

                for segment_filename in segment_filenames:
                    tmp_out_filename = f"{segment_filename}.wav" if \
                        segment_filename.split(".")[-1] != "wav" else \
                        segment_filename
            
                    audio_tensor, info = load_audio(segment_filename)
                    enhanced_audio = enhance(self.model, self.state, audio_tensor)
                    save_audio(tmp_out_filename, enhanced_audio, frame_rate)

                    f.writeframesraw(extract_pcm(tmp_out_filename))
        
        except wave.Error as e:
             error(e)

      
        if isinstance(outfile, str):
            file.close()
