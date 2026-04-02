from sentence_transformers import SentenceTransformer, util
import torch

class SemanticValidator:
    def __init__(self):
        # Оставляем легкую модель
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # Кеш для хранения вычисленных векторов (эмбеддингов)
        self.embedding_cache = {}

    def get_embedding(self, text: str):
        """Получает вектор текста из кеша или вычисляет его"""
        if text not in self.embedding_cache:
            # Вычисляем вектор и сохраняем в кеш
            self.embedding_cache[text] = self.model.encode(text, convert_to_tensor=True)
        return self.embedding_cache[text]

    def get_similarity(self, text1: str, text2: str) -> float:
        """Сравнивает два текста с использованием кеширования"""
        # Текст бота (всегда разный) — вычисляем
        emb1 = self.model.encode(text1, convert_to_tensor=True)
        # Эталон из YAML (повторяется) — берем из кеша
        emb2 = self.get_embedding(text2)
        
        # Вычисляем косинусное сходство
        cos_sim = util.cos_sim(emb1, emb2)
        return float(cos_sim.item())