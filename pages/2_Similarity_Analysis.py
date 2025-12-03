import streamlit as st
from utils.similarity import compute_similarity

st.title("🧬 Similarity Analysis")

if "client_df" not in st.session_state:
    st.error("Please upload a client file on the main page.")
    st.stop()

client_df = st.session_state["client_df"]

@st.cache_data(show_spinner=True)
def get_similarity(df):
    return compute_similarity(df)

st.write("Computing SG similarity (this is done once per upload and cached)...")
sim_df = get_similarity(client_df)

if sim_df.empty:
    st.info("No SG pairs found with similarity above threshold.")
else:
    st.dataframe(sim_df)
