import streamlit as st

st.title("📘 Difference Report")

if "client_df" not in st.session_state:
    st.error("Please upload a client file on the main page.")
    st.stop()

client_df = st.session_state["client_df"]
std_df = st.session_state.get("std_df")

from utils.comparator import compute_differences

only_in_std, only_in_client, diff_table = compute_differences(std_df, client_df)

st.subheader("Missing in Client")
st.dataframe(only_in_std)

st.subheader("Client Only")
st.dataframe(only_in_client)

st.subheader("Detailed Differences")
st.dataframe(diff_table)
