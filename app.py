import streamlit as st
import pandas as pd

st.title("Workday Security Analysis Tool")

# Load Standard data ONCE
if "standard_df" not in st.session_state:
    st.session_state.standard_df = pd.read_excel("data/standard_workday_security.xlsx")

standard_df = st.session_state.standard_df

uploaded_file = st.file_uploader("Upload Client Security Groups Excel", type=["xlsx"])

if uploaded_file:
    st.session_state.client_df = pd.read_excel(uploaded_file)

if "client_df" in st.session_state:
    client_df = st.session_state.client_df

    st.success("File uploaded successfully.")

    # Normalize SG key
    sg_column = "Domains granted to Security Group"
    client_df[sg_column] = client_df[sg_column].astype(str).str.strip().str.lower()
    standard_df[sg_column] = standard_df[sg_column].astype(str).str.strip().str.lower()

    # Summary counts
    client_set = set(client_df[sg_column])
    standard_set = set(standard_df[sg_column])

    st.metric("Client SG Count", len(client_set))
    st.metric("Standard SG Count", len(standard_set))
    st.metric("Client Only SGs", len(client_set - standard_set))
    st.metric("Missing in Client (Standard Only)", len(standard_set - client_set))
else:
    st.info("Upload an Excel file to begin.")
