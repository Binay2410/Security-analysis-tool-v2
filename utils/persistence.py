
import pandas as pd
import os

def load_history():
    def safe_load(path):
        return pd.read_excel(path) if os.path.exists(path) else pd.DataFrame()

    return (
        safe_load("accepted_risk.xlsx"),
        safe_load("update_workday.xlsx"),
        safe_load("duplicate_sg_analysis.xlsx")
    )
