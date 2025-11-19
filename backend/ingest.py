import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from supabase.client import Client, create_client
from tqdm import tqdm  # progress bar

load_dotenv()

supabase_url = os.environ.get("SUPABASE_API")
supabase_key = os.environ.get("SUPABASE_SERVICE_API_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# ✅ Updated import path
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print("✅ Loaded embedding model: all-MiniLM-L6-v2")

dir = "data"
data_dir = Path(dir).resolve()
csv_files = list(data_dir.glob("**/*.csv"))

print(f"Found {len(csv_files)} CSV files: {[str(f) for f in csv_files]}")

documents = []
for csv_file in csv_files:
    print(f"Loading CSV: {csv_file}")
    loader = CSVLoader(file_path=str(csv_file), encoding="utf-8", csv_args={"delimiter": ","})
    documents.extend(loader.load())

print(f"Total loaded documents: {len(documents)}")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(documents)
print(f"Total chunks: {len(docs)}")

# ⚡ Create empty Supabase store
vector_store = SupabaseVectorStore(
    client=supabase,
    table_name="documents",
    query_name="match_documents",
    embedding=embedding_model,
)

# ✅ Batch insert (to avoid timeout)
batch_size = 200 
for i in tqdm(range(0, len(docs), batch_size), desc="Uploading to Supabase"):
    batch = docs[i : i + batch_size]
    try:
        vector_store.add_documents(batch)
    except Exception as e:
        print(f"⚠️ Failed batch {i // batch_size}: {e}")
