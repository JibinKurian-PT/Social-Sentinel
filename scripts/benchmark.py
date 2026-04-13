import time
import sys
import os

# Add root to sys path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.nlp.sentiment.ensemble_analyzer import EnsembleAnalyzer

def run_benchmark():
    """Benchmark sentiment analysis processing time."""
    print("Loading models (may take a moment)...")
    analyzer = EnsembleAnalyzer()
    
    texts = [
        "This product is absolutely amazing! I love everything about it.",
        "Worst experience ever. The customer service was terrible and unhelpful.",
        "The package arrived on Tuesday as expected. The box was brown.",
        "I'm not sure how I feel about this new update. It has some pros and cons.",
        "Absolutely garbage, do not buy this scam!!!",
        "It's okay, nothing special but it gets the job done."
    ]
    
    # Duplicate to make a batch of 120
    batch_texts = texts * 20
    
    print(f"Running benchmark on {len(batch_texts)} texts...")
    
    start = time.time()
    results = analyzer.analyze_batch(batch_texts)
    end = time.time()
    
    elapsed = end - start
    print(f"\n--- Benchmark Results ---")
    print(f"Total time: {elapsed:.2f} seconds")
    print(f"Average time per text: {(elapsed / len(batch_texts) * 1000):.2f} ms")
    print(f"Throughput: {(len(batch_texts) / elapsed):.2f} texts/second")
    print(f"Models used distribution:")
    
    # Count models
    counts = {}
    for r in results:
        m = r.get("model_used", "unknown")
        counts[m] = counts.get(m, 0) + 1
        
    for k, v in counts.items():
        print(f"  {k}: {v}/{len(results)}")

if __name__ == "__main__":
    run_benchmark()
