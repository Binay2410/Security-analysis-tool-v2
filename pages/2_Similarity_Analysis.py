import streamlit as st
import pandas as pd

# ------------------------------------------------------------------------------
# PAGE HEADER
# ------------------------------------------------------------------------------
st.markdown("""
<h2 style="color:#2A61FF; margin-bottom:0;">🧬 Similarity Analysis</h2>
<p style="color:#555; margin-top:4px; font-size:14px;">
This analysis identifies security groups that share similar access patterns.
Useful for detecting duplicates, redundancies, or merge candidates.
</p>
<hr style="margin-top:0;">
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# VALIDATE DATA
# ------------------------------------------------------------------------------
if "client_df" not in st.session_state:
    st.error("⚠️ Please upload a client file on the main page.")
    st.stop()

if "similarity_results" not in st.session_state:
    st.error("⚠️ Similarity has not been computed yet. Please rerun the home page.")
    st.stop()

sim_df = st.session_state["similarity_results"]

# ------------------------------------------------------------------------------
# SUMMARY CARD
# ------------------------------------------------------------------------------
st.markdown("""
<div style="padding:18px; background:#FFF; border-radius:10px; 
            box-shadow:0 2px 8px rgba(0,0,0,.08); border:1px solid #EEE;">
    <h3 style="margin:0; font-size:20px;
