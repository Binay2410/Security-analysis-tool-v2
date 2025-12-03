import pandas as pd

# The FIRST column is ALWAYS the SG name.
SG_COL = "Domains granted to Security Group"

def compute_differences(std_df, client_df):

    if SG_COL not in std_df.columns or SG_COL not in client_df.columns:
        raise KeyError(
            f"Required column '{SG_COL}' not found.\n\n"
            f"Your file columns are:\n{list(std_df.columns)}"
        )

    # Convert to sets
    std_set = set(std_df[SG_COL].astype(str))
    client_set = set(client_df[SG_COL].astype(str))

    # Only-in checks
    only_in_std = sorted(list(std_set - client_set))
    only_in_client = sorted(list(client_set - std_set))

    # Compare common SG names
    common = std_set.intersection(client_set)

    diff_rows = []
    for sg in common:
        std_row = std_df[std_df[SG_COL] == sg].iloc[0]
        client_row = client_df[client_df[SG_COL] == sg].iloc[0]

        row_diff = {}
        for col in std_df.columns:
            # Skip SG column
            if col == SG_COL:
                continue

            std_val = str(std_row[col]) if pd.notna(std_row[col]) else ""
            client_val = str(client_row[col]) if pd.notna(client_row[col]) else ""

            if std_val != client_val:
                row_diff[col] = {
                    "standard": std_val,
                    "client": client_val
                }

        if row_diff:
            diff_rows.append({
                SG_COL: sg,
                "Differences": row_diff
            })

    return only_in_std, only_in_client, pd.DataFrame(diff_rows)
