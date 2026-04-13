import torch # type: ignore
import torch.nn.functional as F # type: ignore
from transformers import AutoTokenizer, AutoModelForSequenceClassification # type: ignore
from typing import List, Dict, Any, Optional
from functools import lru_cache
from src.config import settings
import logging
import os

logger = logging.getLogger(__name__)

class BertAnalyzer:
    """
    HuggingFace BERT model for high-accuracy sentiment analysis.
    Supports CUDA, MPS (Apple Silicon), and CPU.
    """
    
    _instance = None
    
    def __new__(cls):
        # Singleton pattern
        if cls._instance is None:
            cls._instance = super(BertAnalyzer, cls).__new__(cls)
            cls._instance.initialized = False
            cls._instance.is_ready = False
            cls._instance.model = None
            cls._instance.tokenizer = None
            cls._instance.device = torch.device("cpu")
        return cls._instance
        
    def __init__(self):
        # Parameters initialization only. Model loading is separate.
        self.model_name = settings.BERT_MODEL_NAME
        self.initialized = True

    def load_model(self):
        """Heavy model loading. Should be called during startup lifespan."""
        if self.is_ready:
            return
            
        logger.info(f"Loading BERT Sentiment Model: {self.model_name}")
        
        # ── Device Detection ─────────────────────────────────────────────────
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")
            
        logger.info(f"BERT using device: {self.device}")
        
        # ── Model Loading ────────────────────────────────────────────────────
        try:
            cache_dir = settings.HF_HOME if os.path.exists(settings.HF_HOME) else None
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, cache_dir=cache_dir)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name, cache_dir=cache_dir)
            self.model.to(self.device)
            self.model.eval()
            self.labels = ["negative", "neutral", "positive"]
            self.is_ready = True
            logger.info("BERT Sentiment Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load BERT model '{self.model_name}': {e}")
            self.is_ready = False

    @lru_cache(maxsize=1000)
    def _analyze_single_cached(self, text: str) -> Dict[str, Any]:
        return self.analyze_batch([text])[0]

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze a single string with LRU caching."""
        if not text or not text.strip():
            return {"label": "neutral", "polarity": 0.0, "confidence": 0.0}
            
        if not self.is_ready:
            # On-demand loading if not initialized via lifespan (for fallback)
            self.load_model()
            
        if not self.is_ready:
            return {"label": "neutral", "polarity": 0.0, "confidence": 0.0}
            
        return self._analyze_single_cached(text.strip())

    def analyze_batch(self, texts: List[str], batch_size: int = 32) -> List[Dict[str, Any]]:
        """Process texts in efficiently sized batches."""
        if not texts:
            return []
            
        if not self.is_ready:
            self.load_model()
            
        if not self.is_ready:
            return [{"label": "neutral", "polarity": 0.0, "confidence": 0.0} for _ in texts]
            
        results = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            try:
                encoded_input = self.tokenizer(
                    batch_texts, 
                    return_tensors='pt', 
                    padding=True, 
                    truncation=True, 
                    max_length=512
                ).to(self.device)
                
                with torch.no_grad():
                    output = self.model(**encoded_input)
                    
                scores = F.softmax(output.logits, dim=1).cpu().numpy()
                
                for j in range(len(batch_texts)):
                    max_idx = int(scores[j].argmax())
                    confidence = float(scores[j][max_idx])
                    polarity = float(scores[j][2] - scores[j][0])
                    results.append({
                        "label": self.labels[max_idx],
                        "polarity": round(polarity, 4),
                        "confidence": round(confidence, 4)
                    })
            except Exception as e:
                logger.error(f"Error during BERT batch processing: {e}")
                results.extend([{"label": "neutral", "polarity": 0.0, "confidence": 0.0} for _ in batch_texts])
                
        return results

# Singleton instance
bert_analyzer = BertAnalyzer()
