from typing import List
import string

class TopicLabeler:
    """Utility class to assign human-readable labels to topics based on keywords."""
    
    # Pre-defined mapping of domains for a tech-focused sentiment app
    DOMAIN_MAPPINGS = {
        "AI & Machine Learning": ["ai", "model", "gpt", "chatgpt", "openai", "machine", "learning", "data", "algorithm"],
        "Customer Support": ["help", "broken", "fix", "issue", "support", "ticket", "bug", "error", "fail"],
        "Pricing & Sales": ["price", "expensive", "cheap", "cost", "sale", "discount", "offer", "money", "subscription"],
        "Community & Events": ["event", "meetup", "community", "join", "team", "webinar", "conference", "talk"],
        "Product Features": ["new", "feature", "update", "release", "version", "launch", "ui", "ux", "design"],
        "Performance": ["fast", "slow", "speed", "lag", "crash", "performance", "optimize", "quick"]
    }

    @classmethod
    def generate_label(cls, keywords: List[str]) -> str:
        """Assigns a category label based on highest keyword overlap, or generates from top words."""
        scores = {category: 0 for category in cls.DOMAIN_MAPPINGS}
        
        for word in keywords:
            for category, mapped_words in cls.DOMAIN_MAPPINGS.items():
                if word.lower().strip(string.punctuation) in mapped_words:
                    scores[category] += 1
                    
        # Find best match
        best_category = max(scores.items(), key=lambda x: x[1])
        
        # If no significant overlap (less than 2 matched words), fallback to top 2-3 words
        if best_category[1] < 2 and len(keywords) >= 2:
            return "-".join(keywords[:3]).title()
            
        return best_category[0]
