
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

def similarity_matrix(texts):
    emb = model.encode(texts)
    return cosine_similarity(emb)

def detect_duplicate(new_text, existing_texts, threshold=0.82):
    if len(existing_texts) == 0:
        return False, 0
    emb = model.encode([new_text] + existing_texts)
    sim = cosine_similarity([emb[0]], emb[1:])[0]
    score = sim.max()
    return score > threshold, float(score)
