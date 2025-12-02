
import streamlit as st
import pandas as pd
from utils.comparator import generate_difference_report

st.title("Difference Report")

st.session_state.setdefault("client_df", None)
st.session_state.setdefault("std_df", None)

if st.session_state.client_df is None:
    st.error("Please upload a client file on the main page.")
else:
    df = generate_difference_report(
        st.session_state.client_df,
        st.session_state.std_df
    )
    st.dataframe(df)
