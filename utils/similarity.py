import pandas as pd
from itertools import combinations

def _row_items(row: pd.Series):
    """
    Build a set of permission 'items' from all permission columns in a row.
    Split on newlines, strip, ignore empty.
    """
    items = set()
    for col, val in row.items():
        if col == "SG Name":
            continue
        if pd.isna(val):
            continue
        # each cell may contain multiple entries separated by newlines
        for part in str(val).splitlines():
            part = part.strip()
            if part:
                items.add(part)
    return items

def compute_similarity(df: pd.DataFrame, threshold: float = 0.90) -> pd.DataFrame:
    """
    Jaccard similarity between SGs based on permission items.
    Only returns pairs with similarity >= threshold.
    """

    df = df.copy()
    sg_names = df["SG Name"].tolist()
    item_sets = [_row_items(row) for _, row in df.iterrows()]

    rows = []
    n = len(sg_names)

    for i, j in combinations(range(n), 2):
        a = item_sets[i]
        b = item_sets[j]

        if not a and not b:
            continue

        inter = len(a & b)
        union = len(a | b)

        if union == 0:
            continue

        sim = inter / union

        if sim >= threshold:
            rows.append({
                "SG 1": sg_names[i],
                "SG 2": sg_names[j],
                "Similarity": round(sim * 100, 2)
            })

    return pd.DataFrame(rows)
