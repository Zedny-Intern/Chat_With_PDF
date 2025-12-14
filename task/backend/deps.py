import os
import faiss
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

FAISS_FILE = "faiss_index.bin"
DIMENSION = 768

if os.path.exists(FAISS_FILE):
    print("Loading existing FAISS index...")
    faiss_index = faiss.read_index(FAISS_FILE)
else:
    print("Creating new FAISS index...")
    faiss_index = faiss.IndexFlatL2(DIMENSION)

def save_faiss():
    faiss.write_index(faiss_index, FAISS_FILE)
    print("FAISS index saved.")