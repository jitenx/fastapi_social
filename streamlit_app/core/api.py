import requests
import streamlit as st
from core.config import API_BASE_URL
from core.auth import auth_header, logout


def _handle_response(response):
    if response.status_code == 401:
        st.error("Session expired. Please login again.")
        logout()
    response.raise_for_status()
    return response.json() if response.content else None


def get(endpoint):
    response = requests.get(f"{API_BASE_URL}{endpoint}", headers=auth_header())
    return _handle_response(response)


def post(endpoint, payload=None):
    response = requests.post(
        f"{API_BASE_URL}{endpoint}", json=payload, headers=auth_header()
    )
    return _handle_response(response)


def put(endpoint, payload=None):
    response = requests.put(
        f"{API_BASE_URL}{endpoint}", json=payload, headers=auth_header()
    )
    return _handle_response(response)


# def delete(endpoint):
#     response = requests.delete(f"{API_BASE_URL}{endpoint}", headers=auth_header())
#     _handle_response(response)
# core/api.py


def delete(url, data=None):
    return requests.delete(
        API_BASE_URL + url,
        json=data,
        headers=auth_header(),
    )
