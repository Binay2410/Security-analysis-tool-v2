import pandas as pd

def compute_differences(std_df, client_df):
    """Compares standard SG list with client SG list."""
    std_set = set(std_df["SG Name"])
    client_set = set(client_df["SG Name"])

    only_in_std = sorted(list(std_set - client_set))
    only_in_client = sorted(list(client_set - std_set))

    # Row-level differences
    common = std_set.intersection(client_set)

    diff_rows = []
    for sg in common:
        std_row = std_df[std_df["SG Name"] == sg].iloc[0]
        client_row = client_df[client_df["SG Name"] == sg].iloc[0]

        row_diff = {}
        for col in std_df.columns:
            if col in client_df.columns:
                if str(std_row[col]) != str(client_row[col]):
                    row_diff[col] = {"standard": std_row[col], "client": client_row[col]}

        if row_diff:
            diff_rows.append({
                "SG Name": sg,
                "Differences": row_diff
            })

    diff_df = pd.DataFrame(diff_rows)

    return only_in_std, only_in_client, diff_df
