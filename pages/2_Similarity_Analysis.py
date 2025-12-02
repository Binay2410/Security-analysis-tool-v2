
import streamlit as st
import pandas as pd
from utils.similarity import compute_similarity_report
from utils.persistence import load_history

st.title("Security Group Similarity Analysis")

st.session_state.setdefault("client_df", None)

if st.session_state.client_df is None:
    st.error("Upload a file on the main page first.")
else:
    _, _, dup_hist = load_history()
    sim = compute_similarity_report(st.session_state.client_df, dup_hist)
    st.dataframe(sim)
