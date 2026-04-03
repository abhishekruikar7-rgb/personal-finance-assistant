import streamlit as st
from passlib.hash import pbkdf2_sha256
from .database import add_user, get_user

def hash_password(password):
    return pbkdf2_sha256.hash(password)

def verify_password(password, hashed_password):
    return pbkdf2_sha256.verify(password, hashed_password)

def logout():
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.rerun()

def login_user(username, password):
    user = get_user(username)
    if user and verify_password(password, user[2]):
        st.session_state.authenticated = True
        st.session_state.user_id = user[0]
        st.session_state.username = user[1]
        return True
    return False

def signup_user(username, password):
    hashed_password = hash_password(password)
    if add_user(username, hashed_password):
        st.success("Account created successfully!")
        return True
    else:
        st.error("Username already exists.")
        return False

def check_auth():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    return st.session_state.authenticated
