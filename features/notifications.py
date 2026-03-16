
import pandas as pd
from database.db import write, read

def notify(user, message):
    df = pd.DataFrame([[user, message]], columns=["user","message"])
    write(df, "notifications")

def get_notifications(user):
    try:
        return read(f"SELECT * FROM notifications WHERE user='{user}'")
    except:
        return pd.DataFrame(columns=["user","message"])
