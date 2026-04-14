import pytest
import pandas as pd
import os
import shutil
from src.csv_processor.batch_sentiment_analyzer import BatchSentimentAnalyzer
from src.csv_processor.visualization_generator import VisualizationGenerator

# Setup temporary test data directory
TEST_DIR = "tests/temp_csv_test"
os.makedirs(TEST_DIR, exist_ok=True)

@pytest.fixture
def sample_csv():
    path = os.path.join(TEST_DIR, "test_input.csv")
    df = pd.DataFrame({
        "text": ["I love this product", "I hate this product", "It is okay"],
        "category": ["A", "B", "A"],
        "date": ["2023-01-01", "2023-01-02", "2023-01-03"]
    })
    df.to_csv(path, index=False)
    yield path
    # Cleanup after tests
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

def test_batch_analyzer_initialization():
    analyzer = BatchSentimentAnalyzer(model_type="fast")
    assert analyzer.model_type == "fast"
    
def test_visualization_detector():
    df = pd.DataFrame({
        "my_text": ["This is a long sentence that should be detected as text.", "Another long sentence for the test."],
        "my_date": ["2023-01-01", "2023-01-02"],
        "my_cat": ["X", "Y"],
        "my_num": [10.5, 20.2]
    })
    viz = VisualizationGenerator()
    col_types = viz.detect_column_types(df)
    
    assert "my_text" in col_types["text"]
    assert "my_date" in col_types["date"]
    assert "my_cat" in col_types["categorical"]
    assert "my_num" in col_types["numeric"]

def test_summary_statistics():
    df = pd.DataFrame({
        "sentiment_label": ["positive", "negative", "neutral", "positive"],
        "sentiment_polarity": [0.8, -0.8, 0.0, 0.5],
        "sentiment_confidence": [0.9, 0.9, 0.5, 0.8]
    })
    analyzer = BatchSentimentAnalyzer()
    stats = analyzer.generate_summary_statistics(df)
    
    assert stats["total_rows"] == 4
    assert stats["positive"] == 2
    assert stats["negative"] == 1
    assert stats["neutral"] == 1
    assert stats["avg_polarity"] == pytest.approx(0.125)

@pytest.mark.asyncio
async def test_batch_processing_logic(sample_csv):
    # We use 'fast' model for speed in testing
    analyzer = BatchSentimentAnalyzer(model_type="fast")
    
    # Run processing
    results_df = await analyzer.process_csv_file(
        file_path=sample_csv,
        text_column="text",
        batch_size=2
    )
    
    assert len(results_df) == 3
    assert "sentiment_label" in results_df.columns
    assert "sentiment_polarity" in results_df.columns
    # Check if first row is positive
    assert results_df.iloc[0]["sentiment_label"] == "positive"
