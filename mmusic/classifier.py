from transformers import pipeline
import torch


def get_optimal_device():
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


class MusicDetector():
    def __init__(self, model_name, music_label, device, music_threshold=0.5):
        self.music_label = music_label
        self.music_threshold = music_threshold
        self.classifier = pipeline(
            task="audio-classification",
            model=model_name,
            device=device,
        )

    def classify(self, audio_block):
        predictions = self.classifier(audio_array)
        print(predictions)
