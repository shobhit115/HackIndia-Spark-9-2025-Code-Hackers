import os
from PyPDF2 import PdfReader

def extract_pdf_text(folder_path):
    all_text = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            reader = PdfReader(os.path.join(folder_path, filename))
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    all_text += text
    return all_text


def split_text(text, chunk_size=2000, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


import joblib
from scipy.sparse import save_npz

def build_and_save_index(chunks, path="index"):
    os.makedirs(path, exist_ok=True)
    vectorizer = TfidfVectorizer().fit(chunks)
    vectors = vectorizer.transform(chunks)
    
    # Save the vectorizer
    joblib.dump(vectorizer, os.path.join(path, "vectorizer.pkl"))
    
    # Save the vector matrix
    save_npz(os.path.join(path, "vectors.npz"), vectors)
    
    # Save the chunks
    with open(os.path.join(path, "chunks.txt"), "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(chunk + "\n<|CHUNK|>\n")
    return vectorizer, vectors


text = extract_pdf_text("scr")
chunks = split_text(text)
vectorizer, vectors = build_and_save_index(chunks)
