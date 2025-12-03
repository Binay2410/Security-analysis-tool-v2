import streamlit as st
from utils.comparator import compute_differences
import pandas as pd

st.title("📘 Difference Report")

# Ensure data exists
if "client_df" not in st.session_state or "std_df" not in st.session_state:
    st.error("Please upload a client file on the main page.")
    st.stop()

client_df = st.session_state["client_df"]
std_df = st.session_state["std_df"]

@st.cache_data(show_spinner=True)
def get_differences(std_df, client_df):
    return compute_differences(std_df, client_df)

only_in_std, only_in_client, diff_table = get_differences(std_df, client_df)

# -----------------------------
# Section headings
# -----------------------------
st.subheader("❌ Security Group(s) does not exist in tenant")
st.dataframe({"Security Group": only_in_std})

st.subheader("⚠️ Custom Security Group(s)")
st.dataframe({"Security Group": only_in_client})

st.subheader("🟰 Detailed Row-Level Differences")

if diff_table.empty:
    st.info("✔ No row-level differences found.")
    st.stop()

# -----------------------------
# Rename columns as requested
# -----------------------------
diff_table = diff_table.rename(columns={
    "SG Name": "Security Group",
    "Column": "Access Type"
})

# -----------------------------
# Helper: extract difference items
# -----------------------------
def extract_diff_items(std_val: str, client_val: str) -> str:
    """
    From two multi-line strings (Standard Value, Client Value),
    return only the items that are different.

    Example:
    Standard: A, B, C, D
    Client:   A, C
    Result:   B, D
    """
    # Convert to list of stripped lines
    std_items = [
        line.strip()
        for line in str(std_val).splitlines()
        if line is not None and str(line).strip() != ""
    ]
    client_items = [
        line.strip()
        for line in str(client_val).splitlines()
        if line is not None and str(line).strip() != ""
    ]

    std_set = set(std_items)
    client_set = set(client_items)

    # Items that differ between Standard and Client
    # You can choose:
    # - only missing from client: std_set - client_set
    # - OR symmetric diff (both missing and extra): (std_set - client_set) ∪ (client_set - std_set)
    diff_items = sorted(list(std_set - client_set))  # <- only items missing in client

    # If you also want Extra items from client, use:
    # diff_items = sorted(list((std_set - client_set) | (client_set - std_set)))

    return "\n".join(diff_items)

# -----------------------------
# Build Difference Items column
# -----------------------------
diff_table["Difference Items"] = diff_table.apply(
    lambda row: extract_diff_items(row["Standard Value"], row["Client Value"]),
    axis=1
)

# -----------------------------
# Reorder and display
# -----------------------------
display_cols = [
    "Security Group",
    "Access Type",
    "Standard Value",
    "Client Value",
    "Difference Items"
]

diff_table = diff_table[display_cols]

st.dataframe(diff_table, use_container_width=True)
