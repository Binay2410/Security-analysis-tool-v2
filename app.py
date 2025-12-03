import streamlit as st
import pandas as pd

from utils.helpers import normalize_dataframe
from utils.comparator import compute_differences
from utils.similarity import compute_similarity

st.set_page_config(
    page_title="Security Group Analysis Tool",
    layout="wide"
)

st.title("🔐 Security Group Analysis Tool")

STANDARD_FILE = "standard_data.xlsx"

# Load Standard Data
try:
    std_df = pd.read_excel(STANDARD_FILE)
    std_df = normalize_dataframe(std_df)
except Exception as e:
    st.error(f"❌ Could not load `{STANDARD_FILE}`: {e}")
    st.stop()

# Upload Client File
uploaded = st.file_uploader("📤 Upload Client SG Excel File", type=["xlsx"])

if uploaded:
    try:
        raw_client_df = pd.read_excel(uploaded)
        client_df = normalize_dataframe(raw_client_df)
        st.session_state["client_df"] = client_df
        st.success("✅ Client file loaded successfully!")
    except Exception as e:
        st.error(f"❌ Failed to read uploaded file: {e}")
        st.stop()

if "client_df" not in st.session_state:
    st.info("⬆️ Please upload a client file to continue.")
    st.stop()

client_df = st.session_state["client_df"]

# Compute differences
only_in_std, only_in_client, diff_table = compute_differences(std_df, client_df)
similarity_results = compute_similarity(client_df)

# Summary
st.subheader("📊 Summary Overview")

c1, c2, c3 = st.columns(3)
c1.metric("Missing in Client (Std Only)", len(only_in_std))
c2.metric("Client Only SGs", len(only_in_client))
c3.metric("Row-Level Differences", len(diff_table))

st.markdown("---")

st.subheader("🔍 Preview Differences (Top 10)")
if diff_table.empty:
    st.info("✔ No differences found.")
else:
    st.dataframe(diff_table.head(10))

st.markdown("➡️ Use the sidebar pages for full analysis.")
