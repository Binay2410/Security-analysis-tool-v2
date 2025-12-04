import streamlit as st
import pandas as pd

# ------------------------------------------------------------------------------
# PAGE HEADER
# ------------------------------------------------------------------------------
st.markdown("""
<h2 style="color:#2A61FF; margin-bottom:0;">📘 Difference Report</h2>
<p style="color:#555; margin-top:4px; font-size:14px;">
This report highlights missing security groups, custom client-defined groups, 
and detailed row-level differences across all access types.
</p>
<hr style="margin-top:0;">
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# VALIDATION
# ------------------------------------------------------------------------------
if (
    "diff_results" not in st.session_state or
    "client_df" not in st.session_state or
    "std_df" not in st.session_state
):
    st.error("⚠️ Please upload a client file on the main page.")
    st.stop()

only_in_std = st.session_state["diff_results"]["only_in_std"]
only_in_client = st.session_state["diff_results"]["only_in_client"]
diff_table = st.session_state["diff_results"]["diff_table"]

# ------------------------------------------------------------------------------
# MISSING IN CLIENT (Styled)
# ------------------------------------------------------------------------------
st.markdown("""
<h3 style="color:#D62828;">❌ Security Group(s) Does Not Exist in Tenant</h3>
<div style="margin-bottom:15px; color:#666;">
These security groups exist in the industry standard configuration but are missing from the client tenant.
</div>
""", unsafe_allow_html=True)

if only_in_std:
    df_std = pd.DataFrame({"Security Group": only_in_std})
    st.dataframe(df_std, use_container_width=True)
else:
    st.success("✔ No missing security groups.")

# ------------------------------------------------------------------------------
# CLIENT ONLY (Styled)
# ------------------------------------------------------------------------------
st.markdown("""
<h3 style="color:#E67E22;">⚠️ Custom Security Group(s)</h3>
<div style="margin-bottom:15px; color:#666;">
These security groups exist in the client tenant but are not part of the standard configuration.
</div>
""", unsafe_allow_html=True)

if only_in_client:
    df_client = pd.DataFrame({"Security Group": only_in_client})
    st.dataframe(df_client, use_container_width=True)
else:
    st.success("✔ No custom security groups.")

# ------------------------------------------------------------------------------
# DETAILED DIFFERENCES
# ------------------------------------------------------------------------------
st.markdown("""
<h3 style="color:#2A61FF;">🟰 Detailed Row-Level Differences</h3>
<div style="margin-bottom:15px; color:#666;">
Below are detailed access-level differences for each security group.
Missing and extra access items are highlighted.
</div>
""", unsafe_allow_html=True)

if diff_table.empty:
    st.success("✔ No row-level differences found.")
    st.stop()

# ------------------------------------------------------------------------------
# RENAME COLUMNS
# ------------------------------------------------------------------------------
diff_table = diff_table.rename(columns={
    "SG Name": "Security Group",
    "Column": "Access Type"
})

# ------------------------------------------------------------------------------
# FORMAT DIFFERENCES (Missing = Red, Extra = Black)
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
            f"<div><span style='color:red; font-weight:bold;'>Missing:</span> {item}</div>"
        )

    for item in extra_items:
        formatted.append(
            f"<div><span style='color:black;'>Extra:</span> {item}</div>"
        )

    return "".join(formatted)

diff_table["Difference Items"] = diff_table.apply(
    lambda row: extract_diff_items_formatted(row["Standard Value"], row["Client Value"]),
    axis=1
)

# ------------------------------------------------------------------------------
# ORDER COLUMNS
# ------------------------------------------------------------------------------
diff_table = diff_table[
    ["Security Group", "Access Type", "Standard Value", "Client Value", "Difference Items"]
]

# ------------------------------------------------------------------------------
# RENDER HTML TABLE CLEANLY
# ------------------------------------------------------------------------------
def render_html_table(df: pd.DataFrame) -> str:
    html = """
    <table style='width:100%; border-collapse: collapse; font-size:14px;'>
    """

    # Header
    html += "<tr>"
    for col in df.columns:
        html += f"""
        <th style="
            border:1px solid #DDD; 
            padding:8px; 
            background:#F0F4FF; 
            font-weight:600;
            color:#2A2A2A;">
            {col}
        </th>
        """
    html += "</tr>"

    # Rows
    for _, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
            val = row[col] if pd.notna(row[col]) else ""
            html += f"""
            <td style="
                border:1px solid #EEE; 
                padding:8px; 
                vertical-align:top;">
                {val}
            </td>
            """
        html += "</tr>"

    html += "</table>"
    return html


html_table = render_html_table(diff_table)
st.write(html_table, unsafe_allow_html=True)
