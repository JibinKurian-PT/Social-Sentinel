import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_sample_csv(output_path="data/raw/sample_data.csv"):
    """
    Generates a sample CSV with varied sentiments, dates, and categories for testing.
    """
    np.random.seed(42)
    
    # 1. Sample Texts per Category
    samples = {
        "product": [
            "This new model is absolutely incredible!",
            "I'm really disappointed with the build quality.",
            "It's okay, but I expected more for the price.",
            "Best purchase I've made this year. High quality.",
            "The screen cracked after just one day of use. Terrible."
        ],
        "service": [
            "Customer support was helpful and resolved my issue.",
            "Wait times are way too long. I stayed on hold for an hour.",
            "Friendly staff and very quick response times.",
            "They ignored my email for a week. Very unprofessional.",
            "The technician arrived on time and fixed everything."
        ],
        "shipping": [
            "Arrived 3 days earlier than expected! Awesome service.",
            "The box was completely crushed when it arrived.",
            "Still waiting for my package. It's been two weeks.",
            "Fast delivery and great packaging. Zero complaints.",
            "Delivery driver left it in the rain. Not happy."
        ],
        "pricing": [
            "Great value for money. Highly recommended.",
            "Too expensive for what you get. Will look for alternatives.",
            "The discount made it a steal! Happy with my purchase.",
            "Hidden fees were added at checkout. Feels dishonest.",
            "Reasonable pricing compared to other brands."
        ]
    }
    
    categories = list(samples.keys())
    locations = ["New York", "London", "San Francisco", "Tokyo", "Berlin", "Dubai", "Sydney"]
    
    data = []
    end_date = datetime.now()
    
    # 2. Generate 1000 rows
    for i in range(1000):
        category = np.random.choice(categories)
        text = np.random.choice(samples[category])
        
        # Add some random noise/users
        user_id = f"user_{np.random.randint(1000, 9999)}"
        location = np.random.choice(locations)
        
        # Generate random date within last 30 days
        days_ago = np.random.randint(0, 30)
        hours_ago = np.random.randint(0, 24)
        date = end_date - timedelta(days=days_ago, hours=hours_ago)
        
        data.append({
            "id": i,
            "timestamp": date.strftime("%Y-%m-%d %H:%M:%S"),
            "user": user_id,
            "text": text,
            "category": category,
            "location": location,
            "followers": np.random.randint(10, 5000)
        })
    
    df = pd.DataFrame(data)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"✅ Success! Sample CSV generated at: {output_path}")
    print(f"Summary: 1000 rows across categories: {', '.join(categories)}")

if __name__ == "__main__":
    generate_sample_csv()
