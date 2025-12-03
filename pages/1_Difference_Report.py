# -----------------------------
# Helper: extract difference items with formatting
# -----------------------------
def extract_diff_items_formatted(std_val: str, client_val: str) -> str:
    # Convert to list of stripped lines
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

    # Missing items → RED label
    for item in missing_items:
        formatted.append(f"<span style='color:red; font-weight:bold'>Missing:</span> {item}")

    # Extra items → black label
    for item in extra_items:
        formatted.append(f"<span style='color:black'>Extra:</span> {item}")

    return "<br>".join(formatted)


# -----------------------------
# Build HTML formatted Difference Items column
# -----------------------------
diff_table["Difference Items"] = diff_table.apply(
    lambda row: extract_diff_items_formatted(row["Standard Value"], row["Client Value"]),
    axis=1
)

# -----------------------------
# Final reorder
# -----------------------------
display_cols = [
    "Security Group",
    "Access Type",
    "Standard Value",
    "Client Value",
    "Difference Items"
]

display_df = diff_table[display_cols].copy()

# -----------------------------
# Render using Styler to allow HTML
# -----------------------------
styled_df = display_df.style.format(escape=False)

st.write(styled_df.to_html(), unsafe_allow_html=True)
