# streamlit_app.py
import streamlit as st
import requests
import json
import re
import time

if st.session_state.get("authenticated"):
    st.switch_page("pages/All_Posts.py")

# The API URL
api_url = "http://127.0.0.1:8000/users/"


EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

st.title("Sign up form")
form_values = {
    "first_name": None,
    "last_name": None,
    "email": None,
    "password": None,
    "phone_number": None,
    "address": None,
}
with st.form(key="User Signup Form"):
    form_values["first_name"] = st.text_input("First Name", placeholder="John")
    form_values["last_name"] = st.text_input("Last Name", placeholder="Doe")
    form_values["email"] = st.text_input(
        "Email ID", placeholder="e.g, user@example.com"
    )
    form_values["password"] = st.text_input("Password", type="password")
    # form_values["phone_number"] = st.text_input(
    #     "Phone Number", placeholder="e.g., +12223334444"
    # )
    # form_values["address"] = st.text_area("Address")

    submit_button = st.form_submit_button()

    if submit_button:
        if not form_values["first_name"]:
            st.error("Please enter first name")
        elif not form_values["last_name"]:
            st.error("Please enter last name")
        elif not form_values["email"]:
            st.error("Please enter email")
        elif not EMAIL_REGEX.match(form_values["email"]):
            st.error("Please enter a valid email address.")
        elif not form_values["password"]:
            st.error("Please enter password")
        # elif not form_values["phone_number"]:
        #     st.error("Please enter phone number")
        # elif not form_values["address"]:
        #     st.error("Please enter address")
        else:
            try:
                response = requests.post(url=api_url, data=json.dumps(form_values))
                json_data = response.json()
                if response.status_code == 201:
                    st.success("User Created succesfully.")
                    # st.info(f"""
                    # Email: {json_data["email"]} \n
                    # Name: {json_data["first_name"]} {json_data["last_name"]}
                    # """)
                    with st.spinner("Please wait..."):
                        time.sleep(2)
                    st.switch_page("app.py")
                if response.status_code == 406:
                    st.error(json_data["detail"])
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
