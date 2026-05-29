from df.enhance import init_df, load_audio, enhance, save_audio
from media import iter_media_segments 
from tqdm import tqdm
from pydub import AudioSegment
from pydub.utils import mediainfo
import env
import numpy as np
import tempfile
import torch


class DeepFilterNetIsolator():
    """The vocals isolator for the DeepFilterNet model"""

    def __init__(self, chunk_length_ms=5000):
        self.model, self.state, _ = init_df(log_level="CRITICAL")
        self.chunk_length_ms = chunk_length_ms

    def process(self, media_filename, outfile):
        """Removes music from the media file and outputs to a given file path 
        or stream (produces a wav 48kHz signed int 16-bit little-endian stereo
        output file)"""

        file = None

        if type(outfile) == str:
            file = open(outfile, 'wb')
        else:
            file = outfile

        segment_filenames, segment_number = iter_media_segments(
            media_filename, self.chunk_length_ms,
        )

        if env.progress:
            segment_filenames = tqdm(
                segment_filenames, "Processing audio", ascii=' -',
                total=segment_number, file=env.logfile,
            )

        frame_rate = 48000

        for segment_filename in segment_filenames:
            audio_tensor, info = load_audio(segment_filename)
            enhanced_audio = enhance(self.model, self.state, audio_tensor)
            save_audio(segment_filename, enhanced_audio, frame_rate)

            audio = AudioSegment.from_file(segment_filename)
            audio.set_channels(2)
            audio.set_frame_rate(frame_rate)
            audio.set_sample_width(2)

            file.write(audio.raw_data)
            file.flush()

        if isinstance(outfile, str):
            file.close()
