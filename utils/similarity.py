import pandas as pd
from difflib import SequenceMatcher

def compute_similarity(df, threshold=0.60):
    """Find SGs with similar descriptions or names."""
    results = []

    df = df.fillna("")

    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            sg1 = df.iloc[i]
            sg2 = df.iloc[j]

            text1 = f"{sg1['SG Name']} {sg1['Description']}"
            text2 = f"{sg2['SG Name']} {sg2['Description']}"

            score = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

            if score >= threshold:
                results.append({
                    "SG1": sg1["SG Name"],
                    "SG2": sg2["SG Name"],
                    "Similarity Score": round(score, 3)
                })

    return pd.DataFrame(results)
