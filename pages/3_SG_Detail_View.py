import streamlit as st

st.title("🔎 SG Detail Viewer")

if "client_df" not in st.session_state:
    st.error("Please upload a file on the main page to continue.")
    st.stop()

client_df = st.session_state["client_df"]

sg_list = sorted(client_df["SG Name"].unique())

choice = st.selectbox("Select Security Group", sg_list)

row = client_df[client_df["SG Name"] == choice].iloc[0]

st.subheader(f"Details for: {choice}")

st.dataframe(row.to_frame(name="Value"))
