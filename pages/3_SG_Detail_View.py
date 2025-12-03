import streamlit as st
import pandas as pd

st.set_page_config(page_title="SG Detail View", layout="wide")

# ---- Retrieve data from session ---- #
client_df = st.session_state.get("client_df", None)
std_df = st.session_state.get("std_df", None)

if client_df is None:
    st.error("Please upload a file on the main page to continue.")
    st.stop()

# ---- Canonical Column Names ---- #
SG_COL = "Security Group Name"

if SG_COL not in client_df.columns:
    st.error(f"Expected column '{SG_COL}' not found in uploaded file.")
    st.write("Available columns:", list(client_df.columns))
    st.stop()

# ---- SG List ---- #
sg_list = sorted(client_df[SG_COL].dropna().unique())

st.title("🔍 Security Group Detail Viewer")

selected_sg = st.selectbox("Select a Security Group", sg_list)

if selected_sg:

    st.subheader(f"Details for: **{selected_sg}**")

    # Get the row
    sg_row = client_df[client_df[SG_COL] == selected_sg]

    if sg_row.empty:
        st.warning("No details found for this SG.")
        st.stop()

    row = sg_row.iloc[0]

    # ---- Display the fields except hidden ones ---- #
    st.write("### 📘 SG Attributes")

    hide_fields = [SG_COL]

    for col in client_df.columns:
        if col not in hide_fields:
            st.write(f"**{col}:** {row[col]}")

    # ---- Comparison with Standard Data ---- #
    st.write("---")
    st.write("### 📊 Match Against Standard Data")

    if std_df is not None and SG_COL in std_df.columns:
        std_row = std_df[std_df[SG_COL] == selected_sg]
        if len(std_row) > 0:
            st.success("This Security Group is present in Standard Data.")
            st.dataframe(std_row)
        else:
            st.warning("This Security Group does **NOT** exist in Standard Data.")
    else:
        st.info("Standard data is not loaded, cannot compute comparison.")
