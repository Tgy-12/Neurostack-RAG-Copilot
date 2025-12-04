---
title: Neurostack RAG Copilot
sdk: docker
app_port: 7860
emoji: ⚡
colorTo: pink
short_description: 'Hachaton neurostack project aims at no/less hallucination! '
---
# Neurostack RAG Copilot - FastAPI Backend

This is the backend service for the Neurostack RAG Copilot, deployed on Hugging Face Spaces using FastAPI and Docker.

---

## 🚀 Deployment

The service is currently live at the following URL:
**[Hugging Face Space URL]** (e.g., `https://thomi-12-neurostack-rag-copilot.hf.space`)

The frontend application communicates with this URL.

---

## 🛠️ Setup & Local Development (Optional)

1.  **Clone the Repository:**
    ```bash
    git clone [Your Repository URL]
    cd [Your-Backend-Folder]
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set Environment Variables:**
    Create a `.env` file and add your secrets:
    ```
    GROQ_API_KEY=your_key_here
    JWT_SECRET_KEY=your_secret_here
    HUGGINGFACE_ACCESS_TOKEN=your_token_here
    ```
4.  **Run Locally:**
    ```bash
    uvicorn app.main:app --reload
    ```

---

## 🔗 Endpoints

The main functionality is exposed via the following endpoints:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Health check endpoint. Returns status. |
| `/query` | `POST` | Processes a user query using the RAG pipeline (Groq + local documents). |
| `/token` | `POST` | Authenticates a user and returns a JWT token. |