import nltk
import spacy
from spacy.cli import download
from sentence_transformers import SentenceTransformer

def ensure_nltk_spacy_resources():
    """Ensure required NLTK and spaCy resources are available."""
    nltk_resources = [
        'stopwords',
        'punkt',
        'punkt_tab',
        'averaged_perceptron_tagger',
        'averaged_perceptron_tagger_eng'
    ]
    
    for resource in nltk_resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            nltk.download(resource, quiet=True)
    
    # Ensure spaCy models are downloaded
    spacy_models = ['en_core_web_sm', 'en_core_web_md']
    
    for model in spacy_models:
        try:
            spacy.load(model)
        except OSError:
            download(model) #spacy cli download

def ensure_sentence_transformer(model_name="paraphrase-MiniLM-L3-v2"):
    try:
        SentenceTransformer(model_name)  # This loads it; if not found, it downloads
    except Exception:
        print(f"Downloading Sentence Transformer model: {model_name}")
        SentenceTransformer(model_name)  # Try downloading again


ensure_sentence_transformer()
ensure_nltk_spacy_resources()