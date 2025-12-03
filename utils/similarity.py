import pandas as pd
from difflib import SequenceMatcher

def compute_similarity(df: pd.DataFrame):
    """
    Compares SGs against each other inside the same dataset.
    Useful for detecting SGs that are almost identical.
    """

    results = []

    sg_list = df["SG Name"].tolist()

    for i in range(len(sg_list)):
        for j in range(i + 1, len(sg_list)):
            sg1 = sg_list[i]
            sg2 = sg_list[j]

            row1 = df[df["SG Name"] == sg1].iloc[0]
            row2 = df[df["SG Name"] == sg2].iloc[0]

            # Compare entire row except SG Name
            text1 = " ".join(row1.astype(str).tolist())
            text2 = " ".join(row2.astype(str).tolist())

            similarity = SequenceMatcher(None, text1, text2).ratio()

            results.append({
                "SG 1": sg1,
                "SG 2": sg2,
                "Similarity Score": round(similarity * 100, 2)
            })

    return pd.DataFrame(results)
