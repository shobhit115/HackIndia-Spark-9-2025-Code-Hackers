import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from io import BytesIO
import re
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from docx import Document

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import google.generativeai as genai

# Load API keys
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Tavily search
def tavily_search(query):
    from tavily import TavilyClient
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    response = tavily_client.get_search_context(query)
    return response

# File processing
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

def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=15000, chunk_overlap=1500)
    return splitter.split_text(text)

def save_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def load_or_create_vector_store_from_folder(folder_path):
    if not os.path.exists("faiss_index"):
        all_text = get_all_pdf_texts(folder_path)
        chunks = get_text_chunks(all_text)
        save_vector_store(chunks)

# QA Chain
def get_conversational_chain(user_type,legal_area,selected_language,history_pq=None):
    # print(history_pq,user_type,legal_area,selected_language)
    prompt_template = """
    You are a knowledgeable and reliable legal assistant specialized in Indian laws such as the IPC, RTI, labor laws, and other regulations. You are capable of understanding and responding to legal queries in multiple languages. If the user requests an answer in a specific language, you should provide your response in that language.
    User Type {user_type} is simple user or any Advocate Judge.
    legal Area which is select by your user {legal_area}.
    User Language Select {selected_language}.
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

    MOST IMP - Do not return unredable TEXT

   - Generate only  in HTMl and well structured HTML
   - Do not add ```html``` like extra things.
    - Generate whole data in well structure HTML and best manner in HTML Tags.

    NO MARKDOWN ONLY HTML

    
    Generate content in HTML format with well-structured tags. The content should include:

Headings: Use different levels of headings like <h1>, <h2>, etc., for sections and sub-sections.

Paragraphs: Include multiple <p> tags with descriptive content or placeholder text.

Lists: Use ordered (<ol>) or unordered (<ul>) lists with several <li> items.

Links: Add a few links using <a> tags, making sure they have href attributes with dummy URLs.

Images: Insert a couple of placeholder images using the <img> tag with src attributes pointing to example image URLs.

Tables: Include a small <table> with headers and rows, using <th>, <tr>, and <td> tags.

Blockquotes: Use <blockquote> for a quote from a source.

Strong and Emphasis: Add emphasis to some words using <strong> and <em> tags.

Ensure that the generated content makes proper use of HTML tags and is semantically correct, but don’t generate a complete HTML document (no <html>, <head>, or <body> tags). Just focus on the structured content in HTML.
    Answer (in the requested language, with citations if applicable):
    """

    # If HistoryPQ is not None, add it to the context
    if history_pq:
        context = f"Previous Question: {history_pq}\n"
    else:
        context = "No previous question available.\n"

    # Template variables to pass to the model
    prompt = PromptTemplate(
    template=prompt_template,
    input_variables=[
        "user_type",
        "legal_area",
        "selected_language", 
        "context",
        "question"
    ]
)
    
    # Use the current context and the new question for the LLM
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)



# Document Analyzer
def analyze_legal_document(document_text):
    prompt = f"""
    You are an AI legal assistant. The following text is from a legal document. Identify and extract any relevant legal entities, clauses, or provisions, and summarize the main points:

    Document:
    {document_text}

    Instructions:
    - Extract any references to legal entities (e.g., parties involved, dates, and legal terminology).
    - Identify important clauses or provisions, such as terms of agreement, liabilities, rights, etc.
    - Provide a summary of the document's key legal aspects in simple terms.
   - Do not add ```html``` like extra things.

   
    MOST IMP - Do not return unredable TEXT
    
       - Generate only  in HTMl and well structured HTML
          NO MARKDOWN ONLY HTML

          Generate content in HTML format with well-structured tags. The content should include:

Headings: Use different levels of headings like <h1>, <h2>, etc., for sections and sub-sections.

Paragraphs: Include multiple <p> tags with descriptive content or placeholder text.

Lists: Use ordered (<ol>) or unordered (<ul>) lists with several <li> items.

Links: Add a few links using <a> tags, making sure they have href attributes with dummy URLs.

Images: Insert a couple of placeholder images using the <img> tag with src attributes pointing to example image URLs.

Tables: Include a small <table> with headers and rows, using <th>, <tr>, and <td> tags.

Blockquotes: Use <blockquote> for a quote from a source.

Strong and Emphasis: Add emphasis to some words using <strong> and <em> tags.

Ensure that the generated content makes proper use of HTML tags and is semantically correct, but don’t generate a complete HTML document (no <html>, <head>, or <body> tags). Just focus on the structured content in HTML.
    - Generate whole data in well structure HTML and best manner in HTML Tags.

      - Do not add ```html``` like extra things.
    """

    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)
    return model.invoke(prompt).content


# Question Handler
def handle_question(user_question,user_type, legal_area, selected_language,history_pq=None):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = vector_store.similarity_search(user_question)
    
    # Pass the previous question (history_pq) if available
    chain = get_conversational_chain(user_type,legal_area,selected_language,history_pq=history_pq)
    
    response = chain({"input_documents": docs, "question": user_question, "legal_area": legal_area, "selected_language":selected_language, "user_type": user_type}, return_only_outputs=True)
    answer = response["output_text"]

    # If the answer is short or uncertain, we look for additional web data
    if len(answer.split()) < 30 or "i don't know" in answer.lower():
        tavily_context = tavily_search(user_question)
        if isinstance(tavily_context, dict) and 'content' in tavily_context:
            web_data = tavily_context['content']
        elif isinstance(tavily_context, str):
            web_data = tavily_context
        else:
            web_data = "No useful data found."
            
        prompt = f"""
        You are a legal assistant specialized in Indian laws (IPC, RTI, labor laws, and other regulations). Use the following web search results to provide a detailed, legally accurate, and easy-to-understand answer to the user's question.
        Previous Question: {history_pq}
        User Type {user_type} is simple user or any Advocate Judge
        legal Area which is select by your user {legal_area} like 
        User Language Select {selected_language}
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


    MOST IMP - Do not return unredable TEXT

    - Generate whole data in well structure HTML and best manner in HTML Tags.
    - Generate only  in HTMl and well structured HTML
        - Do not add ```html``` like extra things.
           NO MARKDOWN ONLY HTML

           Generate content in HTML format with well-structured tags. The content should include:

Headings: Use different levels of headings like <h1>, <h2>, etc., for sections and sub-sections.

Paragraphs: Include multiple <p> tags with descriptive content or placeholder text.

Lists: Use ordered (<ol>) or unordered (<ul>) lists with several <li> items.

Links: Add a few links using <a> tags, making sure they have href attributes with dummy URLs.

Images: Insert a couple of placeholder images using the <img> tag with src attributes pointing to example image URLs.

Tables: Include a small <table> with headers and rows, using <th>, <tr>, and <td> tags.

Blockquotes: Use <blockquote> for a quote from a source.

Strong and Emphasis: Add emphasis to some words using <strong> and <em> tags.

Ensure that the generated content makes proper use of HTML tags and is semantically correct, but don’t generate a complete HTML document (no <html>, <head>, or <body> tags). Just focus on the structured content in HTML.
  - Do not add ```html``` like extra things.
        **Final Answer** (with legal references if possible):
        
        """
        
        gemini_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.4)
        gemini_response = gemini_model.invoke(prompt)
        return {
            "source": "Internet",
            "ai_answer": gemini_response.content
        }
    else:
        return {
            "source": "Dataset",
            "ai_answer": answer
        }

def extract_multipart_data(content_type, body):
    """
    Parses multipart/form-data manually and extracts the file content and filename.
    Returns: (filename, file_bytes)
    """
    match = re.search(r'boundary=(.*)', content_type)
    if not match:
        return None, None

    boundary = match.group(1).encode()
    parts = body.split(b'--' + boundary)

    for part in parts:
        if b'Content-Disposition' in part and b'name="file"' in part:
            headers, file_data = part.split(b'\r\n\r\n', 1)
            file_data = file_data.rsplit(b'\r\n', 1)[0]  # Remove the trailing \r\n
            filename_match = re.search(rb'filename="(.+?)"', headers)
            if filename_match:
                filename = filename_match.group(1).decode()
                return filename, file_data

    return None, None

# Document Uploader & Analyzer
def parse_and_analyze_file(file_bytes, content_type):
    from PyPDF2 import PdfReader
    from docx import Document

    text = ""
    if content_type == "application/pdf":
        reader = PdfReader(BytesIO(file_bytes))
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(BytesIO(file_bytes))
        text = "\n".join([p.text for p in doc.paragraphs])
    else:
        return {"error": "Unsupported file format"}

    result = analyze_legal_document(text)
    return {
        "source": "AI Analysis",
        "ai_answer": result
    }



# HTTP Server
class LegalAssistantHandler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_POST(self):
        
        content_length = int(self.headers['Content-Length'])
        content_type = self.headers['Content-Type']
        body = self.rfile.read(content_length)

        if self.path == '/query':
            if content_type.startswith("multipart/form-data"):
                # Extract boundary
                match = re.search(r'boundary=(.*)$', content_type)
                if not match:
                    self.send_error(400, "Bad request syntax: missing boundary")
                    return
                boundary = match.group(1).encode()
                parts = body.split(b'--' + boundary)
                form_data = {}
                filename = None
                file_bytes = None

                for part in parts:
                    if b'Content-Disposition' in part:
                        disposition = part.split(b'\r\n', 1)[0]
                        name_match = re.search(rb'name="([^"]*)"', disposition)
                        if name_match:
                            name = name_match.group(1).decode()
                            value_start = part.find(b'\r\n\r\n') + 4
                            value = part[value_start:].rstrip(b'\r\n')
                            form_data[name] = value.decode()

                            if b'filename=' in disposition:
                                filename_match = re.search(rb'filename="([^"]*)"', disposition)
                                if filename_match:
                                    filename = filename_match.group(1).decode()
                                    file_bytes = value

                user_question = form_data.get("question", "")
                history_pq = form_data.get("history_pq", None)
                user_type = form_data.get("user_type", "user")
                legal_area = form_data.get("legal_area", "General Law")
                selected_language = form_data.get("selected_language", "English")
                
                # print("$", user_question,history_pq,user_type,legal_area,selected_language)

                if filename and file_bytes:
                    upload_folder = "uploads"
                    os.makedirs(upload_folder, exist_ok=True)
                    file_path = os.path.join(upload_folder, filename)
                    with open(file_path, "wb") as f:
                        f.write(file_bytes)

                    # Load text and generate vector store
                    all_text = get_all_pdf_texts(upload_folder)
                    chunks = get_text_chunks(all_text)
                    save_vector_store(chunks)
                    os.remove(file_path)


            else:  # Only JSON input
                json_data = json.loads(body.decode())
                user_question = json_data.get("question", "")
                history_pq = json_data.get("history_pq", None)
                user_type = json_data.get("user_type", "user")
                legal_area = json_data.get("legal_area", "General Law")
                selected_language = json_data.get("selected_language", "English")
                # print(user_question,history_pq,user_type,legal_area,selected_language)

            try:
                result = handle_question(user_question, user_type, legal_area, selected_language, history_pq)
                response = json.dumps(result).encode()
                print("\n\n",response)
                self.send_response(200)
                self._set_cors_headers()  # Add CORS headers
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(response)
            except Exception as e:
                self.send_error(500, f"Internal Error: {str(e)}")

        else:
            self.send_error(404, "Endpoint Not Found")


# Boot microservice
def run(server_class=HTTPServer, handler_class=LegalAssistantHandler, port=8080):
    load_or_create_vector_store_from_folder("data")  # Only needs to run once
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Running Legal AI Microservice on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()




#python main.py



#curl -X POST http://localhost:8000/query -H "Content-Type: multipart/form-data" -F "file=@C:/Users/tusha/Downloads/IIF1.pdf" -F "payload={\"question\":\"Given the more detail\",\"history_pq\":\"What is FIR?\",\"user_type\":\"user\",\"legal_area\":\"IPC\",\"selected_language\":\"English\"}"

#curl -X POST http://localhost:8080/query -H "Content-Type: application/json" -d "{\"question\":\"Given the more detail\",\"history_pq\":\"What is FIR?\",\"user_type\":\"user\",\"legal_area\":\"IPC\",\"selected_language\":\"English\"}"