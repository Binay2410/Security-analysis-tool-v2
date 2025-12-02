import streamlit as st
import pandas as pd
from utils.comparator import run_full_comparison
from utils.similarity import compute_similarity_summary
from utils.persistence import load_history

st.set_page_config(
    page_title="Security Group Analysis",
    layout="wide"
)

st.title("🔐 Security Group Analysis Tool")
st.write("Upload the client file below and view all analysis reports using the sidebar navigation.")

# -------------------------------
# Load Standard File (must exist in repo)
# -------------------------------
STANDARD_FILE = "standard_data.xlsx"

try:
    std_df = pd.read_excel(STANDARD_FILE)
except FileNotFoundError:
    st.error(f"❌ Missing required file: `{STANDARD_FILE}`.\n\nUpload it to your GitHub repository root.")
    st.stop()

# -------------------------------
# File Upload Section
# -------------------------------
uploaded = st.file_uploader("📤 Upload Client Access Excel", type=["xlsx"])

if uploaded:
    st.session_state["client_file"] = uploaded

# -------------------------------
# If no client file yet — show instructions
# -------------------------------
if "client_file" not in st.session_state:
    st.info("⬆️ Please upload the client Excel file to begin.")
    st.stop()

# -------------------------------
# Client DF Loaded Successfully
# -------------------------------
client_df = pd.read_excel(st.session_state["client_file"])

st.success("✅ Client file uploaded successfully!")

# -------------------------------
# PERSISTENCE FILES (Optional future feature)
# -------------------------------
accepted_risk_df, update_workday_df = load_persistent_files()

# -------------------------------
# RUN DIFFERENCE ENGINE
# -------------------------------
only_in_std, only_in_client, diff_table = compute_differences(std_df, client_df)

# -------------------------------
# RUN SIMILARITY ENGINE
# -------------------------------
similarity_results = compute_similarity(client_df)

# -------------------------------
# Display Summary Tiles
# -------------------------------
st.subheader("📊 Summary Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="🔹 Security Groups missing in Client (Standard Only)",
        value=len(only_in_std)
    )

with col2:
    st.metric(
        label="🔸 Custom Security Groups (Client Only)",
        value=len(only_in_client)
    )

with col3:
    st.metric(
        label="🟰 SGs with Row-Level Differences",
        value=len(diff_table)
    )

st.markdown("---")

# -------------------------------
# Preview of Differences Table (Top 10)
# -------------------------------
st.subheader("🔍 Quick Preview of Differences")
if len(diff_table) == 0:
    st.info("✔ No row-level differences detected.")
else:
    st.dataframe(diff_table.head(10))

st.markdown("➡️ Use the sidebar to open **Difference Report**, **Similarity Analysis**, or **Detail View** pages.")

