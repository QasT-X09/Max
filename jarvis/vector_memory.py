import faiss
import numpy as np
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer

DB_PATH = "jarvis_memory.db"

vectorizer = TfidfVectorizer()
index = None
texts = []

def load_memory():

    global index, texts

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT user_text FROM history")

    rows = cursor.fetchall()

    conn.close()

    texts = [r[0] for r in rows]

    if not texts:
        return

    X = vectorizer.fit_transform(texts).toarray().astype("float32")

    index = faiss.IndexFlatL2(X.shape[1])

    index.add(X)


def search_similar(query, k=3):

    global index

    if index is None:
        return []

    q = vectorizer.transform([query]).toarray().astype("float32")

    distances, indices = index.search(q, k)

    results = []

    for i in indices[0]:

        if i < len(texts):

            results.append(texts[i])

    return results