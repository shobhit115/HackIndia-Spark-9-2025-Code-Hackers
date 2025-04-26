# VakeelAI: Legal Assistant for Indian Laws

### Overview

VakeelAI is a Legal Assistant that helps users with questions related to Indian Laws. It leverages **Google Gemini**, **Tavily Search API**, and **Langchain** to provide accurate answers. The system uses a combination of **PDF-based question answering**, **web search** from Tavily, and **advanced AI models** for better accuracy.

## Tech Stack

### Frontend
- **React.js**: JavaScript library for building user interfaces, mainly responsible for rendering the UI components and handling user interactions.
- **Next.js**: React framework that enables server-side rendering, static site generation, and building APIs in the same project.

### Backend
- **Python**: Used for handling backend operations like document processing, integrating the Google Gemini API, and managing search queries.
- **Langchain**: A framework for developing applications powered by LLMs (Large Language Models), used to manage question-answering chains.
- **Tavily API**: A search engine for fetching online data to provide real-time answers when document-based data is insufficient.

### Libraries/Frameworks:
- **PyPDF2**: Python library used for reading PDF files and extracting their text.
- **FAISS**: A library for efficient similarity search and clustering of dense vectors, used for storing and querying embedded document texts.
- **Google Generative AI**: The Google Cloud platform's generative AI services to create human-like responses.

---

## Project Structure

### Frontend (`/frontend`)

- **React.js** handles UI elements like input fields, buttons, and display of legal responses.
- **Next.js** is used for server-side rendering and static page generation, optimizing SEO and providing dynamic routes for various parts of the application.

### Backend (`/Model`)

- Python scripts process **PDFs**, handle **Tavily Search API calls**, and run **Google Gemini** to generate legal responses.
- **Langchain** and **FAISS** are used to manage the document text and vector embeddings for better information retrieval.

---

## Features

- **Legal Query Answering**: Responds to questions related to Indian laws, using PDF data and real-time web search via Tavily.
- **PDF Processing**: Extracts legal-related data from multiple PDFs for question answering.
- **Real-time Web Search**: If the answer isn't found in the PDFs, the system fetches information using Tavily's search API.
- **Integration with Google Gemini**: Leverages **Google Gemini** for generating detailed legal answers from both documents and web data.
- **Indian Law-Only Focus**: The assistant is strictly designed to answer queries related to Indian laws, using keywords and intents.
