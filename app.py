import streamlit as st
import pandas as pd

from utils.helpers import normalize_dataframe
from utils.comparator import compute_differences

# ------------------------------------------------------------------------------
# PAGE CONFIG & THEME
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Security Group Analysis Tool",
    layout="wide"
)

# ------------------------------------------------------------------------------
# TOP BANNER
# ------------------------------------------------------------------------------
st.markdown("""
<div style="
    padding: 20px 10px; 
    border-bottom: 1px solid #EEE;
    margin-bottom:20px;">
    <h1 style="color:#2A61FF; font-size:32px; margin:0;">
        🔐 Security Group Analysis Tool
    </h1>
    <p style="color:#555; margin-top:4px; font-size:14px;">
        Compare client-provided Workday security groups with industry standard configuration.
    </p>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# UPLOAD SECTION (Styled)
# ------------------------------------------------------------------------------
st.markdown("""
<div style="
    background:#F5F7FB; 
    padding:20px;
    border-radius:10px;
    border:1px solid #E0E0E0;">
<h3 style="margin:0 0 15px 0; color:#333;">📤 Upload Client Security Group File</h3>
""", unsafe_allow_html=True)

uploaded = st.file_uploader("", type=["xlsx"])

st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# LOAD STANDARD FILE (once)
# ------------------------------------------------------------------------------
STANDARD_FILE = "standard_data.xlsx"

if "std_df" not in st.session_state:
    try:
        raw_std = pd.read_excel(STANDARD_FILE)
        st.session_state["std_df"] = normalize_dataframe(raw_std)
    except Exception as e:
        st.error(f"❌ Could not load standard_data.xlsx: {e}")
        st.stop()

std_df = st.session_state["std_df"]


# ------------------------------------------------------------------------------
# PROCESS UPLOADED CLIENT FILE — ONLY WHEN CHANGED
# ------------------------------------------------------------------------------
if uploaded and ("uploaded_filename" not in st.session_state or st.session_state["uploaded_filename"] != uploaded.name):
    try:
        raw_client_df = pd.read_excel(uploaded)
        client_df = normalize_dataframe(raw_client_df)

        st.session_state["client_df"] = client_df
        st.session_state["uploaded_filename"] = uploaded.name

        # Reset diff cache
        if "diff_results" in st.session_state:
            del st.session_state["diff_results"]

        st.success("✅ Client file loaded successfully!")

    except Exception as e:
        st.error(f"❌ Failed to load file: {e}")
        st.stop()


if "client_df" not in st.session_state:
    st.info("⬆️ Please upload a client file to continue.")
    st.stop()

client_df = st.session_state["client_df"]


# ------------------------------------------------------------------------------
# COMPUTE DIFFERENCES EXACTLY ONCE
# ------------------------------------------------------------------------------
if "diff_results" not in st.session_state:
    with st.spinner("Computing differences..."):
        only_in_std, only_in_client, diff_table = compute_differences(std_df, client_df)
        st.session_state["diff_results"] = {
            "only_in_std": only_in_std,
            "only_in_client": only_in_client,
            "diff_table": diff_table
        }

only_in_std = st.session_state["diff_results"]["only_in_std"]
only_in_client = st.session_state["diff_results"]["only_in_client"]
diff_table = st.session_state["diff_results"]["diff_table"]


# ------------------------------------------------------------------------------
# SUMMARY CARDS
# ------------------------------------------------------------------------------
st.subheader("📊 Summary Overview")

c1, c2, c3 = st.columns(3)

c1.markdown(f"""
<div style="padding:18px; background:#FFF; border-radius:10px; 
            box-shadow:0 2px 8px rgba(0,0,0,.08); border:1px solid #EEE;">
    <h3 style="margin:0; font-size:20px; color:#2A61FF;">Missing in Client</h3>
    <p style="font-size:28px; margin:0; font-weight:bold;">{len(only_in_std)}</p>
</div>
""", unsafe_allow_html=True)

c2.markdown(f"""
<div style="padding:18px; background:#FFF; border-radius:10px; 
            box-shadow:0 2px 8px rgba(0,0,0,.08); border:1px solid #EEE;">
    <h3 style="margin:0; font-size:20px; color:#FF8C00;">Client-Only SGs</h3>
    <p style="font-size:28px; margin:0; font-weight:bold;">{len(only_in_client)}</p>
</div>
""", unsafe_allow_html=True)

c3.markdown(f"""
<div style="padding:18px; background:#FFF; border-radius:10px; 
            box-shadow:0 2px 8px rgba(0,0,0,.08); border:1px solid #EEE;">
    <h3 style="margin:0; font-size:20px; color:#00A65A;">Differences Found</h3>
    <p style="font-size:28px; margin:0; font-weight:bold;">{len(diff_table)}</p>
</div>
""", unsafe_allow_html=True)


st.markdown("---")


# ------------------------------------------------------------------------------
# TOP 10 DIFFERENCE SUMMARY
# ------------------------------------------------------------------------------
def count_difference_items(std_val, client_val):
    std_items = {x.strip() for x in str(std_val).splitlines() if x.strip()}
    client_items = {x.strip() for x in str(client_val).splitlines() if x.strip()}

    return len(std_items - client_items) + len(client_items - std_items)


def build_sg_diff_summary(diff_df):
    summary = {}

    for _, row in diff_df.iterrows():
        sg = row["SG Name"]
        diff_count = count_difference_items(row["Standard Value"], row["Client Value"])
        summary[sg] = summary.get(sg, 0) + diff_count

    return (
        pd.DataFrame(
            [{"Security Group": sg, "Total Differences": count} for sg, count in summary.items()]
        )
        .sort_values("Total Differences", ascending=False)
        .reset_index(drop=True)
    )


st.subheader("🔍 Preview – Top 10 Security Groups With Maximum Differences")

if diff_table.empty:
    st.info("✔ No differences found.")
else:
    top10 = build_sg_diff_summary(diff_table).head(10)
    st.dataframe(top10, use_container_width=True)


st.markdown("➡️ Use the sidebar for full Difference Report and Similarity Analysis.")


# ------------------------------------------------------------------------------
# COMPUTE SIMILARITY ONCE
# ------------------------------------------------------------------------------
from utils.similarity import compute_similarity

if "similarity_results" not in st.session_state:
    with st.spinner("Computing similarity analysis..."):
        sim_df = compute_similarity(client_df)
        st.session_state["similarity_results"] = sim_df
