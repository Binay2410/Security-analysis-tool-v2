import streamlit as st
import pandas as pd

from utils.helpers import normalize_dataframe
from utils.comparator import compute_differences

st.set_page_config(
    page_title="Security Group Analysis Tool",
    layout="wide"
)

st.markdown("""
<div style="padding: 20px 10px; border-bottom: 1px solid #EEE;">
    <h1 style="color:#2A61FF; font-size: 32px; margin: 0;">
        🔐 Security Group Analysis Tool
    </h1>
    <p style="color:#555; margin-top: 4px; font-size:14px;">
        Enterprise-grade comparison, insights & AI-driven analysis
    </p>
</div>
""", unsafe_allow_html=True)


STANDARD_FILE = "standard_data.xlsx"

# ---------- Load & normalize Standard Data (once) ----------
if "std_df" not in st.session_state:
    try:
        raw_std_df = pd.read_excel(STANDARD_FILE)
        std_df = normalize_dataframe(raw_std_df)
        st.session_state["std_df"] = std_df
    except Exception as e:
        st.error(f"❌ Could not load `{STANDARD_FILE}`: {e}")
        st.stop()
else:
    std_df = st.session_state["std_df"]

# ---------- Upload Client File ----------
uploaded = st.file_uploader("📤 Upload Client SG Excel File", type=["xlsx"])

if uploaded:
    try:
        raw_client_df = pd.read_excel(uploaded)
        client_df = normalize_dataframe(raw_client_df)
        st.session_state["client_df"] = client_df
        st.success("✅ Client file loaded successfully!")
    except Exception as e:
        st.error(f"❌ Failed to read uploaded file: {e}")
        st.stop()

if "client_df" not in st.session_state:
    st.info("⬆️ Please upload a client file to continue.")
    st.stop()

client_df = st.session_state["client_df"]

# ---------- Lightweight summary using differences only ----------
# ---------- Compute differences ONCE and cache in session_state ----------
if "diff_results" not in st.session_state:
    with st.spinner("Computing differences..."):
        only_in_std, only_in_client, diff_table = compute_differences(std_df, client_df)
        st.session_state["diff_results"] = {
            "only_in_std": only_in_std,
            "only_in_client": only_in_client,
            "diff_table": diff_table
        }
else:
    only_in_std = st.session_state["diff_results"]["only_in_std"]
    only_in_client = st.session_state["diff_results"]["only_in_client"]
    diff_table = st.session_state["diff_results"]["diff_table"]


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

# -----------------------------
# Build Top 10 SGs by total difference count
# -----------------------------
def count_difference_items(std_val, client_val):
    """Return total number of missing + extra items."""
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

    missing = std_items - client_items
    extra = client_items - std_items

    return len(missing) + len(extra)


def build_sg_diff_summary(diff_df):
    """Aggregate all differences per SG and return ranked summary."""
    summary = {}

    for _, row in diff_df.iterrows():
        sg = row["SG Name"]
        std_val = row["Standard Value"]
        client_val = row["Client Value"]

        diff_count = count_difference_items(std_val, client_val)

        if sg not in summary:
            summary[sg] = 0
        summary[sg] += diff_count

    # Convert to DataFrame
    summary_df = (
        pd.DataFrame(
            [{"Security Group": sg, "Total Differences": c} for sg, c in summary.items()]
        )
        .sort_values("Total Differences", ascending=False)
        .reset_index(drop=True)
    )

    return summary_df


# -----------------------------
# Build Top 10 SGs by total difference count
# -----------------------------
def count_difference_items(std_val, client_val):
    """Return total number of missing + extra items."""
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

    missing = std_items - client_items
    extra = client_items - std_items

    return len(missing) + len(extra)


def build_sg_diff_summary(diff_df):
    """Aggregate all differences per SG and return ranked summary."""
    summary = {}

    for _, row in diff_df.iterrows():
        sg = row["SG Name"]
        std_val = row["Standard Value"]
        client_val = row["Client Value"]

        diff_count = count_difference_items(std_val, client_val)

        if sg not in summary:
            summary[sg] = 0
        summary[sg] += diff_count

    summary_df = (
        pd.DataFrame(
            [{"Security Group": sg, "Total Differences": c} for sg, c in summary.items()]
        )
        .sort_values("Total Differences", ascending=False)
        .reset_index(drop=True)
    )

    return summary_df

# -----------------------------
# Display the real Top 10 preview
# -----------------------------
st.subheader("🔍 Preview – Top 10 Security Groups With Maximum Differences")

if diff_table.empty:
    st.info("✔ No differences found.")
else:
    top10 = build_sg_diff_summary(diff_table).head(10)
    st.dataframe(top10)
