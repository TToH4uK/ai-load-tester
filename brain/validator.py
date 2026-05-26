from sentence_transformers import SentenceTransformer, util
import torch

class SemanticValidator:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_cache = {}

    def get_embedding(self, text: str):
        if text not in self.embedding_cache:
            self.embedding_cache[text] = self.model.encode(text, convert_to_tensor=True)
        return self.embedding_cache[text]

    def get_similarity(self, text1: str, text2: str) -> float:
        emb1 = self.model.encode(text1, convert_to_tensor=True)
        emb2 = self.get_embedding(text2)
        cos_sim = util.cos_sim(emb1, emb2)
        return float(cos_sim.item())