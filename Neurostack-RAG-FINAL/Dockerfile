# let's Start from a stable Python base image
FROM python:3.9

# Set up a non-root user (Standard Hugging Face security practice)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"
WORKDIR /app

# Copy the requirements file and install dependencies
COPY --chown=user:user . .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy all your application files (main.py, models.py, rag_pipeline.py, etc.)
COPY --chown=user . /app

# Default command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]