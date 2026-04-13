import re
import emoji # type: ignore
import nltk # type: ignore
from textblob import TextBlob # type: ignore
from nltk.corpus import stopwords, wordnet # type: ignore
from nltk.stem import WordNetLemmatizer # type: ignore
from typing import List

class NLPPreprocessor:
    """Advanced text preprocessor with emoji handling, spell correction, and lemmatization."""
    
    def __init__(self):
        self.download_nltk_data()
        self.lemmatizer = WordNetLemmatizer()
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.stop_words = set()

    @staticmethod
    def download_nltk_data():
        """Ensure necessary NLTK corpora are downloaded."""
        resources = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'punkt_tab']
        for resource in resources:
            try:
                nltk.download(resource, quiet=True)
            except Exception as e:
                print(f"NLTK download warning for {resource}: {e}")

    def clean_text(self, text: str, spell_correct: bool = False) -> str:
        """
        Comprehensive clean:
        - URL, Mention, Hashtag removal
        - Emoji translation
        - Spell correction (optional, can be slow)
        """
        if not text:
            return ""

        # Demojize
        text = emoji.demojize(text, delimiters=(" ", " "))

        text = text.lower()
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        
        # Remove special chars (excluding spaces)
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', ' ', text)
        
        text = re.sub(r'\s+', ' ', text).strip()
        
        if spell_correct and text:
            try:
                blob = TextBlob(text)
                text = str(blob.correct())
            except Exception:
                pass
                
        return text

    def get_wordnet_pos(self, word: str) -> str:
        """Map POS tag to first character lemmatize() accepts."""
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}
        return tag_dict.get(tag, wordnet.NOUN)

    def tokenize_and_lemmatize(self, text: str, remove_stopwords: bool = True) -> List[str]:
        """Tokenize text, remove stop words, and apply POS-aware lemmatization."""
        cleaned = self.clean_text(text)
        if not cleaned:
            return []
            
        try:
            tokens = nltk.word_tokenize(cleaned)
        except Exception:
            tokens = cleaned.split()

        result = []
        for word in tokens:
            if remove_stopwords and word in self.stop_words:
                continue
            pos = self.get_wordnet_pos(word)
            lemma = self.lemmatizer.lemmatize(word, pos)
            result.append(lemma)
            
        return result
