
import click
from tqdm import tqdm
from normal import normalize_audio, get_normalized_audio_chunks
from classifier import MusicDetector, get_optimal_device
from models import get_model, get_model_music_labels
from models import get_model_optimal_audio_length_ms

@click.command()
@click.option("--model", "-m", type=click.Choice([
    "ast", "norwood"]), default="ast",
    help="The model used for music detection.")
@click.option("--simulate", "-s", is_flag=True, default=False,
    help="Print the timestamp ranges where music is detected.")
@click.option("--output-filename", "-o", default="", type=str,
    help="The output filename.")
@click.option("--to-stdout", is_flag=True, default=False,
    help="Prints raw output to standard output.")
@click.argument("filename", type=str, required=True)
def main(model, simulate, output_filename, to_stdout, filename):
    """A script that mutes audio in a file when music is detected."""
    music_probabilities = []
    segment_length_ms = get_model_optimal_audio_length_ms(model)
    overlap_window = segment_length_ms / 3
    detector = MusicDetector(
        get_model(model),
        get_model_music_labels(model),
        get_optimal_device(),
    )

    audio_blocks = tqdm(
        normalize_audio(filename, segment_length_ms, overlap_window),
        desc="Chunks processed",
        total=get_normalized_audio_chunks(filename, segment_length_ms,
            overlap_window)
    )

    for audio_block in audio_blocks:
        music_probabilities.append(detector.detect(audio_block))

    print(music_probabilities)


if __name__ == "__main__":
    main()
