# VakeelAI: Legal Assistant for Indian Laws ⚖️🇮🇳

### Overview

VakeelAI is a **Legal Assistant** that helps users with questions related to **Indian Laws**. It leverages **Google Gemini**, **Tavily Search API**, and **Langchain** to provide accurate answers. The system uses a combination of **PDF-based question answering**, **web search** from Tavily, and **advanced AI models** for better accuracy. 📜💡

## 🧰 Tech Stack

### 🖥️ Frontend
- **[Streamlit](https://streamlit.io/)** ⚡  
  - Python-based framework for building interactive web apps.  
  - Handles file upload, search input, and displaying search results.  
  - No need for additional JavaScript frameworks.

### 🧠 Backend
- **Python** 🐍  
  - Core language for document processing, text chunking, vectorization, and search indexing.

### 📚 Libraries & Frameworks

| Purpose                     | Technology / Library                          | Role                                                        |
|-----------------------------|-----------------------------------------------|-------------------------------------------------------------|
| File handling               | `os` *(Python Standard Library)*              | Read files, manage directories                              |
| PDF text extraction         | [PyPDF2](https://pypi.org/project/PyPDF2/)    | Read and extract text from PDF files                         |
| Text processing & chunking  | Python logic                                  | Break text into overlapping chunks for better retrieval      |
| Vectorization               | [scikit-learn](https://scikit-learn.org/)     | Convert text chunks into numerical vectors (TF-IDF)          |
| Model & data saving         | [joblib](https://joblib.readthedocs.io/), [SciPy](https://scipy.org/) | Save vectorizer and vector matrices efficiently |
| Index building concept      | Information Retrieval                         | Enable fast and accurate text search & retrieval             |


### ✅ Why This Stack
- Lightweight and fast — no external AI frameworks required  
- Fully Python-based → easy to maintain and extend  
- Ideal for search-based document applications  
- Simple deployment with Streamlit 🚀

## Features 🌟

- **Legal Query Answering**: Responds to questions related to Indian laws, using PDF data and real-time web search via Tavily. 📚
- **PDF Processing**: Extracts legal-related data from multiple PDFs for question answering. 📄➡️🔍
- **Real-time Web Search**: If the answer isn't found in the PDFs, the system fetches information using Tavily's search API. 🌍
- **Integration with Google Gemini**: Leverages **Google Gemini** for generating detailed legal answers from both documents and web data. 🧠🤖
- **Indian Law-Only Focus**: The assistant is strictly designed to answer queries related to Indian laws, using keywords and intents. 🇮🇳⚖️
