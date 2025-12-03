import streamlit as st
from utils.comparator import compute_differences

st.title("📘 Difference Report")

if "client_df" not in st.session_state or "std_df" not in st.session_state:
    st.error("Please upload a client file on the main page.")
    st.stop()

client_df = st.session_state["client_df"]
std_df = st.session_state["std_df"]

@st.cache_data(show_spinner=True)
def get_differences(std_df, client_df):
    return compute_differences(std_df, client_df)

only_in_std, only_in_client, diff_table = get_differences(std_df, client_df)

st.subheader("🔹 Missing in Client (Standard Only)")
st.dataframe({"SG Name": only_in_std})

st.subheader("🔸 Client Only SGs")
st.dataframe({"SG Name": only_in_client})

st.subheader("🟰 Detailed Row-Level Differences")
if diff_table.empty:
    st.info("✔ No row-level differences found.")
else:
    st.dataframe(diff_table)
