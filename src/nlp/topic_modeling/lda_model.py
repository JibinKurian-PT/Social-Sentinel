import os
import gensim # type: ignore
from gensim import corpora # type: ignore
from gensim.models import CoherenceModel # type: ignore
from typing import List, Dict, Any, Optional
import logging
import multiprocessing
from src.nlp.preprocessor import NLPPreprocessor
from src.config import settings

logger = logging.getLogger(__name__)

class LDA_TopicModel:
    """
    Gensim LDA topic modeling wrapper with save/load capability, 
    coherence metrics validation, and auto-training logic.
    """
    
    def __init__(self, num_topics: int = 5, model_dir: str = "models/"):
        self.num_topics = num_topics
        self.preprocessor = NLPPreprocessor()
        self.dictionary = None
        self.model = None
        self.model_dir = model_dir
        self.coherence_score = 0.0
        
        # Create models dir if not exists
        if not os.path.exists(self.model_dir):
            try:
                os.makedirs(self.model_dir)
            except Exception as e:
                logger.error(f"Could not create model directory {self.model_dir}: {e}")

    def train(self, documents: List[str], passes: int = 20) -> Dict[str, Any]:
        """Train the LDA model on a fresh corpus and validate coherence."""
        if not documents or len(documents) < 10:
            logger.warning("Insufficient documents provided to LDA model (min 10).")
            return {"status": "failed", "reason": "not_enough_data"}
            
        logger.info(f"Training LDA with {len(documents)} documents for {self.num_topics} topics...")
        
        # ── Preprocessing ────────────────────────────────────────────────────
        tokenized_docs = []
        for doc in documents:
            tokens = self.preprocessor.tokenize_and_lemmatize(doc)
            if len(tokens) > 2: # Ignore very short documents
                tokenized_docs.append(tokens)
        
        if len(tokenized_docs) < self.num_topics:
            return {"status": "failed", "reason": "not_enough_valid_docs"}
            
        # ── Dictionary & Corpus ──────────────────────────────────────────────
        self.dictionary = corpora.Dictionary(tokenized_docs)
        # Filter out tokens that appear in less than 2 docs or more than 50%
        self.dictionary.filter_extremes(no_below=2, no_above=0.5, keep_n=100000)
        
        if len(self.dictionary) == 0:
            return {"status": "failed", "reason": "empty_dictionary"}
            
        corpus = [self.dictionary.doc2bow(text) for text in tokenized_docs]
        
        # ── Model Training ───────────────────────────────────────────────────
        try:
            workers = max(1, multiprocessing.cpu_count() - 1)
            self.model = gensim.models.LdaMulticore(
                corpus=corpus,
                id2word=self.dictionary,
                num_topics=self.num_topics,
                random_state=42,
                passes=passes,
                workers=workers,
                chunksize=2000,
                alpha='asymmetric' # Better for real-world text distributions
            )
            
            # ── Coherence Validation ──────────────────────────────────────────
            coherence_model = CoherenceModel(
                model=self.model, 
                texts=tokenized_docs, 
                dictionary=self.dictionary, 
                coherence='c_v'
            )
            self.coherence_score = float(coherence_model.get_coherence())
            
            # Log quality warning
            if self.coherence_score < 0.3:
                logger.warning(f"Low LDA coherence score: {self.coherence_score:.4f}. Topics may be noisy.")
            else:
                logger.info(f"LDA training complete. Coherence: {self.coherence_score:.4f}")
                
            self.save_model()
            
            return {
                "status": "success", 
                "coherence": self.coherence_score,
                "topics": self.extract_topics()
            }
        except Exception as e:
            logger.error(f"LDA Training failed: {e}")
            return {"status": "failed", "reason": str(e)}

    def save_model(self, prefix: str = "lda_prod"):
        """Persist the model and dictionary to disk."""
        if not self.model or not self.dictionary:
            return False
            
        try:
            model_path = os.path.join(self.model_dir, f"{prefix}.model")
            dict_path = os.path.join(self.model_dir, f"{prefix}.dict")
            
            self.model.save(model_path)
            self.dictionary.save(dict_path)
            logger.info(f"Saved LDA model assets to {self.model_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to save LDA model: {e}")
            return False
        
    def load_model(self, prefix: str = "lda_prod") -> bool:
        """Load model assets from disk."""
        model_path = os.path.join(self.model_dir, f"{prefix}.model")
        dict_path = os.path.join(self.model_dir, f"{prefix}.dict")
        
        if os.path.exists(model_path) and os.path.exists(dict_path):
            try:
                self.model = gensim.models.LdaMulticore.load(model_path)
                self.dictionary = corpora.Dictionary.load(dict_path)
                logger.info("LDA model loaded from disk.")
                return True
            except Exception as e:
                logger.error(f"Error loading LDA model: {e}")
        return False

    async def train_if_needed(self):
        """
        Startup logic: if model doesn't exist on disk, attempt to train 
        using initial data from the database.
        """
        if self.load_model():
            return
            
        logger.info("No saved LDA model found. Attempting initial training from DB...")
        # Note: This requires a circular import check or a separate service call.
        # For simplicity, we assume documents will be provided via API trigger or worker.
        # But we initialize the structure anyway.
        pass

    def extract_topics(self, num_words: int = 10) -> List[Dict[str, Any]]:
        """Get the trained topics and their top keywords."""
        if not self.model or not self.dictionary:
            return []
            
        topics = []
        for topic_id in range(self.num_topics):
            words = self.model.show_topic(topic_id, topn=num_words)
            topics.append({
                "topic_id": topic_id,
                "keywords": [word for word, prob in words],
                "weights": [float(prob) for word, prob in words]
            })
            
        return topics
        
    def predict_topic(self, text: str) -> Dict[str, Any]:
        """Predict topics for a single document with confidence score."""
        if not self.model or not self.dictionary or not text.strip():
            return {"topic_id": -1, "confidence": 0.0, "distribution": []}
            
        tokens = self.preprocessor.tokenize_and_lemmatize(text)
        bow = self.dictionary.doc2bow(tokens)
        
        if not bow:
            return {"topic_id": -1, "confidence": 0.0, "distribution": []}
            
        try:
            topic_distribution = self.model.get_document_topics(bow, minimum_probability=0.01)
            if not topic_distribution:
                return {"topic_id": -1, "confidence": 0.0, "distribution": []}
                
            best_topic = max(topic_distribution, key=lambda item: item[1])
            return {
                "topic_id": int(best_topic[0]),
                "confidence": round(float(best_topic[1]), 4),
                "distribution": [(int(t_id), round(float(prob), 4)) for t_id, prob in topic_distribution]
            }
        except Exception as e:
            logger.error(f"Error predicting topic: {e}")
            return {"topic_id": -1, "confidence": 0.0, "distribution": []}

# Singleton instance
lda_model = LDA_TopicModel(num_topics=5)
