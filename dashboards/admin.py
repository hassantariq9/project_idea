import streamlit as st
from auth.auth import change_password
from database.db import read

def admin_dashboard():

    st.title("Admin Panel")

    st.subheader("Users")

    df = read("SELECT username,email,role FROM users")

    st.dataframe(df)

    st.subheader("Change Password")

    user = st.text_input("Username")
    new_pw = st.text_input("New Password",type="password")

    if st.button("Update Password"):

        change_password(user,new_pw)

        st.success("Password updated")
