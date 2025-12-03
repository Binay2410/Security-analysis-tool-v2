import streamlit as st
import pandas as pd
from utils.comparator import compute_differences

st.title("📘 Difference Report")

if "client_file" not in st.session_state:
    st.error("❌ Please upload a client file from the main page.")
    st.stop()

std_df = pd.read_excel("standard_data.xlsx")
client_df = pd.read_excel(st.session_state["client_file"])

only_in_std, only_in_client, diff_table = compute_differences(std_df, client_df)

st.subheader("🔷 Missing in Client (Standard Only)")
st.dataframe(pd.DataFrame({"SG Name": only_in_std}))

st.subheader("🔶 Present Only in Client")
st.dataframe(pd.DataFrame({"SG Name": only_in_client}))

st.subheader("🟰 Row-Level Differences")
if diff_table.empty:
    st.info("✔ No row-level differences found.")
else:
    st.dataframe(diff_table)
