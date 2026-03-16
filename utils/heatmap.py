
import plotly.express as px
import pandas as pd

def heatmap(sim):
    df = pd.DataFrame(sim)
    fig = px.imshow(df, color_continuous_scale="Reds", title="Idea Similarity Heatmap")
    return fig
