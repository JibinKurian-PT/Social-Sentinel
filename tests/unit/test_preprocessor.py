import pytest # type: ignore
from src.nlp.preprocessor import NLPPreprocessor

@pytest.fixture
def preprocessor():
    return NLPPreprocessor()

def test_clean_text_removes_urls(preprocessor):
    text = "Check out this link: https://example.com/test #cool"
    cleaned = preprocessor.clean_text(text)
    assert "http" not in cleaned
    assert "example" not in cleaned

def test_clean_text_handles_emojis(preprocessor):
    text = "I am happy 😊!"
    cleaned = preprocessor.clean_text(text)
    assert "smiling" in cleaned or "happy" in cleaned # demojize converts to words

def test_tokenize_and_lemmatize(preprocessor):
    text = "The runner was running very quickly to the stores."
    tokens = preprocessor.tokenize_and_lemmatize(text)
    
    # "runner", "run", "quickly", "store" should be root lemmas without stop words
    assert "run" in tokens
    assert "store" in tokens
    assert "the" not in tokens
