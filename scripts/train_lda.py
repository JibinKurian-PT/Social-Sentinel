import asyncio
import sys
import os

# Add root to sys path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.nlp.topic_modeling.lda_model import LDA_TopicModel

def train_lda():
    """Manual script to train LDA on dummy data if DB is missing."""
    print("Initializing LDA Model...")
    lda = LDA_TopicModel(num_topics=3)
    
    # Dummy documents
    docs = [
        "Artificial intelligence is transforming the software industry. Machine learning models like GPT are very smart.",
        "I need help with my customer support ticket. The system is broken and I cannot login.",
        "The new pricing model is too expensive. I want a discount or I will cancel my subscription.",
        "AI algorithms and data science are the future of tech. Neural networks are very powerful.",
        "Customer service hasn't replied to my email. Please fix this issue immediately. Very frustrating.",
        "Can we get a sale on the annual subscription? The cost is too high for indie developers.",
        "Using machine learning for data processing is efficient. AI is great.",
        "The app crashed again. I submitted a bug report. Support team is slow.",
        "How much money does this cost? I like the product but the price is steep."
    ]
    
    print("Training...")
    result = lda.train(docs, passes=20)
    print(f"Training result: {result}")
    
    if result["status"] == "success":
        lda.save_model()
        print("Model saved to models/ directory.")

if __name__ == "__main__":
    train_lda()
