import bcrypt
import pandas as pd
from database.db import read, write

def hash_pw(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())

def verify_pw(pw, hashed):
    return bcrypt.checkpw(pw.encode(), hashed)

def register_student(username,password,email):

    df = read("SELECT * FROM users")

    if username in df["username"].values:
        return False

    new_user = pd.DataFrame(
        [[username,hash_pw(password),email,"student"]],
        columns=["username","password","email","role"]
    )

    write(new_user,"users")

    return True

def change_password(username,new_pw):

    from database.db import engine
    import sqlalchemy as sa

    hashed = hash_pw(new_pw)

    with engine.begin() as conn:

        conn.execute(
            sa.text(
            "UPDATE users SET password=:pw WHERE username=:u"
            ),
            {"pw":hashed,"u":username}
        )
