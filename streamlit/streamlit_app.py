import os

import requests
from dotenv import load_dotenv

import streamlit as st

load_dotenv()


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
CHAT_URL = f"{BASE_URL}/get-chat"


def chat(user_input: str):
    user_input = f"Is {user_input} a good investment choice right now?"
    payload = {"user_input": user_input}
    response = requests.post(
        CHAT_URL,
        json=payload
    )

    return response


st.title("Stock Recommendation Agent")
user_input = st.text_input("Enter Stock Ticker", "AAPL")

if st.button("Get Stock Recommendation"):
    try:
        chat_response = chat(user_input)
        if chat_response is None:
            st.error("Error getting the agent response")
        else:
            st.write("Agent Response:")
            st.markdown(chat_response)

    except Exception as e:
        st.error(f"Error running the agent: {e}")
