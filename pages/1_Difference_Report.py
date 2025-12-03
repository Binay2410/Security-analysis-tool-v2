import streamlit as st
from utils.comparator import compute_differences

st.title("📘 Difference Report")

# Ensure data exists
if "client_df" not in st.session_state or "std_df" not in st.session_state:
    st.error("Please upload a client file on the main page.")
    st.stop()

client_df = st.session_state["client_df"]
std_df = st.session_state["std_df"]

# Cached for speed
@st.cache_data(show_spinner=True)
def get_differences(std_df, client_df):
    return compute_differences(std_df, client_df)

only_in_std, only_in_client, diff_table = get_differences(std_df, client_df)

# -----------------------------
# Rename Section Headings
# -----------------------------

st.subheader("❌ Security Group(s) does not exist in tenant")
st.dataframe({"Security Group": only_in_std})

st.subheader("⚠️ Custom Security Group(s)")
st.dataframe({"Security Group": only_in_client})

# -----------------------------
# Transform diff_table as requested
# -----------------------------
if not diff_table.empty:

    # Rename SG Name → Security Group
    diff_table = diff_table.rename(columns={
        "SG Name": "Security Group",
        "Column": "Access Type"
    })

    # Create Difference Summary column
    diff_table["Difference Summary"] = diff_table.apply(
        lambda row: 
            f"Standard: {row['Standard Value']}\nClient: {row['Client Value']}",
        axis=1
    )

# -----------------------------
# Display Row-Level Differences
# -----------------------------

st.subheader("🟰 Detailed Row-Level Differences")

if diff_table.empty:
    st.info("✔ No row-level differences found.")
else:
    # Reorder columns
    diff_table = diff_table[
        ["Security Group", "Access Type", "Standard Value", "Client Value", "Difference Summary"]
    ]
    st.dataframe(diff_table, use_container_width=True)
