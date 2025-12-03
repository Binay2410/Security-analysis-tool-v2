import pandas as pd

def compute_differences(std_df: pd.DataFrame, client_df: pd.DataFrame):
    """
    Computes:
    - SGs missing in client
    - SGs only in client
    - Detailed differences
    """

    std_set = set(std_df["SG Name"])
    client_set = set(client_df["SG Name"])

    only_in_std = sorted(list(std_set - client_set))
    only_in_client = sorted(list(client_set - std_set))

    # Row-level detailed diff
    diff_rows = []

    common = std_set.intersection(client_set)

    for sg in common:
        std_row = std_df[std_df["SG Name"] == sg].iloc[0]
        client_row = client_df[client_df["SG Name"] == sg].iloc[0]

        for col in std_df.columns:
            if col == "SG Name":
                continue

            if str(std_row[col]) != str(client_row[col]):
                diff_rows.append({
                    "SG Name": sg,
                    "Column": col,
                    "Standard Value": std_row[col],
                    "Client Value": client_row[col]
                })

    diff_table = pd.DataFrame(diff_rows)

    return only_in_std, only_in_client, diff_table
