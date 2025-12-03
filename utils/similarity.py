import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SG_COL = "Domains granted to Security Group"

def compute_similarity(df):
    if SG_COL not in df.columns:
        raise KeyError(f"Missing required column: {SG_COL}")

    permission_columns = [c for c in df.columns if c != SG_COL]

    # Build text per SG by concatenating all permission values
    sg_texts = []
    sg_names = list(df[SG_COL])

    for _, row in df.iterrows():
        combined = []
        for col in permission_columns:
            cell = row[col]
            if pd.notna(cell):
                combined.append(str(cell))
        sg_texts.append(" | ".join(combined))

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(sg_texts)

    # Cosine similarity matrix
    similarity_matrix = cosine_similarity(tfidf_matrix)

    results = []
    n = len(sg_names)

    for i in range(n):
        for j in range(i + 1, n):
            score = similarity_matrix[i][j]

            if score >= 0.35:  # threshold
                results.append({
                    "SG1": sg_names[i],
                    "SG2": sg_names[j],
                    "Similarity Score": round(float(score), 4)
                })

    return pd.DataFrame(results)
