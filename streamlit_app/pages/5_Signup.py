import streamlit as st
import requests
import json
from core.config import API_BASE_URL,USERS_ENDPOINT
from core.validators import valid_email
from core.auth import is_authenticated

if is_authenticated():
    st.switch_page("pages/1_All_Posts.py")
else:
    st.title("Sign Up")

    with st.form("signup"):
        first = st.text_input("First Name")
        last = st.text_input("Last Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Create Account")

    if submit:
        if not all([first, last, email, password]):
            st.error("All fields required")
        elif not valid_email(email):
            st.error("Invalid email")
        else:
            response = requests.post(
                f"{API_BASE_URL}{USERS_ENDPOINT}",
                data=json.dumps({
                    "first_name": first,
                    "last_name": last,
                    "email": email,
                    "password": password
                })
            )

            if response.status_code == 201:
                st.success("Account created 🎉")
                st.switch_page("app.py")
            else:
                st.error(response.json().get("detail", "Signup failed"))