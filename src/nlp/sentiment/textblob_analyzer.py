from textblob import TextBlob # type: ignore
from typing import Dict, Any

class TextBlobAnalyzer:
    """Fast lexicon-based sentiment analysis."""
    
    def analyze(self, text: str) -> Dict[str, Any]:
        if not text.strip():
            return {"label": "neutral", "polarity": 0.0, "confidence": 1.0}
            
        try:
            blob = TextBlob(text)
            polarity = float(blob.sentiment.polarity)
            subjectivity = float(blob.sentiment.subjectivity)
            
            # Confidence is derived loosely from subjectivity and extremity of polarity
            confidence = min(1.0, (abs(polarity) + subjectivity) / 2.0)
            if confidence == 0:
                confidence = 0.5 # Default confidence for neutral/objective statements
                
            if polarity > 0.05:
                label = "positive"
            elif polarity < -0.05:
                label = "negative"
            else:
                label = "neutral"
                
            return {
                "label": label,
                "polarity": polarity,
                "confidence": confidence
            }
        except Exception:
            return {"label": "neutral", "polarity": 0.0, "confidence": 0.1}
