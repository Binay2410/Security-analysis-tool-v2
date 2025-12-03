import streamlit as st
import pandas as pd

st.title("📘 Difference Report")

# ------------------------------------------------------------------------------
# ✔ 1. VALIDATE DATA — MUST read from session_state only
# ------------------------------------------------------------------------------
if (
    "diff_results" not in st.session_state or
    "client_df" not in st.session_state or
    "std_df" not in st.session_state
):
    st.error("Please upload a client file on the main page.")
    st.stop()

only_in_std = st.session_state["diff_results"]["only_in_std"]
only_in_client = st.session_state["diff_results"]["only_in_client"]
diff_table = st.session_state["diff_results"]["diff_table"]

# ------------------------------------------------------------------------------
# ✔ 2. Show “Missing in Client”
# ------------------------------------------------------------------------------
st.subheader("❌ Security Group(s) does not exist in tenant")
st.dataframe({"Security Group": only_in_std})

# ------------------------------------------------------------------------------
# ✔ 3. Show “Client Only”
# ------------------------------------------------------------------------------
st.subheader("⚠️ Custom Security Group(s)")
st.dataframe({"Security Group": only_in_client})

# ------------------------------------------------------------------------------
# ✔ 4. Detailed Row-Level Differences
# ------------------------------------------------------------------------------
st.subheader("🟰 Detailed Row-Level Differences")

if diff_table.empty:
    st.info("✔ No differences found.")
    st.stop()

# ------------------------------------------------------------------------------
# ✔ 5. Rename Columns
# ------------------------------------------------------------------------------
diff_table = diff_table.rename(columns={
    "SG Name": "Security Group",
    "Column": "Access Type"
})

# ------------------------------------------------------------------------------
# ✔ 6. Format Missing / Extra Items
# ------------------------------------------------------------------------------
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


diff_table["Difference Items"] = diff_table.apply(
    lambda row: extract_diff_items_formatted(row["Standard Value"], row["Client Value"]),
    axis=1
)

# ------------------------------------------------------------------------------
# ✔ 7. Order Columns
# ------------------------------------------------------------------------------
diff_table = diff_table[
    ["Security Group", "Access Type", "Standard Value", "Client Value", "Difference Items"]
]

# ------------------------------------------------------------------------------
# ✔ 8. Render HTML Table (Styler removed)
# ------------------------------------------------------------------------------
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

html_table = render_html_table(diff_table)
st.write(html_table, unsafe_allow_html=True)
