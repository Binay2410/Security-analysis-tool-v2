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
    st.dataframe(pd.DataFrame({"Security Group": only_in_std}),
                 use_container_width=True)
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
    st.dataframe(pd.DataFrame({"Security Group": only_in_client}),
                 use_container_width=True)
else:
    st.success("✔ No custom security groups.")

# ------------------------------------------------------------------------------
# SECTION 3 — DETAILED ROW-LEVEL DIFFERENCES
# ------------------------------------------------------------------------------
st.markdown("""
<h3 style="color:#2A61FF;">🟰 Detailed Row-Level Differences</h3>
<p style="margin-bottom:12px; color:#666;">
Below are detailed access-level differences for each security group.
Each row shows the Standard value, Client value, and a list of Missing/Extra items.
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
# BUILD PLAIN TEXT DIFFERENCE ITEMS
# ------------------------------------------------------------------------------
def build_diff_items_text(std_val: str, client_val: str) -> str:
    """Return multi-line text:
       Missing: X
       Extra: Y
    with all items compared line-by-line."""
    std_items = {
        line.strip() for line in str(std_val).splitlines() if str(line).strip() != ""
    }
    client_items = {
        line.strip() for line in str(client_val).splitlines() if str(line).strip() != ""
    }

    missing = sorted(list(std_items - client_items))
    extra = sorted(list(client_items - std_items))

    lines = []
    for item in missing:
        lines.append(f"Missing: {item}")
    for item in extra:
        lines.append(f"Extra: {item}")

    return "\n".join(lines)


diff_table["Difference Items"] = diff_table.apply(
    lambda r: build_diff_items_text(r["Standard Value"], r["Client Value"]),
    axis=1
)

# ------------------------------------------------------------------------------
# COLUMN ORDER
# ------------------------------------------------------------------------------
diff_table = diff_table[
    ["Security Group", "Access Type", "Standard Value", "Client Value", "Difference Items"]
]

# ------------------------------------------------------------------------------
# DISPLAY USING STANDARD STREAMLIT TABLE (NO HTML)
# ------------------------------------------------------------------------------
st.dataframe(diff_table, use_container_width=True)
