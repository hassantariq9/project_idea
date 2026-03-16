
from ai.clustering import cluster_ideas

def topic_explorer(texts):
    labels = cluster_ideas(texts)
    return labels
