import os
import streamlit as st
import requests
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from docx import Document

# Load API keys
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_API_URL = "https://api.tavily.com/search"

# Tavily search
def tavily_search(query):
    from tavily import TavilyClient
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    response = tavily_client.get_search_context(query)
    return response

# Read and combine text from all PDFs in a folder
def get_all_pdf_texts(folder_path):
    all_text = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            pdf_reader = PdfReader(pdf_path)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text
    return all_text

# Split text into chunks
def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=15000, chunk_overlap=1500)
    return splitter.split_text(text)

# Save FAISS vector store
def save_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

# Load or create vector store from all PDFs
def load_or_create_vector_store_from_folder(folder_path):
    if os.path.exists("faiss_index"):
        return
    all_text = get_all_pdf_texts(folder_path)
    chunks = get_text_chunks(all_text)
    save_vector_store(chunks)

# Load conversational QA chain
def get_conversational_chain():
    prompt_template = """
    You are a knowledgeable and reliable legal assistant specialized in Indian laws such as the IPC, RTI, labor laws, and other regulations. You are capable of understanding and responding to legal queries in multiple languages. If the user requests an answer in a specific language, you should provide your response in that language.

    Use the information provided in the context below to generate a detailed, accurate, and clear response. Answer common legal questions concisely and clearly.

    Context:
    {context}

    Question:
    {question}

    Instructions:
    - Provide a clear, concise, and legally accurate answer, especially for common legal queries like "What is FIR?".
    - If the question is about a well-known legal term or process (e.g., FIR, RTI, IPC, etc.), provide a brief and easy-to-understand definition or explanation.
    - If the question specifies a language (e.g., "in Hindi," "in English," etc.), respond in that language.
    - If the context contains direct legal references, quote or cite them precisely.
    - If the answer is not directly available, infer logically from related laws or principles in the context.
    - If multiple interpretations exist, mention them clearly.
    - If the question is vague or unclear, request clarification in the requested language.
    - If the question is outside the scope of Indian laws or insufficient data is available, respond with: "I am unable to provide a legally accurate answer based on the available context."
    - When possible, include citations (e.g., IPC Section 302, RTI Act Section 8) or references to official legal documents.
    - Format your answer clearly using bullet points or short paragraphs if needed.
    - If no language is specified, default to answering in English.
    - Compulsorily You should mention the sources/citations at last of it.. (also)

    Answer (in the requested language, with citations if applicable):
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)

# Handle user input
def user_input_handler(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = vector_store.similarity_search(user_question)
    chain = get_conversational_chain()

    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
    answer = response["output_text"]

    if len(answer.split()) < 30 or "i don't know" in answer.lower():
        with st.status("Searching online databases...", expanded=True) as status:
            st.write("Not enough information in documents. Looking for legal information online...")
            tavily_context = tavily_search(user_question)

            if not tavily_context:
                status.update(label="Search complete", state="error", expanded=False)
                st.error("⚠️ Could not find useful legal information online. Please refine your question.")
                return

            if isinstance(tavily_context, dict) and 'content' in tavily_context:
                web_data = tavily_context['content']
            elif isinstance(tavily_context, str):
                web_data = tavily_context
            else:
                web_data = "No useful data found."
                
            prompt = f"""
            You are a legal assistant specialized in Indian laws (IPC, RTI, labor laws, and other regulations). Use the following web search results to provide a detailed, legally accurate, and easy-to-understand answer to the user's question.

            Web Data (retrieved from trusted legal sources):
            {web_data}

            User's Legal Question:
            {user_question}

            Instructions:
            - You have to structurize the "Web Data (retrieved from trusted legal sources)" provided in a beautiful manner.
            - For common questions of law, even if context is not present, you should answer them by using your own intelligence.
            - **Base your answer on the content in the web data**: Use the data provided in the search results to respond.
            - **Legal Citations**: Always quote or reference specific legal sections or laws (e.g., "IPC Section 420") when applicable.
            - **Common Legal Terms**: For frequently asked questions such as "What is FIR?", provide clear and concise definitions or explanations.
            - **Inference from Data**: If a direct match isn't found in the context, infer logically from the most relevant laws or content available.
            - **Ambiguous Questions**: If the question is vague, ask the user for more details in a polite and clear manner.
            - **Out-of-Scope Questions**: If the question is outside the scope of Indian laws or unrelated to the context, respond with: "This question is beyond the current legal scope I can assist with."
            - **Avoid Hallucinations**: Do not make up data or laws. Stick to the facts provided in the web search results.
            - **Clarity and Simplicity**: Write in clear, simple language that any user can understand. Avoid legal jargon unless necessary, and explain it when used.
            - **Answer Formatting**: Provide your answer in short paragraphs, bullet points, or numbered lists where appropriate to improve readability.
            - Compulsorily You should mention the sources/citations at last of it.. (also)

            **Final Answer** (with legal references if possible):
            """
            gemini_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.4)
            gemini_response = gemini_model.invoke(prompt)
            status.update(label="Search complete", state="complete", expanded=False)

        answer_container = st.container(border=True)
        with answer_container:
            st.markdown(f"<h4 style='color: #4B8BBE;'>🌐 Web Research Result</h4>", unsafe_allow_html=True)
            st.write(gemini_response.content)
    else:
        answer_container = st.container(border=True)
        with answer_container:
            st.markdown(f"<h4 style='color: #4B8BBE;'>📚 Database Result</h4>", unsafe_allow_html=True)
            st.write(answer)

# Function to handle file upload
def upload_file():
    uploaded_file = st.file_uploader("", type=["pdf", "docx"], label_visibility="collapsed")
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(uploaded_file)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
        return text
    return None

# Analyze document for legal entities, clauses, etc.
def analyze_legal_document(document_text):
    prompt = f"""
    You are an AI legal assistant. The following text is from a legal document. Identify and extract any relevant legal entities, clauses, or provisions, and summarize the main points:

    Document:
    {document_text}

    Instructions:
    - Extract any references to legal entities (e.g., parties involved, dates, and legal terminology).
    - Identify important clauses or provisions, such as terms of agreement, liabilities, rights, etc.
    - Provide a summary of the document's key legal aspects in simple terms.
    """
    
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)
    analysis_response = model.invoke(prompt)
    return analysis_response.content

# Custom CSS to inject into the Streamlit app
def local_css():
    st.markdown("""
    <style>
    /* Main theme colors and styling */
    :root {
        --primary-color: #4B8BBE;
        --secondary-color: #306998;
        --accent-color: #FFD43B;
        --background-color: #F5F7FA;
        --text-color: #333333;
        --light-gray: #E0E0E0;
    }
    
    .stApp {
        background-color: var(--background-color);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        font-size: 3rem !important;
        margin-bottom: 0.5rem !important;
        font-weight: 700 !important;
    }
    
    .main-header p {
        font-size: 1.2rem !important;
        opacity: 0.9;
    }
    
    /* Card styling */
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        border-bottom: 1px solid var(--light-gray);
        padding-bottom: 0.75rem;
    }
    
    .card-header h3 {
        margin: 0;
        color: var(--primary-color);
        font-weight: 600;
    }
    
    .card-icon {
        margin-right: 0.75rem;
        font-size: 1.5rem;
        color: var(--primary-color);
    }
    
    /* Button styling */
    .custom-button {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        text-align: center;
        cursor: pointer;
    }
    
    .custom-button:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transform: translateY(-2px);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #E0E0E0;
        padding: 0.75rem;
        transition: all 0.3s ease;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(75, 139, 190, 0.2);
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        border-radius: 10px;
        border: 2px dashed var(--primary-color);
        padding: 2rem;
        background-color: rgba(75, 139, 190, 0.05);
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        background-color: rgba(75, 139, 190, 0.1);
    }
    
    /* Answer container styling */
    .stExpander {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #888;
        font-size: 0.9rem;
    }
    
    /* Custom tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 5px 5px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
    
    /* Legal scale animation */
    @keyframes balance {
        0%, 100% {
            transform: rotate(0deg);
        }
        50% {
            transform: rotate(5deg);
        }
    }
    
    .legal-scale {
        animation: balance 5s ease-in-out infinite;
        transform-origin: top center;
        display: inline-block;
    }
    
    /* Highlight term styling */
    .highlight-term {
        background-color: rgba(255, 212, 59, 0.3);
        padding: 0.1rem 0.3rem;
        border-radius: 3px;
        font-weight: 500;
    }
    
    /* Custom containers */
    .info-container {
        background-color: rgba(75, 139, 190, 0.1);
        border-left: 4px solid var(--primary-color);
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        margin: 1rem 0;
    }
    
    /* Stat counter for document analysis */
    .stat-container {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
        text-align: center;
    }
    
    .stat-item {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        min-width: 100px;
    }
    
    .stat-number {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary-color);
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
    
    /* AI Response styling */
    .ai-response {
        border-radius: 8px;
        background-color: white;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        margin-top: 1rem;
    }
    
    /* Override Streamlit container padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
    }
    
    div[data-testid="stVerticalBlock"] > div:has(div.stButton) {
        text-align: center;
    }

    /* Improve expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: var(--primary-color);
    }
    
    /* Progress indicator */
    .stProgress > div > div > div > div {
        background-color: var(--primary-color);
    }
    
    /* Help tooltip */
    .help-tooltip {
        color: var(--primary-color);
        font-size: 1rem;
        cursor: help;
    }
    
    /* FAQ styling */
    .faq-question {
        font-weight: 600;
        color: var(--primary-color);
        cursor: pointer;
        padding: 0.5rem 0;
    }
    
    /* Citation styling */
    .citation {
        background-color: #f1f1f1;
        border-left: 3px solid var(--primary-color);
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        font-style: italic;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Streamlit App
def streamlit_app():
    st.set_page_config(
        page_title="VakeelAI - Legal Document Analyzer",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Apply custom CSS
    local_css()
    
    # Header section
    st.markdown(
        """
        <div class="main-header">
            <h1>⚖️ VakeelAI</h1>
            <p>Your AI-powered legal assistant for Indian law</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Main content
    tabs = st.tabs(["🏠 Home", "📄 Document Analysis", "❓ Legal Query", "ℹ️ About"])
    
    # Home Tab
    with tabs[0]:
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown(
                """
                <div class="card">
                    <div class="card-header">
                        <span class="card-icon">👋</span>
                        <h3>Welcome to VakeelAI</h3>
                    </div>
                    <p>VakeelAI is your intelligent legal assistant, designed to help you understand Indian laws and analyze legal documents with ease.</p>
                    <p>How can VakeelAI assist you today?</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            col1_1, col1_2 = st.columns(2)
            
            with col1_1:
                st.markdown(
                    """
                    <div class="card">
                        <div class="card-header">
                            <span class="card-icon">📄</span>
                            <h3>Document Analysis</h3>
                        </div>
                        <p>Upload legal documents and get instant analysis of key terms, provisions, and insights.</p>
                        <br>
                        <div style="text-align: center;">
                            <a href="javascript:void(0);" onclick="document.querySelectorAll('[data-baseweb=\'tab\']')[1].click();" class="custom-button">Analyze Documents</a>
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
            with col1_2:
                st.markdown(
                    """
                    <div class="card">
                        <div class="card-header">
                            <span class="card-icon">❓</span>
                            <h3>Legal Queries</h3>
                        </div>
                        <p>Ask any question about Indian laws, regulations, or legal procedures and get accurate answers.</p>
                        <br>
                        <div style="text-align: center;">
                            <a href="javascript:void(0);" onclick="document.querySelectorAll('[data-baseweb=\'tab\']')[2].click();" class="custom-button">Ask Questions</a>
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
            st.markdown(
                """
                <div class="card">
                    <div class="card-header">
                        <span class="card-icon">🔍</span>
                        <h3>Popular Legal Topics</h3>
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
                        <a href="javascript:void(0);" onclick="document.querySelectorAll('[data-baseweb=\'tab\']')[2].click(); setTimeout(() => { document.querySelector('input[aria-label=\'\']').value = 'What is FIR?'; document.querySelector('button[kind=\'primary\']').click(); }, 500);" style="text-decoration: none;">
                            <span class="highlight-term">FIR</span>
                        </a>
                        <a href="javascript:void(0);" onclick="document.querySelectorAll('[data-baseweb=\'tab\']')[2].click(); setTimeout(() => { document.querySelector('input[aria-label=\'\']').value = 'RTI Act explained'; document.querySelector('button[kind=\'primary\']').click(); }, 500);" style="text-decoration: none;">
                            <span class="highlight-term">RTI Act</span>
                        </a>
                        <a href="javascript:void(0);" onclick="document.querySelectorAll('[data-baseweb=\'tab\']')[2].click(); setTimeout(() => { document.querySelector('input[aria-label=\'\']').value = 'IPC 302 explained'; document.querySelector('button[kind=\'primary\']').click(); }, 500);" style="text-decoration: none;">
                            <span class="highlight-term">IPC 302</span>
                        </a>
                        <a href="javascript:void(0);" onclick="document.querySelectorAll('[data-baseweb=\'tab\']')[2].click(); setTimeout(() => { document.querySelector('input[aria-label=\'\']').value = 'Consumer Protection Act'; document.querySelector('button[kind=\'primary\']').click(); }, 500);" style="text-decoration: none;">
                            <span class="highlight-term">Consumer Protection</span>
                        </a>
                        <a href="javascript:void(0);" onclick="document.querySelectorAll('[data-baseweb=\'tab\']')[2].click(); setTimeout(() => { document.querySelector('input[aria-label=\'\']').value = 'Divorce proceedings in India'; document.querySelector('button[kind=\'primary\']').click(); }, 500);" style="text-decoration: none;">
                            <span class="highlight-term">Divorce</span>
                        </a>
                        <a href="javascript:void(0);" onclick="document.querySelectorAll('[data-baseweb=\'tab\']')[2].click(); setTimeout(() => { document.querySelector('input[aria-label=\'\']').value = 'Property rights in India'; document.querySelector('button[kind=\'primary\']').click(); }, 500);" style="text-decoration: none;">
                            <span class="highlight-term">Property Rights</span>
                        </a>
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                """
                <div class="card">
                    <div class="card-header">
                        <span class="card-icon">📊</span>
                        <h3>VakeelAI Features</h3>
                    </div>
                    <ul style="padding-left: 20px;">
                        <li><strong>Document Analysis:</strong> Extract key legal entities and clauses</li>
                        <li><strong>Legal Q&A:</strong> Get answers to your legal questions</li>
                        <li><strong>Multilingual Support:</strong> Ask questions in multiple languages</li>
                        <li><strong>Legal Citations:</strong> Receive properly cited legal information</li>
                        <li><strong>Web Research:</strong> Access online legal databases when needed</li>
                    </ul>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            st.markdown(
                """
                <div class="card">
                    <div class="card-header">
                        <span class="card-icon">⚠️</span>
                        <h3>Disclaimer</h3>
                    </div>
                    <p style="font-size: 0.9rem;">VakeelAI is an AI-powered legal assistant designed to provide information about Indian laws. The information provided should not be considered as legal advice. Always consult a qualified lawyer for professional legal advice.</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            st.markdown(
                """
                <div class="card">
                    <div class="card-header">
                        <span class="card-icon">🔔</span>
                        <h3>Latest Updates</h3>
                    </div>
                    <ul style="padding-left: 20px; font-size: 0.9rem;">
                        <li><strong>April 2025:</strong> Enhanced multilingual support</li>
                        <li><strong>March 2025:</strong> Improved document analysis capabilities</li>
                        <li><strong>February 2025:</strong> Added support for more Indian legal codes</li>
                    </ul>
                </div>
                """, 
                unsafe_allow_html=True
            )
    
    # Document Analysis Tab
    with tabs[1]:
        st.markdown(
            """
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">📄</span>
                    <h3>Document Analysis</h3>
                </div>
                <p>Upload your legal document (PDF or DOCX) for analysis. VakeelAI will extract key legal terms, clauses, and provide a summary.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # File uploader section with improved UI
        st.markdown(
            """
            <div style="text-align: center; padding: 1rem 0;">
                <h4 style="color: #4B8BBE;">Upload Your Document</h4>
                <p style="font-size: 0.9rem; color: #666;">Supported formats: PDF, DOCX</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        document_text = upload_file()
        
        if document_text:
            with st.status("Document processing in progress...") as status:
                st.write("⏳ Extracting text from document...")
                st.write("🔍 Analyzing legal content...")
                st.write("📊 Generating insights...")
                
                analysis_result = analyze_legal_document(document_text)
                status.update(label="Analysis complete! ✅", state="complete", expanded=False)
            
            # Document stats
            doc_words = len(document_text.split())
            doc_chars = len(document_text)
            doc_pages = round(doc_words / 500)  # Rough estimate: ~500 words per page
            
            st.markdown(
                f"""
                <div class="stat-container">
                    <div class="stat-item">
                        <div class="stat-number">{doc_words}</div>
                        <div class="stat-label">Words</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{doc_chars}</div>
                        <div class="stat-label">Characters</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">~{doc_pages}</div>
                        <div class="stat-label">Pages</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Analysis results in tabs
            analysis_tabs = st.tabs(["📝 Summary", "🔍 Full Analysis", "📄 Document Text"])
            
            with analysis_tabs[0]:
                st.markdown(
                    """
                    <div style="margin-top: 1rem;">
                        <h4 style="color: #4B8BBE;">Executive Summary</h4>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                # Extract just the summary portion
                summary_lines = []
                capture = False
                for line in analysis_result.split('\n'):
                    if "summary" in line.lower() or "overview" in line.lower():
                        capture = True
                    if capture and line.strip():
                        summary_lines.append(line)
                    if capture and (len(summary_lines) > 2) and line.strip() == "":
                        break
                
                summary_text = "\n".join(summary_lines) if summary_lines else "Summary section not found in analysis."
                st.markdown(f"<div class='ai-response'>{summary_text}</div>", unsafe_allow_html=True)
            
            with analysis_tabs[1]:
                st.markdown(
                    """
                    <div style="margin-top: 1rem;">
                        <h4 style="color: #4B8BBE;">Full Analysis</h4>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                st.markdown(f"<div class='ai-response'>{analysis_result}</div>", unsafe_allow_html=True)
            
            with analysis_tabs[2]:
                st.markdown(
                    """
                    <div style="margin-top: 1rem;">
                        <h4 style="color: #4B8BBE;">Document Text</h4>
                        <p style="font-size: 0.9rem; color: #666;">Below is the extracted text from your document:</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                st.text_area("", document_text, height=300, label_visibility="collapsed")
    
    # Legal Query Tab
    with tabs[2]:
        st.markdown(
            """
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">❓</span>
                    <h3>Ask a Legal Question</h3>
                </div>
                <p>Ask any question about Indian laws, regulations, or legal procedures. VakeelAI will search through its knowledge base and provide accurate answers with citations.</p>
                <p><small>You can ask questions in multiple languages - VakeelAI will respond in the language you use.</small></p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Initialize or load vector store
        if "pdf_folder" not in st.session_state:
            st.session_state.pdf_folder = "legal_pdfs"  # Default folder for legal PDFs
        
        # Check if vector store exists or needs to be created
        try:
            if not os.path.exists("faiss_index"):
                with st.status("Initializing knowledge base..."):
                    st.write("Loading legal document database...")
                    if os.path.exists(st.session_state.pdf_folder):
                        load_or_create_vector_store_from_folder(st.session_state.pdf_folder)
                        st.success("Knowledge base initialized successfully!")
                    else:
                        st.error(f"Error: The folder {st.session_state.pdf_folder} does not exist.")
        except Exception as e:
            st.error(f"Error initializing knowledge base: {str(e)}")
        
        # Query input
        user_question = st.text_input("Type your legal question here:", placeholder="e.g., What is FIR? or मुझे RTI अधिनियम के बारे में बताएं।")
        
        # Example queries
        with st.expander("Example questions you can ask"):
            st.markdown(
                """
                - What is an FIR and how to file it?
                - Explain Section 302 of IPC
                - What are my rights under RTI Act?
                - How to file a consumer complaint?
                - Labor law provisions for maternity leave
                - Rights of tenants in rental agreements
                - Grounds for divorce in Hindu Marriage Act
                - How to apply for anticipatory bail?
                - Legal procedures for property registration
                - मुझे RTI अधिनियम के बारे में बताएं (Tell me about the RTI Act in Hindi)
                """
            )
        
        # Submit button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_button = st.button("🔍 Get Legal Answer", type="primary")
        
        # Process query
        if submit_button and user_question:
            with st.status("Processing your query..."):
                st.write("Searching knowledge base...")
                user_input_handler(user_question)
    
    # About Tab
    with tabs[3]:
        st.markdown(
            """
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">ℹ️</span>
                    <h3>About VakeelAI</h3>
                </div>
                <p>VakeelAI is an AI-powered legal assistant designed to make Indian laws more accessible to everyone. Our mission is to democratize legal information and empower citizens with knowledge about their rights and legal procedures.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(
                """
                <div class="card">
                    <div class="card-header">
                        <span class="card-icon">🛠️</span>
                        <h3>Technologies Used</h3>
                    </div>
                    <ul style="padding-left: 20px;">
                        <li><strong>Generative AI:</strong> Google Gemini 2.0 model</li>
                        <li><strong>Vector Database:</strong> FAISS for efficient similarity search</li>
                        <li><strong>Web Framework:</strong> Streamlit</li>
                        <li><strong>Web Search:</strong> Tavily API</li>
                        <li><strong>Document Processing:</strong> PyPDF2 and python-docx</li>
                    </ul>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                """
                <div class="card">
                    <div class="card-header">
                        <span class="card-icon">⚠️</span>
                        <h3>Legal Disclaimer</h3>
                    </div>
                    <p>VakeelAI is designed to provide information about Indian laws and legal concepts. It is not a substitute for professional legal advice.</p>
                    <p>The information provided by VakeelAI is for general informational purposes only and should not be construed as legal advice on any subject matter. You should consult with a qualified lawyer for specific advice tailored to your situation.</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        st.markdown(
            """
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">❓</span>
                    <h3>Frequently Asked Questions</h3>
                </div>
                <div style="margin-top: 1rem;">
                    <div class="faq-question">What types of legal documents can VakeelAI analyze?</div>
                    <p>VakeelAI can analyze various legal documents such as contracts, agreements, court orders, legal notices, and other documents in PDF or DOCX format.</p>
                    
                    <div class="faq-question">In which languages can I ask questions?</div>
                    <p>You can ask questions in multiple Indian languages including Hindi, English, Tamil, Telugu, Marathi, Gujarati, Bengali, and more. VakeelAI will respond in the same language you use.</p>
                    
                    <div class="faq-question">How accurate is the information provided by VakeelAI?</div>
                    <p>VakeelAI strives to provide accurate information based on its knowledge base of Indian laws. However, legal interpretations can vary, and laws are subject to change. Always verify critical information with authoritative sources.</p>
                    
                    <div class="faq-question">How is my data handled?</div>
                    <p>Documents uploaded for analysis are processed securely. We do not store your documents or queries for longer than necessary to provide the service. For more details, please refer to our privacy policy.</p>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Footer
    st.markdown(
        """
        <div class="footer">
            <p>© 2025 VakeelAI - Your AI-powered legal assistant | Created with ❤️ for Indian legal system</p>
            <p><small>This is a prototype application for educational purposes only.</small></p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    streamlit_app()