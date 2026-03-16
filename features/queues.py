
def generate_queue(df):
    return df.sort_values(by=["timestamp","similarity"], ascending=[True,True])
