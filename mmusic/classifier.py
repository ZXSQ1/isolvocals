from transformers import pipeline
import warnings
import torch

def get_optimal_device():
    """Gets the device for running the model"""
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"

class MusicDetector():
    """Contains functionality to detect music"""
    def __init__(self, model_name, music_labels, device):
        warnings.simplefilter("ignore", UserWarning)

        self.music_labels = music_labels
        self.classifier = pipeline(
            task="audio-classification",
            model=model_name,
            device=device,
        )

    def detect(self, audio_block):
        """Returns the probability of music in a given audio chunk"""
        predictions = self.classifier(audio_block)
        print(predictions)
        exit()
        probability = 0.0
    
        for prediction in predictions:
            if prediction["label"] in self.music_labels:
                probability += prediction["score"]

        return probability 
