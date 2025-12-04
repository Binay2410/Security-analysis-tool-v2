import streamlit as st
import pandas as pd
import html

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
    "diff_results" not in st.session_state
    or "client_df" not in st.session_state
    or "std_df" not in st.session_state
):
    st.error("⚠️ Please upload a client file on the main page.")
    st.stop()

only_in_std = st.session_state["diff_results"]["only_in_std"]
only_in_client = st.session_state["diff_results"]["only_in_client"]
diff_table = st.session_state["diff_results"]["diff_table"].copy()


# ------------------------------------------------------------------------------
# SECTION 1 — MISSING IN CLIENT
# ------------------------------------------------------------------------------
st.markdown("""
<h3 style="color:#D62828;">❌ Security Group(s) Does Not Exist in Tenant</h3>
<p style="margin-bottom:12px; color:#666;">
These SGs exist in the standard configuration but are missing from the client tenant.
</p>
""", unsafe_allow_html=True)

if only_in_std:
    st.dataframe(pd.DataFrame({"Security Group": only_in_std}), use_container_width=True)
else:
    st.success("✔ No missing security groups.")


# ------------------------------------------------------------------------------
# SECTION 2 — CLIENT ONLY SGs
# ------------------------------------------------------------------------------
st.markdown("""
<h3 style="color:#E67E22;">⚠️ Custom Security Group(s)</h3>
<p style="margin-bottom:12px; color:#666;">
These SGs exist in the client tenant but are not part of the standard configuration.
</p>
""", unsafe_allow_html=True)

if only_in_client:
    st.dataframe(pd.DataFrame({"Security Group": only_in_client}), use_container_width=True)
else:
    st.success("✔ No custom security groups.")


# ------------------------------------------------------------------------------
# SECTION 3 — DETAILED ROW-LEVEL DIFFERENCES
# ------------------------------------------------------------------------------
st.markdown("""
<h3 style="color:#2A61FF;">🟰 Detailed Row-Level Differences</h3>
<p style="margin-bottom:12px; color:#666;">
Below are detailed access-level differences for each security group.
The table highlights Missing (red) and Extra (black) access items.
</p>
""", unsafe_allow_html=True)

if diff_table.empty:
    st.success("✔ No row-level differences found.")
    st.stop()


# ------------------------------------------------------------------------------
# RENAME COLUMNS (final expected names)
# ------------------------------------------------------------------------------
diff_table = diff_table.rename(columns={
    "SG Name": "Security Group",
    "Column": "Access Type"
})


# ------------------------------------------------------------------------------
# FORMAT DIFF ITEMS AS HTML (Missing = Red, Extra = Black)
# ------------------------------------------------------------------------------
def extract_diff_items_formatted(std_val: str, client_val: str) -> str:
    std_items = {
        line.strip() for line in str(std_val).splitlines() if str(line).strip() != ""
    }
    client_items = {
        line.strip() for line in str(client_val).splitlines() if str(line).strip() != ""
    }

    missing = sorted(list(std_items - client_items))
    extra = sorted(list(client_items - std_items))

    result = []

    for item in missing:
        result.append(
            f"<div><span style='color:red; font-weight:bold;'>Missing:</span> {html.escape(item)}</div>"
        )
    for item in extra:
        result.append(
            f"<div><span style='color:black;'>Extra:</span> {html.escape(item)}</div>"
        )

    return "".join(result)


diff_table["Difference Items"] = diff_table.apply(
    lambda r: extract_diff_items_formatted(r["Standard Value"], r["Client Value"]),
    axis=1
)


# ------------------------------------------------------------------------------
# COLUMN ORDER
# ------------------------------------------------------------------------------
diff_table = diff_table[
    ["Security Group", "Access Type", "Standard Value", "Client Value", "Difference Items"]
]


# ------------------------------------------------------------------------------
# SAFE HTML ESCAPING FOR NON-HTML COLUMNS
# ------------------------------------------------------------------------------
def safe_cell(val: str) -> str:
    """Escape HTML safely and convert newlines into <br>."""
    if val is None:
        return ""
    val = str(val)
    val = html.escape(val)
    val = val.replace("\n", "<br>").replace("\r", "")
    return val


# ------------------------------------------------------------------------------
# FINAL SAFE HTML TABLE RENDERER (100% stable)
# ------------------------------------------------------------------------------
def render_html_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "<p style='color:#777;'>No differences found.</p>"

    html_str = "<table style='width:100%; border-collapse: collapse; font-size:14px;'>"

    # Header
    html_str += "<thead><tr>"
    for col in df.columns:
        html_str += f"""
        <th style='
            border:1px solid #DDD;
            padding:8px;
            background:#F0F4FF;
            font-weight:600;
            color:#2A2A2A;
        '>{html.escape(str(col))}</th>
        """
    html_str += "</tr></thead><tbody>"

    # Rows
    for _, row in df.iterrows():
        html_str += "<tr>"
        for col in df.columns:
            raw_val = row[col]
            raw_val = "" if raw_val is None else str(raw_val)

            # Difference Items contains intended HTML → do NOT escape
            if col == "Difference Items":
                cell_html = raw_val
            else:
                cell_html = safe_cell(raw_val)

            html_str += f"""
            <td style='
                border:1px solid #EEE;
                padding:8px;
                vertical-align:top;
            '>{cell_html}</td>
            """
        html_str += "</tr>"

    html_str += "</tbody></table>"

    return html_str


# ------------------------------------------------------------------------------
# DISPLAY THE TABLE
# ------------------------------------------------------------------------------
html_output = render_html_table(diff_table)
st.write(html_output, unsafe_allow_html=True)
