
def get_model(acronym):
    if acronym == "ast":
        return "MIT/ast-finetuned-audioset-10-10-0.4593"
    elif acronym == "distilhubert":
        return "sanchit-gandhi/distilhubert-finetuned-gtzan"
    elif acronym == "whispertiny":
        return "vineetsharma/whisper-tiny-finetuned-gtzan"
