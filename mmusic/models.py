
def get_model(acronym) -> str:
    """Converts the user-selected model into the actual model identifier"""
    if acronym == "ast":
        return "MIT/ast-finetuned-audioset-10-10-0.4593"
    elif acronym == "silerovad":
        return "onnx-community/silero-vad"

def get_model_music_labels(acronym) -> list[str]:
    """Gets the labels for music detection of a given model"""
    if acronym == "ast":
        return ["Music"]
    elif acronym == "silerovad":
        return ["noise"]

def get_model_optimal_audio_length_ms(acronym) -> int:
    """Gets the optimal audio chunk length for a given model"""
    if acronym == "ast":
        return 10000
    elif acronym == "silerovad":
        return 30

def get_model_music_threshold(acronym) -> float:
    """Gets the threshold probability for music for a given model"""
    if acronym == "silerovad":
        return 0.5
