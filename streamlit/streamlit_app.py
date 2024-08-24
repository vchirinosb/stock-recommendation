import requests

import streamlit as st
# from app.core.config import settings

st.title("Stock Recommendation Agent")


user_input = st.text_input("Enter Stock Ticker", "AAPL")

if st.button("Get Stock Recommendation"):
    try:

        url = "http://localhost:8000/get-recommendation"
        payload = {"user_input": user_input}
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            result = response.json()
            if "response" in result:
                st.write("Agent Response:")
                st.write(result["response"])
            else:
                st.error(
                    "Error: " + result.get("error", "Unknown error occurred")
                )
        else:
            st.error(f"Error: {response.status_code}")

    except Exception as e:
        st.error(f"Error running the agent: {e}")
