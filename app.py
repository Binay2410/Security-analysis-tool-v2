import streamlit as st
import pandas as pd

from utils.comparator import compute_differences
from utils.similarity import compute_similarity

st.set_page_config(
    page_title="Security Group Analysis Tool",
    layout="wide"
)

st.title("🔐 Security Group Analysis Tool")

# Load Standard File
STANDARD_FILE = "standard_data.xlsx"

try:
    std_df = pd.read_excel(STANDARD_FILE)
except Exception as e:
    st.error(f"❌ Could not load `{STANDARD_FILE}`: {e}")
    st.stop()

# Upload Client File
uploaded = st.file_uploader("📤 Upload Client SG Excel File", type=["xlsx"])

if uploaded:
    st.session_state["client_file"] = uploaded

if "client_file" not in st.session_state:
    st.info("⬆️ Please upload a client file to continue.")
    st.stop()

# Load Client File
try:
    client_df = pd.read_excel(st.session_state["client_file"])
except Exception as e:
    st.error(f"❌ Failed to read uploaded file: {e}")
    st.stop()

st.success("✅ Client file uploaded!")

# Compute Differences
only_in_std, only_in_client, diff_table = compute_differences(std_df, client_df)

# Compute Similarity
similarity_results = compute_similarity(client_df)

# Summary Metrics
st.subheader("📊 Summary")

c1, c2, c3 = st.columns(3)

c1.metric("Missing in Client", len(only_in_std))
c2.metric("Client Only SGs", len(only_in_client))
c3.metric("Row-Level Differences", len(diff_table))

st.markdown("---")

st.subheader("🔍 Preview Differences (Top 10)")
if diff_table.empty:
    st.info("✔ No differences found.")
else:
    st.dataframe(diff_table.head(10))

st.markdown("➡️ Use the sidebar pages for full analysis.")
