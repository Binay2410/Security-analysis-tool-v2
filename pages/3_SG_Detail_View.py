import streamlit as st
import pandas as pd

# ------------------------------------------------------------------------------
# PAGE HEADER
# ------------------------------------------------------------------------------
st.markdown("""
<h2 style="color:#2A61FF; margin-bottom:0;">🔎 Security Group Detail Viewer</h2>
<p style="color:#555; margin-top:4px; font-size:14px;">
View the complete access configuration for any Security Group in the client tenant.
</p>
<hr style="margin-top:0;">
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# VALIDATION
# ------------------------------------------------------------------------------
if "client_df" not in st.session_state:
    st.error("⚠️ Please upload a client file on the main page.")
    st.stop()

if "std_df" not in st.session_state:
    st.error("⚠️ Standard file missing. Ensure the main page loaded correctly.")
    st.stop()

if "diff_results" not in st.session_state:
    st.error("⚠️ Differences not computed yet. Load the main page once.")
    st.stop()

client_df = st.session_state["client_df"]
std_df = st.session_state["std_df"]
diff_table = st.session_state["diff_results"]["diff_table"]

# ------------------------------------------------------------------------------
# SELECT SECURITY GROUP
# ------------------------------------------------------------------------------
sg_list = sorted(client_df["SG Name"].unique())

selected = st.selectbox(
    "Select a Security Group",
    sg_list,
    index=0,
    help="Choose an SG to view all access details."
)

row_client = client_df[client_df["SG Name"] == selected].iloc[0]

# Try to load standard row (may not exist)
std_matches = std_df[std_df["SG Name"] == selected]
row_std = std_matches.iloc[0] if not std_matches.empty else None

# ------------------------------------------------------------------------------
# SECTION: SG SUMMARY CARD
# ------------------------------------------------------------------------------
st.markdown(f"""
<div style="padding:18px; background:#FFF; border-radius:10px;
            box-shadow:0 2px 8px rgba(0,0,0,.08); border:1px solid #EEE;
            margin-bottom:20px;">
    <h3 style="margin:0; font-size:22px; color:#2A61FF;">{selected}</h3>
    <p style="margin:4px 0 0; color:#444;">Complete access breakdown</p>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# SHOW ACCESS CATEGORIES (Client Data)
# ------------------------------------------------------------------------------
st.markdown("""
<h3 style="color:#2A61FF;">📂 Client Access Details</h3>
<div style="color:#555; margin-bottom:10px;">
Each category below shows the raw configured values for the selected SG.
</div>
""", unsafe_allow_html=True)


client_display_df = (
    row_client
    .drop(labels="SG Name")
    .to_frame(name="Client Value")
    .reset_index()
    .rename(columns={"index": "Access Type"})
)

st.dataframe(client_display_df, use_container_width=True)


# ------------------------------------------------------------------------------
# SHOW STANDARD VS CLIENT (If available)
# ------------------------------------------------------------------------------
st.markdown("""
<h3 style="color:#2A61FF; margin-top:35px;">📘 Standard Access Comparison</h3>
""", unsafe_allow_html=True)

if row_std is None:
    st.warning("ℹ️ This security group does **not** exist in the Standard dataset.")
else:
    compare_df = pd.DataFrame({
        "Access Type": row_client.drop("SG Name").index,
        "Client Value": row_client.drop("SG Name").values,
        "Standard Value": row_std.drop("SG Name").values
    })
    st.dataframe(compare_df, use_container_width=True)


# ------------------------------------------------------------------------------
# DIFFERENCE DETAILS (if SG appears in diff_table)
# ------------------------------------------------------------------------------
st.markdown("""
<h3 style="color:#2A61FF; margin-top:35px;">⚡ Differences for This SG</h3>
""", unsafe_allow_html=True)

sg_diffs = diff_table[diff_table["SG Name"] == selected]

if sg_diffs.empty:
    st.success("✔ No differences for this security group.")
else:
    sg_diffs_display = sg_diffs.rename(columns={
        "Column": "Access Type",
        "Standard Value": "Standard Value",
        "Client Value": "Client Value"
    })[["Access Type", "Standard Value", "Client Value"]]

    st.dataframe(sg_diffs_display, use_container_width=True)
