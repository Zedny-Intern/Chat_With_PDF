import fitz  # PyMuPDF
import os

CHUNK_SIZE = 1000
SAVE_DIR = r"Q:\projects\save_data"

os.makedirs(SAVE_DIR, exist_ok=True)

def extract_chunks(pdf_path):
    chunks = []
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        text = page.get_text()
        chunks.append((i+1, text))
    doc.close()
    return chunks

def extract_chunks_to_disk(pdf_path, chunk_size=CHUNK_SIZE):
    chunk_files = []
    doc = fitz.open(pdf_path)
    
    for page_num, page in enumerate(doc):
        text = page.get_text()
        for i, start in enumerate(range(0, len(text), chunk_size)):
            end = start + chunk_size
            chunk_text = text[start:end]

            file_name = f"{os.path.splitext(os.path.basename(pdf_path))[0]}_page{page_num+1}_chunk{i+1}.txt"
            file_path = os.path.join(SAVE_DIR, file_name)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(chunk_text)
            
            chunk_files.append(file_path)
    
    doc.close()
    return chunk_files

def read_chunk(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
