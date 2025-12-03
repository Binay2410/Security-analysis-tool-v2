import pandas as pd

SG_KEY = "Domains granted to Security Group"

def normalize_key(df):
    df[SG_KEY] = (
        df[SG_KEY]
        .astype(str)
        .str.strip()
        .str.lower()
    )
    return df

def compute_differences(client_df, standard_df):
    # Normalize SG Key
    client_df = client_df.copy()
    standard_df = standard_df.copy()

    client_df = normalize_key(client_df)
    standard_df = normalize_key(standard_df)

    # Identify SG sets
    client_sg = set(client_df[SG_KEY])
    standard_sg = set(standard_df[SG_KEY])

    # Determine categories
    client_only = client_sg - standard_sg
    standard_only = standard_sg - client_sg
    in_both = client_sg & standard_sg

    # Differences inside SG
    difference_rows = []

    permission_columns = [c for c in client_df.columns if c != SG_KEY]

    for sg in in_both:
        c_row = client_df[client_df[SG_KEY] == sg].iloc[0]
        s_row = standard_df[standard_df[SG_KEY] == sg].iloc[0]

        for col in permission_columns:
            c_val = c_row[col]
            s_val = s_row[col]

            if pd.isna(c_val) and pd.isna(s_val):
                continue

            if str(c_val) != str(s_val):
                difference_rows.append({
                    SG_KEY: sg,
                    "Permission": col,
                    "Client Value": c_val,
                    "Standard Value": s_val
                })

    client_only_list = sorted(list(client_only))
    standard_only_list = sorted(list(standard_only))
    differences_df = pd.DataFrame(difference_rows)

    return client_only_list, standard_only_list, differences_df
