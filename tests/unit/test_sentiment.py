import pytest # type: ignore
from src.nlp.sentiment.textblob_analyzer import TextBlobAnalyzer
# We don't extensively unit test BERT here because it requires large models,
# but we test the ensemble logic and fast textblob base.

def test_textblob_analyzer_positive():
    analyzer = TextBlobAnalyzer()
    res = analyzer.analyze("I absolutely love this amazing product!")
    assert res["label"] == "positive"
    assert res["polarity"] > 0
    assert res["confidence"] > 0.5

def test_textblob_analyzer_negative():
    analyzer = TextBlobAnalyzer()
    res = analyzer.analyze("This is the worst experience of my life. Terrible.")
    assert res["label"] == "negative"
    assert res["polarity"] < 0

def test_textblob_analyzer_neutral():
    analyzer = TextBlobAnalyzer()
    res = analyzer.analyze("The color of the box is brown.")
    assert res["label"] == "neutral"
    
def test_textblob_edge_cases():
    analyzer = TextBlobAnalyzer()
    res = analyzer.analyze("")
    assert res["label"] == "neutral"
    assert res["polarity"] == 0.0
