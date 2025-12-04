import streamlit as st
import pandas as pd

from utils.helpers import normalize_dataframe
from utils.comparator import compute_differences

# ------------------------------------------------------------------------------
# PAGE CONFIG & THEME
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Security Group Analysis Tool",
    layout="wide"
)

# ------------------------------------------------------------------------------
# TOP BANNER
# ------------------------------------------------------------------------------
st.markdown("""
<div style="
    padding: 20px 10px; 
    border-bottom: 1px solid #EEE;
    margin-bottom:20px;">
    <h1 style="color:#2A61FF; font-size:32px; margin:0;">
        🔐 Security Group Analysis Tool
    </h1>
    <p style="color:#555; margin-top:4px; font-size:14px;">
        Compare client-provided Workday security groups with industry standard configuration.
    </p>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# UPLOAD SECTION (Styled)
# ------------------------------------------------------------------------------
st.markdown("""
<div style="
    background:#F5F7FB; 
    padding:20px;
    border-radius:10px;
    border:1px solid #E0E0E0;">
<h3 style="margin:0 0 15px 0; color:#333;">📤 Upload Client Security Group File</h3>
""", unsafe_allow_html=True)

uploaded = st.file_uploader("", type=["xlsx"])

st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# LOAD STANDARD FILE (once)
# ------------------------------------------------------------------------------
STANDARD_FILE = "standard_data.xlsx"

if "std_df" not in st.session_state:
    try:
        raw_std = pd.read_excel(STANDARD_FILE)
        st.session_state["std_df"] = normalize_dataframe(raw_std)
    except Exception as e:
        st.error(f"❌ Could not load standard_data.xlsx: {e}")
        st.stop()

std_df = st.session_state["std_df"]


# ------------------------------------------------------------------------------
# PROCESS UPLOADED CLIENT FILE — ONLY WHEN CHANGED
# ------------------------------------------------------------------------------
if uploaded and ("uploaded_filename" not in st.session_state or st.session_state["uploaded_filename"] != uploaded.name):
    try:
        raw_client_df = pd.read_excel(uploaded)
        client_df = normalize_dataframe(raw_client_df)

        st.session_state["client_df"] = client_df
        st.session_state["uploaded_filename"] = uploaded.name

        # Reset diff cache
        if "diff_results" in st.session_state:
            del st.session_state["diff_results"]

        st.success("✅ Client file loaded successfully!")

    except Exception as e:
        st.error(f"❌ Failed to load file: {e}")
        st.stop()


if "client_df" not in st.session_state:
    st.info("⬆️ Please upload a client file to continue.")
    st.stop()

client_df = st.session_state["client_df"]


# ------------------------------------------------------------------------------
# COMPUTE DIFFERENCES EXACTLY ONCE
# ------------------------------------------------------------------------------
if "diff_results" not in st.session_state:
    with st.spinner("Computing differences..."):
        only_in_std, only_in_client, diff_table = compute_difference
