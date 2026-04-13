import pytest # type: ignore
from src.nlp.topic_modeling.topic_labeler import TopicLabeler

def test_topic_labeler_exact_match():
    keywords = ["machine", "learning", "data", "ai"]
    label = TopicLabeler.generate_label(keywords)
    assert label == "AI & Machine Learning"

def test_topic_labeler_support():
    keywords = ["ticket", "broken", "help", "fast"]
    label = TopicLabeler.generate_label(keywords)
    assert label == "Customer Support"

def test_topic_labeler_fallback():
    # Words not clearly matching any domain > 1 count
    keywords = ["apple", "banana", "orange"]
    label = TopicLabeler.generate_label(keywords)
    assert label == "Apple-Banana-Orange"
