
import streamlit as st
import pandas as pd
from utils.comparator import run_full_comparison
from utils.similarity import compute_similarity_summary
from utils.persistence import load_history

st.set_page_config(page_title="Access AI", layout="wide")

st.title("Access AI – Main Dashboard")

uploaded = st.file_uploader("Upload Client Access Excel", type=["xlsx"])

if uploaded:
    client_df = pd.read_excel(uploaded)
    std_df = pd.read_excel("standard_data.xlsx")

    accepted_risk, update_wd, dup_hist = load_history()

    st.subheader("Findings Summary")
    summary = run_full_comparison(client_df, std_df, accepted_risk, update_wd)
    st.dataframe(summary)

    st.divider()
    st.subheader("Similarity Summary")
    sim_summary = compute_similarity_summary(client_df, dup_hist)
    st.dataframe(sim_summary)

    if st.button("Go to Difference Report"):
        st.switch_page("pages/1_Difference_Report.py")

    if st.button("Go to Similarity Analysis"):
        st.switch_page("pages/2_Similarity_Analysis.py")
else:
    st.info("Upload client file to begin.")
