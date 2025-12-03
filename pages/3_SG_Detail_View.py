import streamlit as st
import pandas as pd

st.title("📄 SG Detail Viewer")

if "client_file" not in st.session_state:
    st.error("❌ Please upload a client file from the main page.")
    st.stop()

client_df = pd.read_excel(st.session_state["client_file"])

sg_list = sorted(client_df["SG Name"].unique())

selected = st.selectbox("Select SG", sg_list)

row = client_df[client_df["SG Name"] == selected]

st.subheader(f"Details for: {selected}")
st.dataframe(row)
