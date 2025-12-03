import streamlit as st
from utils.similarity import compute_similarity

st.title("🧬 Similarity Analysis")

if "client_df" not in st.session_state:
    st.error("Please upload a file on the main page.")
    st.stop()

client_df = st.session_state["client_df"]

results = compute_similarity(client_df)

st.dataframe(results)
