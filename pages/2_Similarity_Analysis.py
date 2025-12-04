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
<div style="
    padding:18px; 
    background:#FFF; 
    border-radius:10px; 
    box-shadow:0 2px 8px rgba(0,0,0,.08); 
    border:1px solid #EEE;
    margin-bottom:20px;
">
    <h3 style="margin:0; font-size:20px; color:#2A61FF;">
        Similarity Overview
    </h3>
    <p style="margin:6px 0 0 0; color:#555; font-size:16px;">
        Total high-similarity SG pairs detected: 
        <strong>{count}</strong>
    </p>
</div>
""".format(count=len(sim_df)), unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# RESULTS TABLE
# ------------------------------------------------------------------------------
st.subheader("🔍 Similar SG Pairs")

if sim_df.empty:
    st.info("✔ No similarity matches found above threshold.")
else:
    st.dataframe(sim_df, use_container_width=True)
