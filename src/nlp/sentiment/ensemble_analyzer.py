from typing import Dict, Any, List
from .bert_analyzer import BertAnalyzer
from .textblob_analyzer import TextBlobAnalyzer
from src.config import settings
import logging

logger = logging.getLogger(__name__)

class EnsembleAnalyzer:
    """Ensemble approach combining BERT and TextBlob for robustness."""
    
    def __init__(self):
        self.bert = BertAnalyzer()
        self.textblob = TextBlobAnalyzer()
        self.bert_weight = settings.ENSEMBLE_BERT_WEIGHT
        self.tb_weight = settings.ENSEMBLE_TEXTBLOB_WEIGHT
        self.confidence_threshold = 0.6

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze a single text using ensemble approach."""
        tb_res = self.textblob.analyze(text)
        
        # If BERT isn't ready or text is extremely short, fallback completely to TextBlob
        if not self.bert.is_ready or len(text.split()) < 3:
            tb_res["model_used"] = "textblob"
            return tb_res
            
        bert_res = self.bert.analyze(text)
        return self._merge_results(bert_res, tb_res)

    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze a batch of texts robustly."""
        if not texts:
            return []
            
        if not self.bert.is_ready:
            results = []
            for t in texts:
                res = self.textblob.analyze(t)
                res["model_used"] = "textblob"
                results.append(res)
            return results
            
        bert_results = self.bert.analyze_batch(texts)
        final_results = []
        
        for text, bert_res in zip(texts, bert_results):
            tb_res = self.textblob.analyze(text)
            final_results.append(self._merge_results(bert_res, tb_res))
            
        return final_results

    def _merge_results(self, bert_res: Dict[str, Any], tb_res: Dict[str, Any]) -> Dict[str, Any]:
        """Combine results using weighted average for polarity and defined thresholds."""
        
        # If BERT confidence is high, trust it entirely
        if bert_res["confidence"] >= self.confidence_threshold:
            bert_res["model_used"] = "bert_confident"
            return bert_res
            
        # Otherwise, calculate a weighted ensemble polarity
        ensemble_polarity = (bert_res["polarity"] * self.bert_weight) + (tb_res["polarity"] * self.tb_weight)
        
        if ensemble_polarity > 0.05:
            label = "positive"
        elif ensemble_polarity < -0.05:
            label = "negative"
        else:
            label = "neutral"
            
        # Ensemble confidence is combination
        ensemble_confidence = (bert_res["confidence"] * self.bert_weight) + (tb_res["confidence"] * self.tb_weight)
        
        return {
            "label": label,
            "polarity": ensemble_polarity,
            "confidence": ensemble_confidence,
            "model_used": "ensemble"
        }
