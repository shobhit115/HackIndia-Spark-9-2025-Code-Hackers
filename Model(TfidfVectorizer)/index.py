import os 
import joblib
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_similarity

def load_index(path="index"):
    vectorizer = joblib.load(os.path.join(path, "vectorizer.pkl"))
    vectors = load_npz(os.path.join(path, "vectors.npz"))
    
    # Load the chunks
    with open(os.path.join(path, "chunks.txt"), "r", encoding="utf-8") as f:
        chunks = f.read().split("<|CHUNK|>\n")
        chunks = [c.strip() for c in chunks if c.strip()]
        
    return vectorizer, vectors, chunks

vectorizer, vectors, chunks = load_index("index")

def search_chunks(question, vectorizer, vectors, chunks, top_k=3):
    query_vec = vectorizer.transform([question])
    similarities = cosine_similarity(query_vec, vectors).flatten()
    top_indices = similarities.argsort()[-top_k:][::-1]
    return [chunks[i] for i in top_indices]

def generate_response(question, relevant_chunks):
    answer = "\n---\n".join(relevant_chunks)
    return f"Based on the documents, here’s what I found:\n\n{answer}"



question = input("Ask a question: ")
relevant = search_chunks(question, vectorizer, vectors, chunks)

from transformers import BartTokenizer, BartForConditionalGeneration

# Initialize tokenizer and model
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")

def summarize_chunks_with_transformers(chunks):
    # Combine all chunks into a single string
    all_text = " ".join(chunks)
    
    # Tokenize the text
    inputs = tokenizer(all_text, return_tensors="pt", truncation=True, max_length=1024)
    
    # Check if the input exceeds the model's token limit
    if inputs["input_ids"].size(1) > 1024:
        print("Text exceeds token limit, truncating...")
        inputs["input_ids"] = inputs["input_ids"][:, :1024]  # Truncate the input to fit the token limit

    # Generate summary
    summary_ids = model.generate(inputs["input_ids"], num_beams=4, min_length=100, max_length=200, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    return summary

# Example usage

summary = summarize_chunks_with_transformers(relevant)
print(summary)