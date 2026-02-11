import streamlit as st
import pandas as pd

from utils.helpers import normalize_dataframe
from utils.comparator import compute_differences
from utils.similarity import compute_similarity

# -------------------------------------------------------------------------
# FORCE SIDEBAR TO DISPLAY "Home" INSTEAD OF APP FILENAME
# -------------------------------------------------------------------------
st.set_page_config(
    page_title="Home",
    layout="wide",
    page_icon="🏠"
)

# ----- FORCE SIDEBAR TITLE TO "Home" -----
st.markdown("""
<style>

header[data-testid="stSidebarHeader"] div {
    display: none;
}

header[data-testid="stSidebarHeader"]::after {
    content: "Home";
    font-size: 20px;
    font-weight: 600;
    color: white;
    padding-left: 15px;
}

</style>
""", unsafe_allow_html=True)



# Sidebar label override
st.markdown("""
<style>
/* Replace the sidebar page title (which normally shows filename) */
section[data-testid="stSidebar"] .css-10trblm, 
section[data-testid="stSidebar"] .css-1v0mbdj {
    visibility: hidden;
}
section[data-testid="stSidebar"] .css-10trblm:before, 
section[data-testid="stSidebar"] .css-1v0mbdj:before {
    content: "Home";
    visibility: visible;
    font-weight: 600;
    font-size: 20px;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# TOP HEADER
# -------------------------------------------------------------------------
st.markdown("""
<div style="
    padding: 18px 10px;
    border-bottom: 1px solid #EEE;
    margin-bottom:20px;"
>
    <h1 style="color:#2A61FF; font-size:32px; margin:0;">
        🔐 Security Analysis Tool
    </h1>
    <p style="color:#555; margin-top:4px; font-size:14px;">
        Compare Workday security set-up with industry-standard configuration.
    </p>
</div>
""", unsafe_allow_html=True)


# -------------------------------------------------------------------------
# UPLOAD SECTION
# -------------------------------------------------------------------------
st.markdown("""
<div style="
    background:#F5F7FB;
    padding:20px;
    border-radius:10px;
    border:1px solid #E0E0E0;
    margin-bottom:15px;"
>
<h3 style="margin:0 0 15px 0; color:#333;">📤 Upload Client Security File</h3>
""", unsafe_allow_html=True)

uploaded = st.file_uploader("", type=["xlsx"])

st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------------
# LOAD STANDARD DATA
# -------------------------------------------------------------------------
STANDARD_FILE = "standard_data.xlsx"

if "std_df" not in st.session_state:
    try:
        raw_std = pd.read_excel(STANDARD_FILE)
        st.session_state["std_df"] = normalize_dataframe(raw_std)
    except Exception as e:
        st.error(f"❌ Could not load standard_data.xlsx: {e}")
        st.stop()

std_df = st.session_state["std_df"]


# -------------------------------------------------------------------------
# PROCESS CLIENT FILE
# -------------------------------------------------------------------------
if uploaded and (
    "uploaded_filename" not in st.session_state
    or st.session_state["uploaded_filename"] != uploaded.name
):
    try:
        raw_client_df = pd.read_excel(uploaded)
        client_df = normalize_dataframe(raw_client_df)

        st.session_state["client_df"] = client_df
        st.session_state["uploaded_filename"] = uploaded.name

        # Reset caches
        st.session_state.pop("diff_results", None)
        st.session_state.pop("similarity_results", None)

        st.success("✅ Client file loaded successfully!")

    except Exception as e:
        st.error(f"❌ Failed to load file: {e}")
        st.stop()

if "client_df" not in st.session_state:
    st.info("⬆️ Please upload a client file to continue.")
    st.stop()

client_df = st.session_state["client_df"]


# -------------------------------------------------------------------------
# COMPUTE DIFFERENCES (cached)
# -------------------------------------------------------------------------
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


# -------------------------------------------------------------------------
# SUMMARY CARDS
# -------------------------------------------------------------------------
st.subheader("📊 Summary Overview")

c1, c2, c3 = st.columns(3)

c1.markdown(f"""
<div style="padding:18px; background:#FFF; border-radius:10px;
            box-shadow:0 2px 8px rgba(0,0,0,.08); border:1px solid #EEE;">
    <h3 style="margin:0; font-size:20px; color:#2A61FF;">🛡️ Missing Security Group(s)</h3>
    <p style="font-size:28px; margin:0; font-weight:bold;">{len(only_in_std)}</p>
</div>
""", unsafe_allow_html=True)

c2.markdown(f"""
<div style="padding:18px; background:#FFF; border-radius:10px;
            box-shadow:0 2px 8px rgba(0,0,0,.08); border:1px solid #EEE;">
    <h3 style="margin:0; font-size:20px; color:#FF8C00;">⚙️ Custom Security Group(s)</h3>
    <p style="font-size:28px; margin:0; font-weight:bold;">{len(only_in_client)}</p>
</div>
""", unsafe_allow_html=True)

c3.markdown(f"""
<div style="padding:18px; background:#FFF; border-radius:10px;
            box-shadow:0 2px 8px rgba(0,0,0,.08); border:1px solid #EEE;">
    <h3 style="margin:0; font-size:20px; color:#00A65A;">🔍 Security Group - Differences Found</h3>
    <p style="font-size:28px; margin:0; font-weight:bold;">{len(diff_table)}</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# -------------------------------------------------------------------------
# TOP 10 DIFFERENCES
# -------------------------------------------------------------------------
def count_diff(std_val, client_val):
    std_items = {x.strip() for x in str(std_val).splitlines() if x.strip()}
    client_items = {x.strip() for x in str(client_val).splitlines() if x.strip()}
    return len(std_items - client_items) + len(client_items - std_items)


def build_sg_diff_summary(diff_df):
    summary = {}

    for _, row in diff_df.iterrows():
        sg = row["SG Name"]
        diff_count = count_diff(row["Standard Value"], row["Client Value"])
        summary[sg] = summary.get(sg, 0) + diff_count

    return (
        pd.DataFrame(
            [{"Security Group": sg, "Total Differences": count} for sg, count in summary.items()]
        )
        .sort_values("Total Differences", ascending=False)
        .reset_index(drop=True)
    )


st.subheader("🏆 Top 10 SGs With Maximum Differences")

if diff_table.empty:
    st.info("✔ No differences found.")
else:
    top10 = build_sg_diff_summary(diff_table).head(10).reset_index(drop=True)
    top10.insert(0, "S.No", range(1, len(top10) + 1))
    st.dataframe(top10, use_container_width=True, hide_index=True)



st.markdown("➡️ Use the sidebar for full Difference Report and Similarity Analysis.")


# -------------------------------------------------------------------------
# COMPUTE SIMILARITY (cached)
# -------------------------------------------------------------------------
if "similarity_results" not in st.session_state:
    with st.spinner("Computing SG similarity..."):
        st.session_state["similarity_results"] = compute_similarity(client_df)


# -------------------------------------------------------------------------
# FIX SIDEBAR LABEL "app" → "Home"
# -------------------------------------------------------------------------
st.markdown("""
<style>
/* Hide the original label */
section[data-testid="stSidebar"] .css-10trblm, 
section[data-testid="stSidebar"] .css-1v0mbdj {
    visibility: hidden !important;
}

/* Insert our custom label */
section[data-testid="stSidebar"] .css-10trblm:before,
section[data-testid="stSidebar"] .css-1v0mbdj:before {
    content: "Home";
    visibility: visible !important;
    position: relative;
    top: 0;
    left: 0;
    font-size: 20px !important;
    font-weight: 600 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)
