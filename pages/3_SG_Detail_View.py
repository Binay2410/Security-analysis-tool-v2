import streamlit as st

st.title("🔎 SG Detail Viewer")

if "client_df" not in st.session_state:
    st.error("Please upload a client file on the main page.")
    st.stop()

client_df = st.session_state["client_df"]

sg_list = sorted(client_df["SG Name"].unique())
selected = st.selectbox("Select Security Group", sg_list)

row = client_df[client_df["SG Name"] == selected].iloc[0]

st.subheader(f"Details for: {selected}")
st.dataframe(row.to_frame(name="Value"))
