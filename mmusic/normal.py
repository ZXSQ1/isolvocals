import numpy as np
from pydub import AudioSegment


def normalize_audio(filename, chunk_duration_ms=1000, overlap_window_ms=500):
    """Yields an array of number, representing the audio file, that is suitable
    for processing with models."""

    audio = AudioSegment.from_file(filename)
    audio.set_frame_rate(16000)
    audio.set_channels(1)

    normalization_factor = 2.0 ** (audio.sample_width * 8 - 1)
    audio_duration_ms = len(audio)
    start_ms = 0

    while start_ms + chunk_duration_ms <= audio_duration_ms:
        chunk = audio[start_ms:start_ms + chunk_duration_ms]
        samples = np.array(chunk.get_array_of_samples())
        samples = samples.astype(np.float32) / normalization_factor

        yield samples
        start_ms += chunk_duration_ms - overlap_window_ms

