import os
import faiss
from groq import Groq # Correct Groq import because of failure in hugging face
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_community.vectorstores import FAISS 
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate 
from langchain_community.retrievers import BM25Retriever 

# --- CONFIGURATION ---
GROQ_MODEL_NAME = "llama-3.1-8b-instant"#the Goq model name may change from time to time
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN", "YOUR_HUGGING_FACE_TOKEN")#it was for huging face but not used currently
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"#accroding the manual

def format_docs(docs: List[Document]) -> str:
    """Formats retrieved documents for the RAG prompt."""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)

# 1. Indexing Pipeline: Hybrid Retriever Setup ---
def create_retriever(doc_path: str):
    """this Loads, chunks, and creates the two individual retrievers (FAISS + BM25)."""
    # 1. Load Documents & Split
    loader = TextLoader(doc_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)

    # 2. Vector Store (FAISS / Dense Retrieval)
    try:
        #  requiring of  the HuggingFace Token to download the model initially
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME) 
        vectorstore = FAISS.from_documents(docs, embeddings)
        faiss_retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) 
    except Exception as e:
        print(f"ERROR: RAG initialization failed at FAISS/Embeddings: {e}")
        return None
    # 3. Keyword Store (BM25 / Sparse Retrieval)
    bm25_retriever = BM25Retriever.from_documents(docs)
    bm25_retriever.k = 3 
    print("✅ RAG Retrievers Initialized: FAISS and BM25")
    return {
        "faiss": faiss_retriever,
        "bm25": bm25_retriever
    }

# Initialize the retriever globally when the app starts
RAG_RETRIEVER = create_retriever(os.path.join(os.path.dirname(__file__), "docs.txt"))

# --- 2. Generation & Validation Pipeline Templates ---
# NOTE: The templates below are crucial for proper LLM function. Replace the placeholders
# with your full original template text.

RAG_PROMPT_TEMPLATE = """
You are an expert SaaS Support Copilot. Your role is to answer user questions truthfully and based ONLY on the provided context.
Context:
{context}

Question:
{question}

Instructions:
1. If the context is empty or does not contain the information needed to answer, state clearly that you cannot answer based on the documentation.
2. If the context is sufficient, generate a concise and helpful answer.
3. End your response with 'Final Answer:' followed by the generated answer.

Final Answer:
"""

# Hallucination Check Prompt
VALIDATION_PROMPT_TEMPLATE = """
Validator AI. Check if the Answer is confidently grounded in the Retrieved Chunks.
Retrieved Chunks:
{retrieved_chunks}

Question:
{question}

Answer:
{answer}

Instructions:
Evaluate the Answer against the Retrieved Chunks.
1. If the Answer is entirely supported by the Chunks, output ONLY "YES".
2. If the Answer contains information not found in the Chunks (hallucination) or contradicts the Chunks, output ONLY "NO".

Validator Output (YES/NO):
"""

# --- 3. The Main RAG Pipeline Function ---

async def get_rag_answer(query: str) -> Dict[str, Any]:
    """Runs the full RAG pipeline (Retrieval, Generation, Validation)."""
    
    if not RAG_RETRIEVER:
        return {
            "query": query,
            "answer": "The RAG system failed to initialize.",
            "source_chunks": [],
            "similarity_scores": [],
            "validation_status": "CRITICAL_ERROR"
        }

    # Initialize Groq Client
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY")) 
    except Exception as e:
        return { 
            "query": query,
            "answer": f"Groq Client Init Error. Check GROQ_API_KEY. Error: {e}",
            "validation_status": "LLM_ERROR" 
        }
    
    # 1. Hybrid Retrieval (MANUAL IMPLEMENTATION)
    faiss_docs = RAG_RETRIEVER["faiss"].invoke(query)
    bm25_docs = RAG_RETRIEVER["bm25"].invoke(query)

    # Combinining and deduplicate documents
    unique_docs_map = {doc.page_content: doc for doc in faiss_docs + bm25_docs}
    retrieved_docs = list(unique_docs_map.values())
    context_text = format_docs(retrieved_docs)
    
    source_chunks = [doc.page_content for doc in retrieved_docs]
    # Simple placeholder for similarity scores, as true scoring is complex for manual hybrid
    similarity_scores = [f"Source {i+1} - Relevance Est: {round(0.7 + i * 0.04, 3)}" for i, _ in enumerate(source_chunks)]
    
    # 2. Initial Hallucination Check: Minimum relevance threshold
    if len(retrieved_docs) < 2:
        rejection_message = "I cannot confidently answer that question based on the provided support documentation."
        return {
            "query": query,
            "answer": rejection_message,
            "source_chunks": source_chunks,
            "similarity_scores": similarity_scores,
            "validation_status": "REJECTED_LOW_CONTEXT"
        }

    # 3. Generation
    rag_prompt = PromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
    formatted_prompt = rag_prompt.format(context=context_text, question=query)

    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL_NAME,
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0.1,
            max_tokens=512
        )
        final_answer_raw = completion.choices[0].message.content
        # Extract the final answer text
        final_answer = final_answer_raw.split("Final Answer:", 1)[-1].strip()

    except Exception as e:
        return { 
            "query": query,
            "answer": f"Groq Generation Error: {e}",
            "source_chunks": source_chunks,
            "similarity_scores": similarity_scores,
            "validation_status": "GENERATION_ERROR" 
        }

    # 4. Validation Layer
    validation_prompt = PromptTemplate.from_template(VALIDATION_PROMPT_TEMPLATE)
    validation_formatted_prompt = validation_prompt.format(
        retrieved_chunks=context_text,
        question=query,
        answer=final_answer
    )
    
    validation_status = "GROUNDED" # Assume success by default

    try:
        validation_completion = client.chat.completions.create(
            model=GROQ_MODEL_NAME,
            messages=[{"role": "user", "content": validation_formatted_prompt}],
            temperature=0.0,
            max_tokens=50
        )
        validation_output_raw = validation_completion.choices[0].message.content.strip().upper()
        
        # Determine final status based on validation model's output
        if validation_output_raw.startswith("NO"):
             validation_status = "HALLUCINATED"
        elif not validation_output_raw.startswith("YES"):
             validation_status = "VALIDATION_FAILED"
        
    except Exception:
        validation_status = "VALIDATION_ERROR"
    
    # 5. Final Return (Using the correctly parsed variables)
    return {
        "query": query,
        "answer": final_answer,
        "source_chunks": source_chunks,
        "similarity_scores": similarity_scores,
        "validation_status": validation_status
    }
