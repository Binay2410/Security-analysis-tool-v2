import streamlit as st
import pandas as pd
from utils.comparator import compute_differences
from utils.similarity import compute_similarity

st.set_page_config(
    page_title="Security Group Analysis",
    layout="wide"
)

st.title("🔐 Security Group Analysis Tool")
st.write("Upload the client file below and view all analysis reports using the sidebar menu.")

# ---------------------------------------------------
# LOAD STANDARD DATA FILE
# ---------------------------------------------------
STANDARD_FILE = "standard_data.xlsx"

try:
    std_df = pd.read_excel(STANDARD_FILE)
except FileNotFoundError:
    st.error(f"❌ Missing required file: `{STANDARD_FILE}`.\n\nPlease ensure it exists in your repository root.")
    st.stop()

# ---------------------------------------------------
# FILE UPLOAD SECTION
# ---------------------------------------------------
uploaded = st.file_uploader("📤 Upload Client Access Excel", type=["xlsx"])

if uploaded:
    st.session_state["client_file"] = uploaded

# ---------------------------------------------------
# IF NO CLIENT FILE — STOP & SHOW MESSAGE
# ---------------------------------------------------
if "client_file" not in st.session_state:
    st.info("⬆️ Please upload a client Excel file to begin.")
    st.stop()

# ---------------------------------------------------
# READ CLIENT FILE
# ---------------------------------------------------
try:
    client_df = pd.read_excel(st.session_state["client_file"])
except Exception as e:
    st.error(f"❌ Error reading uploaded file: {e}")
    st.stop()

st.success("✅ Client file uploaded successfully!")

# ---------------------------------------------------
# RUN DIFFERENCE ANALYSIS
# ---------------------------------------------------
only_in_std, only_in_client, diff_table = compute_differences(std_df, client_df)

# ---------------------------------------------------
# RUN SIMILARITY ANALYSIS
# ---------------------------------------------------
similarity_results = compute_similarity(client_df)

# ---------------------------------------------------
# SUMMARY METRICS
# ---------------------------------------------------
st.subheader("📊 Summary Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="🔹 Missing in Client (Standard Only)",
        value=len(only_in_std)
    )

with col2:
    st.metric(
        label="🔸 Client Only Groups (Custom)",
        value=len(only_in_client)
    )

with col3:
    st.metric(
        label="🟰 Differences in Row-Level Data",
        value=len(diff_table)
    )

st.markdown("---")

# ---------------------------------------------------
# QUICK PREVIEW OF DIFFERENCES
# ---------------------------------------------------
st.subheader("🔍 Differences Preview (Top 10)")

if len(diff_table) == 0:
    st.info("✔ No row-level differences detected.")
else:
    st.dataframe(diff_table.head(10))

st.markdown("➡️ Use the sidebar to access full **Difference Report**, **Similarity Analysis**, or **SG Detail Views**.")
