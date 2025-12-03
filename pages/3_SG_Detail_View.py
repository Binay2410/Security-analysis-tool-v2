import streamlit as st
import pandas as pd

st.set_page_config(page_title="SG Detail View", layout="wide")

# ---- Retrieve data ---- #
client_df = st.session_state.get("client_df", None)
std_df = st.session_state.get("std_df", None)

if client_df is None:
    st.error("⚠️ No client file found. Please upload the client file on the main page.")
    st.stop()

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

    sg_row = client_df[client_df[SG_COL] == selected_sg]

    if sg_row.empty:
        st.warning("No details found for this SG.")
        st.stop()

    row = sg_row.iloc[0]

    # ---- Display all columns ---- #
    st.write("### 📘 SG Attributes")

    for col in client_df.columns:
        st.write(f"**{col}:** {row[col]}")

    # ---- Comparison with Standard ---- #
    st.write("---")
    st.write("### 📊 Comparison With Standard Data")

    if std_df is not None and SG_COL in std_df.columns:
        std_row = std_df[std_df[SG_COL] == selected_sg]
        if len(std_row) > 0:
            st.success("This Security Group exists in Standard Data.")
            st.dataframe(std_row)
        else:
            st.warning("This SG does NOT exist in Standard Data.")
    else:
        st.info("Standard Data Not Loaded.")
