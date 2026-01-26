import streamlit as st
import requests
import re

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

LOGIN_URL = "http://127.0.0.1:8000/login"
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


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
    try:
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
    except requests.exceptions.ConnectionError:
        st.error(
            "⚠️ We’re having trouble connecting to the server right now.\n\n"
            "Your login didn’t go through. Please try again in a few moments."
        )
    except requests.exceptions.Timeout:
        st.error(
            "⏱️ The server is taking too long to respond.\n\nPlease try again shortly."
        )
    except requests.exceptions.HTTPError:
        st.error("❌ Login failed. Please check your credentials.")
    except requests.exceptions.RequestException:
        st.error(
            "⚠️ Something went wrong while contacting the server.\n\nPlease try again."
        )


def login_form():
    with st.form("login_form"):
        username = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")
        if submitted:
            if not username or not password:
                st.error("Please enter Email and Password")
            elif not EMAIL_REGEX.match(username):
                st.error("Please enter a valid email address.")

            else:
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
