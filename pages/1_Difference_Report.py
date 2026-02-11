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
<h3 style="color:#D62828;">Missing Security Group(s)</h3>
<p style="margin-bottom:12px; color:#666;">
These Security Group(s) should exist as per Industry Standards if the corresponding modules are implemented, but are missing from Workday tenant.
</p>
""", unsafe_allow_html=True)

if only_in_std:
    missing_df = pd.DataFrame({"Security Group": only_in_std}).reset_index(drop=True)
    missing_df.insert(0, "S.No", range(1, len(missing_df) + 1))

    missing_html = missing_df.to_html(index=False, escape=True)

    st.write(
        """
        <style>
        .mini-table table { width:100%; table-layout:fixed; border-collapse:collapse; }
        .mini-table th, .mini-table td { padding: 8px; border: 1px solid #E6E6E6; }
        .mini-table th { text-align:center; }
        .mini-table td:nth-child(1), .mini-table th:nth-child(1) { width:20%; text-align:center; }
        .mini-table td:nth-child(2), .mini-table th:nth-child(2) { width:80%; }
        .mini-table td:nth-child(2) { text-align:left; }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.write(f"<div class='mini-table'>{missing_html}</div>", unsafe_allow_html=True)
else:
    st.success("✔ No missing security groups.")


 


# ------------------------------------------------------------------------------
# SECTION 2 — CLIENT ONLY SGs
# ------------------------------------------------------------------------------
st.markdown("""
<h3 style="color:#E67E22;">Custom Security Group(s)</h3>
<p style="margin-bottom:12px; color:#666;">
These Security Group(s) exist in Workday tenant but do not appear in industry-standards and may represent client-specific custom groups.
</p>
""", unsafe_allow_html=True)

if only_in_client:
    custom_df = pd.DataFrame({"Security Group": only_in_client}).reset_index(drop=True)
    custom_df.insert(0, "S.No", range(1, len(custom_df) + 1))

    custom_html = custom_df.to_html(index=False, escape=True)

    # (CSS already injected above; no need to re-inject unless you want to)
    st.write(f"<div class='mini-table'>{custom_html}</div>", unsafe_allow_html=True)
else:
    st.success("✔ No custom security groups.")


# ------------------------------------------------------------------------------
# SECTION 3 — DETAILED ROW-LEVEL DIFFERENCES
# ------------------------------------------------------------------------------
st.markdown("""
<h3 style="color:#2A61FF;">Detailed Security Analysis</h3>
<p style="margin-bottom:12px; color:#666;">
Below are detailed access-level differences for each security group.
Missing = red, Extra = black.
</p>
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
# BUILD PLAIN TEXT FOR DIFFERENCE ITEMS
# ------------------------------------------------------------------------------
def build_diff_items_list(std_val: str, client_val: str):
    std_items = {
        line.strip() for line in str(std_val).splitlines() if str(line).strip() != ""
    }
    client_items = {
        line.strip() for line in str(client_val).splitlines() if str(line).strip() != ""
    }

    missing = sorted(list(std_items - client_items))
    extra = sorted(list(client_items - std_items))

    rows = []
    for item in missing:
        rows.append(("Missing", item))
    for item in extra:
        rows.append(("Extra", item))

    return rows


diff_table["Difference Items Raw"] = diff_table.apply(
    lambda r: build_diff_items_list(r["Standard Value"], r["Client Value"]),
    axis=1
)

# ------------------------------------------------------------------------------
# FLATTEN LIST INTO MULTILINE TEXT FOR DISPLAY
# ------------------------------------------------------------------------------
def diff_text(row):
    lines = []
    for typ, item in row:
        lines.append(f"{typ}: {item}")
    return "\n".join(lines)

diff_table["Difference Items"] = diff_table["Difference Items Raw"].apply(diff_text)

# ------------------------------------------------------------------------------
# APPLY COLOR WITH PANDAS STYLER
# ------------------------------------------------------------------------------
def color_diff(val):
    """Apply line-by-line coloring for Missing/Extra."""
    if pd.isna(val):
        return val

    lines = str(val).split("\n")

    colored = []
    for line in lines:
        if line.startswith("Missing:"):
            colored.append(f"<span style='color:red;font-weight:bold;'>{html.escape(line)}</span>")
        elif line.startswith("Extra:"):
            colored.append(f"<span style='color:black;'>{html.escape(line)}</span>")
        else:
            colored.append(html.escape(line))

    return "<br>".join(colored)


# ------------------------------------------------------------------
# ADD SERIAL NUMBER (START FROM 1) - DISPLAY ONLY (do not touch diff_table)
# ------------------------------------------------------------------

display_df = diff_table[[
    "Security Group",
    "Access Type",
    "Standard Value",
    "Client Value",
    "Difference Items"
]].reset_index(drop=True)

display_df.insert(0, "S.No", range(1, len(display_df) + 1))

styled_df = display_df.style.format({
    "Difference Items": color_diff
}, escape="html")

# ------------------------------------------------------------------
# DISPLAY STYLED TABLE
# ------------------------------------------------------------------
st.write(styled_df.hide(axis="index").to_html(), unsafe_allow_html=True)


