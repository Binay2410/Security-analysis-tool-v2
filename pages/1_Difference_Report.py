import streamlit as st
import pandas as pd

st.title("📘 Difference Report")

# Ensure data exists
if "client_df" not in st.session_state or "std_df" not in st.session_state:
    st.error("Please upload a client file on the main page.")
    st.stop()

client_df = st.session_state["client_df"]
std_df = st.session_state["std_df"]

# -----------------------------
# Load diff results (cached)
# -----------------------------
@st.cache_data(show_spinner=True)
def get_differences(std_df, client_df):
    from utils.comparator import compute_differences
    return compute_differences(std_df, client_df)

only_in_std, only_in_client, diff_table = get_differences(std_df, client_df)

# SAFETY: If diff_table is None or not a DataFrame
if diff_table is None or not isinstance(diff_table, pd.DataFrame):
    st.error("❌ Failed to compute differences.")
    st.stop()

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
# Rename columns
# -----------------------------
required_cols = {"SG Name", "Column", "Standard Value", "Client Value"}
missing_cols = required_cols - set(diff_table.columns)

if missing_cols:
    st.error(f"❌ Missing columns in diff_table: {missing_cols}")
    st.stop()

diff_table = diff_table.rename(columns={
    "SG Name": "Security Group",
    "Column": "Access Type"
})

# -----------------------------
# Helper: extract difference items with formatting
# -----------------------------
def extract_diff_items_formatted(std_val: str, client_val: str) -> str:

    std_items = {
        line.strip()
        for line in str(std_val).splitlines()
        if str(line).strip() != ""
    }

    client_items = {
        line.strip()
        for line in str(client_val).splitlines()
        if str(line).strip() != ""
    }

    missing_items = sorted(list(std_items - client_items))
    extra_items = sorted(list(client_items - std_items))

    formatted = []

    for item in missing_items:
        formatted.append(
            f"<span style='color:red; font-weight:bold'>Missing:</span> {item}"
        )

    for item in extra_items:
        formatted.append(
            f"<span style='color:black'>Extra:</span> {item}"
        )

    return "<br>".join(formatted)

# -----------------------------
# Build Difference Items column
# -----------------------------
diff_table["Difference Items"] = diff_table.apply(
    lambda row: extract_diff_items_formatted(row["Standard Value"], row["Client Value"]),
    axis=1
)

# -----------------------------
# Reorder columns
# -----------------------------
diff_table = diff_table[
    ["Security Group", "Access Type", "Standard Value", "Client Value", "Difference Items"]
]

# -----------------------------
# Render using HTML (Styler)
# -----------------------------
# -----------------------------
# Render table manually in HTML to avoid Styler errors
# -----------------------------

def render_html_table(df: pd.DataFrame) -> str:
    html = "<table style='width:100%; border-collapse: collapse;'>"

    # Header
    html += "<tr>"
    for col in df.columns:
        html += f"<th style='border:1px solid #ccc; padding:6px; background:#f0f0f0'>{col}</th>"
    html += "</tr>"

    # Rows
    for _, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
            val = row[col] if pd.notna(row[col]) else ""
            html += f"<td style='border:1px solid #ccc; padding:6px; vertical-align: top'>{val}</td>"
        html += "</tr>"

    html += "</table>"
    return html


# Now render the HTML table
html_table = render_html_table(diff_table)
st.write(html_table, unsafe_allow_html=True)
