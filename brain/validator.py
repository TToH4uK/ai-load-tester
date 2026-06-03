from fastembed import TextEmbedding
import numpy as np

class SemanticValidator:
    def __init__(self):
        # Using the same fastembed model as main.py for consistency
        self.model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        self.embedding_cache = {}

    def get_embedding(self, text: str):
        if text not in self.embedding_cache:
            self.embedding_cache[text] = list(self.model.embed([text]))[0]
        return self.embedding_cache[text]

    def get_similarity(self, text1: str, text2: str) -> float:
        emb1 = list(self.model.embed([text1]))[0]
        emb2 = self.get_embedding(text2)
        
        # FastEmbed returns normalized embeddings, so dot product is equivalent to cosine similarity
        cos_sim = np.dot(emb1, emb2)
        return float(cos_sim)