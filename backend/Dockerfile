FROM python:3.11-slim

WORKDIR /app


RUN python -m pip install --upgrade pip setuptools wheel

# Copy only requirements first (for build caching)
#COPY requirements.txt .

# Install all dependencies from requirements.txt
#RUN python -m pip install --no-cache-dir -r requirements.txt

RUN python -m pip install --no-cache-dir \
    langchain==1.0.2 \
    langchain-google-genai==3.0.0 \
    langchain-huggingface \
    langchain_community \
    kafka-python \
    pymongo \
    python-dotenv \
    supabase==2.4.6\
    langchain_core\
    sentence-transformers

COPY . /app

CMD ["python", "agent.py"]