import os
import torch
from sentence_transformers import CrossEncoder

# Configuration
MODEL_NAME = "cross-encoder/ms-marco-TinyBERT-L-2"

class ImportanceClassifier:
    def __init__(self):
        print(f"Loading Importance Classifier: {MODEL_NAME}...")
        # Force CPU to avoid MemoryError/CUDA issues in server context for now
        self.device = "cpu" 
        print(f"Using device: {self.device}")
        
        # Load local model (cached in HF_HOME)
        self.model = CrossEncoder(MODEL_NAME, device=self.device)
        print("Importance Classifier loaded successfully.")

    def predict(self, query: str, text: str) -> float:
        """
        Predicts relevance score between a query and text.
        """
        score = self.model.predict([(query, text)])[0]
        # Sigmoid normalization
        import numpy as np
        return 1 / (1 + np.exp(-score))

    def predict_importance(self, text: str) -> float:
        """
        Wrapper for importance scoring.
        """
        return self.predict("Important personal details, names, relationships, life events, or preferences.", text)

    def rerank(self, query: str, memories: list) -> list:
        """
        Reranks a list of memory texts based on relevance to the query.
        Returns list of (score, text) tuples sorted by score.
        """
        if not memories:
            return []
            
        pairs = [(query, m) for m in memories]
        scores = self.model.predict(pairs)
        
        # Sigmoid
        import numpy as np
        scores = 1 / (1 + np.exp(-scores))
        
        # Combine
        results = list(zip(scores, memories))
        results.sort(key=lambda x: x[0], reverse=True)
        return results

# Singleton instance to be used by store
classifier = None

def get_classifier():
    global classifier
    if classifier is None:
        classifier = ImportanceClassifier()
    return classifier
