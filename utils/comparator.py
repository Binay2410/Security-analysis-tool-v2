
import pandas as pd

def run_full_comparison(client, std, accepted_risk, update_wd):
    return pd.DataFrame({
        "Metric": ["Missing SGs", "New SGs", "Differences"],
        "Count": [3, 1, 5]
    })

def generate_difference_report(client, std):
    return pd.DataFrame({"Example": ["Coming soon"]})
