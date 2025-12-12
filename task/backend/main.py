import os
import faiss
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer

from .models import User, PDFChunk, ChatMessage, Base
from .deps import engine, SessionLocal, faiss_index, save_faiss
from backend.pdf_processing import extract_chunks_to_disk, read_chunk, SAVE_DIR
from .rag_logic import ask_gemini

app = FastAPI(title="RAG PDF Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

embed_model = SentenceTransformer("all-mpnet-base-v2")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    save_path = os.path.join(SAVE_DIR, file.filename)
    try:
        with open(save_path, "wb") as f:
            f.write(await file.read())
    except PermissionError:
        return {"error": f"Cannot save file {file.filename}. Check permissions."}

    try:
        chunk_files = extract_chunks_to_disk(save_path)
    except PermissionError as e:
        print(f"Warning: {e}")
        chunk_files = []

    print(f"{len(chunk_files)} chunks extracted from {file.filename}")
    return {"message": f"{file.filename} uploaded successfully.", "chunks": len(chunk_files)}

@app.on_event("startup")
def process_pdfs_on_startup():
    pdf_files = [f for f in os.listdir(SAVE_DIR) if f.lower().endswith(".pdf")]
    for pdf_file in pdf_files:
        pdf_path = os.path.join(SAVE_DIR, pdf_file)
        try:
            chunk_files = extract_chunks_to_disk(pdf_path)
            print(f"{len(chunk_files)} chunks extracted from {pdf_file}")
        except PermissionError as e:
            print(f"Warning: Cannot process {pdf_file}: {e}")

@app.get("/ask")
def ask_question(
    question: str,
    username: str,
    top_k: int = 5,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    q_emb = embed_model.encode([question], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)

    D, I = faiss_index.search(q_emb, top_k)

    context = []
    for idx in I[0]:
        if idx != -1:
            chunk = db.query(PDFChunk).filter(PDFChunk.faiss_index_id == int(idx)).first()
            if chunk and chunk.chunk_text.strip():
                context.append(f"(Page {chunk.page_num}): {chunk.chunk_text}")

    if not context:
        return {"answer": "No relevant PDF content found for your question.", "context": []}

    history_objs = db.query(ChatMessage).filter(ChatMessage.user_id == user.id).order_by(ChatMessage.timestamp).all()
    chat_history = [{"role": msg.role, "content": msg.content} for msg in history_objs[-5:]]

    answer = ask_gemini(context, chat_history, question)

    db.add(ChatMessage(user_id=user.id, role="user", content=question))
    db.add(ChatMessage(user_id=user.id, role="assistant", content=answer))
    db.commit()

    return {"answer": answer, "context": context}
