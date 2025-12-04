# NeuroStack GenAI Hackathon Submission: SaaS Support Copilot

**Chosen Problem:** 1) SaaS Support Copilot (RAG System)

---
### **Submission Links**

| Component | URL | Status |
| :--- | :--- | :--- |
| **Live Frontend App URL** | [Your Vercel/Netlify/GH Pages URL] | (Mandatory) |
| **Backend API URL** | [Your Hugging Face Space URL] | (Mandatory) |
| **GitHub Repository** | [Link to this Repo] | (Mandatory) |

---
### 1. Overview & Architecture

This project is a multi-step Retrieval-Augmented Generation (RAG) system built to provide accurate, grounded answers to user support queries based only on internal documentation. It satisfies all mandatory requirements: FastAPI backend with Authentication, React.js frontend, and a production-ready RAG pipeline using only free, open-source tools.

**Tech Stack:**
* **Frontend:** React.js + TypeScript
* **Backend:** FastAPI (Python)
* **LLM/Embedding:** Hugging Face Hub (Zephyr-7b-beta, all-MiniLM-L6-v2)
* **RAG Framework:** LangChain (Python)
* **Vector Store:** FAISS (Free)
* **Deployment:** Hugging Face Spaces (Backend/Docker)

### 2. GenAI Workflow & Innovation

#### **A. Hybrid Retrieval (Retrieval Accuracy Improvement)**
[cite_start]To improve retrieval accuracy beyond simple semantic search, we implemented an **EnsembleRetriever** with a 50/50 weighted approach[cite: 214]:
1.  **Dense Retrieval (FAISS):** Uses the `all-MiniLM-L6-v2` embeddings to find conceptually similar chunks.
2.  **Sparse Retrieval (BM25Okapi):** Uses keyword matching to find exact term matches (e.g., specific error codes like "413 error").
*This hybrid approach ensures both semantic and keyword relevance are considered.*

#### **B. Hallucination Control and Validation Layer**
[cite_start]We implemented two layers of hallucination control[cite: 215, 221, 222]:
1.  **Relevance Threshold (Pre-Generation):** If the Hybrid Retriever returns fewer than two relevant chunks, the system immediately rejects the query with a standard "cannot confidently answer" message.
2.  **Validator AI (Post-Generation):** A second, smaller LLM call is made using the `VALIDATION_PROMPT_TEMPLATE`. This validator checks if the `Final Answer` is factually supported *only* by the `Retrieved Chunks`. [cite_start]If the validator returns 'NO', the `Final Answer` is overridden with the standard rejection message[cite: 223].
*This validation layer is visible on the UI via the **Validation Status**.*

---
*(Continue with detailed Setup & Installation Instructions, Sample Prompts, and Next Steps for the full 7-day challenge.)*