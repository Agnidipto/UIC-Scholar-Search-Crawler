from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

def compute_tfidf(tokens: list, top_n: int = 20):
    docs = [' '.join(tokens)]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(docs)
    scores = zip(vectorizer.get_feature_names_out(), tfidf_matrix.toarray()[0])
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)[:top_n]
    return pd.DataFrame(sorted_scores, columns=['keyword', 'tfidf'])