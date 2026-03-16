
from sqlalchemy import create_engine
import pandas as pd
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)

def read(query):
    return pd.read_sql(query, engine)

def write(df, table):
    df.to_sql(table, engine, if_exists="append", index=False)
