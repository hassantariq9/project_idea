
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
from config import CLUSTERS

model = SentenceTransformer("all-MiniLM-L6-v2")

def cluster_ideas(texts):
    emb = model.encode(texts)
    kmeans = KMeans(n_clusters=CLUSTERS, random_state=0)
    labels = kmeans.fit_predict(emb)
    return labels
