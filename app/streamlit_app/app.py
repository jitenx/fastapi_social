import streamlit as st
import requests

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

LOGIN_URL = "http://127.0.0.1:8000/login"

st.title("Login")


def login(username, password):
    payload = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": "string",
    }

    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    response = requests.post(LOGIN_URL, data=payload, headers=headers)

    if response.status_code == 201:
        token_data = response.json()
        st.success("Login successful")

        # Save token in session state
        st.session_state["access_token"] = token_data["access_token"]
        st.session_state["authenticated"] = True
        # st.json(token_data)
        st.switch_page("pages/All_Posts.py")

    else:
        data = response.json()
        st.error("Login failed")
        st.text(data["detail"])


def login_form():
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")
        if submitted:
            login(username, password)


if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login_form()
else:
    st.switch_page("pages/All_Posts.py")


st.write("Don’t have an account?")
if st.button("Create account"):
    st.switch_page("pages/Signup.py")
