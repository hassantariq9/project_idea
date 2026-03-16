
import bcrypt
from database.db import read, write
import pandas as pd

def hash_pw(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())

def verify_pw(pw, hashed):
    return bcrypt.checkpw(pw.encode(), hashed)

def create_default_users():
    try:
        read("SELECT * FROM users")
    except:
        df = pd.DataFrame([
            ["student1", hash_pw("student123"), "student"],
            ["faculty1", hash_pw("faculty123"), "faculty"]
        ], columns=["username","password","role"])
        write(df,"users")

def login(username,password):
    df = read("SELECT * FROM users")
    user = df[df["username"]==username]
    if len(user)==0:
        return None
    hashed = user.iloc[0]["password"]
    role = user.iloc[0]["role"]
    if verify_pw(password, hashed):
        return role
    return None
