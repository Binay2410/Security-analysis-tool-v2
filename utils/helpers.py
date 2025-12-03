import pandas as pd

EXPECTED_COLUMNS = [
    "Domains granted to Security Group",
    "Reports and Tasks - Modify Access",
    "Reports and Tasks - View Access",
    "Integrations - Put Access",
    "Integrations - Get Access",
    "Business Process Types granted to Security Group - Initiate Access",
    "Business Process Types granted to Security Group - Enrichment Access",
    "Business Process Types granted to Security Group - Approve Access",
    "Business Process Types granted to Security Group - View Access",
    "Business Process Types granted to Security Group - View Completed Access"
]

def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure expected columns exist and rename SG column to 'SG Name'.
    """
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise KeyError(f"Missing expected columns: {missing}\nGot: {list(df.columns)}")

    df = df.copy()
    df.rename(columns={"Domains granted to Security Group": "SG Name"}, inplace=True)
    return df
