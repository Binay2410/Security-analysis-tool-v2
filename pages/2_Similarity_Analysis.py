import streamlit as st
import pandas as pd
from utils.similarity import compute_similarity

st.title("🔍 Similarity Analysis")

if "client_file" not in st.session_state:
    st.error("❌ Please upload a client file from the main page.")
    st.stop()

client_df = pd.read_excel(st.session_state["client_file"])

st.write("Processing similarity comparison...")

results = compute_similarity(client_df)

if results.empty:
    st.info("✔ No similar SGs detected.")
else:
    st.dataframe(results)
