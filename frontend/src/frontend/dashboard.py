import streamlit as st
import httpx
import os


BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

def main():
    st.markdown("# Lunar Eclipse Events ")

    st.write(BASE_URL)

    data = httpx.get(f"{BASE_URL}/lunar/statistics", timeout=30).json()
    st.dataframe(data)

    st.metric("total", data["total_eclipse"])
    st.bar_chart(data["categories"])

if __name__ == "__main__":
    main()