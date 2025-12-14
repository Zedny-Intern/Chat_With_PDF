import pymongo
import traceback
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from config import MONGO_URI, DB_NAME, COLLECTION_NAME, GOOGLE_API_KEY

print("start engine setup...")

try:
    print("Loading Embedding Model...")
    Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print("Loading Gemini Model...")
    Settings.llm = GoogleGenAI(model="gemini-2.5-flash", api_key=GOOGLE_API_KEY)

    print("Models setup done.")
except Exception as e:
    print(f"Error setting up models: {e}")


class RAGEngine:
    
    def __init__(self):
        print("🔧 Initializing RAG Engine...")
        
        self.client = None
        self.vector_store = None
        self.index = None
        
        try:
            self.client = pymongo.MongoClient(MONGO_URI)
            self.client.admin.command('ping')
            print("Success: Connected to MongoDB")
            
            self.vector_store = MongoDBAtlasVectorSearch(
                mongodb_client=self.client,
                db_name=DB_NAME,
                collection_name=COLLECTION_NAME,
                vector_index_name="vector_index"
            )
        except Exception as e:
            print(f"MongoDB Connection Error: {e}")
            return

        try:
            self.index = VectorStoreIndex.from_vector_store(vector_store=self.vector_store)
            self.query_engine = self.index.as_query_engine()
            print("RAG Engine is Ready (Loaded existing index)")
        except Exception as e:
            print(f"Index might be empty or new: {e}")
            self.index = None 

    def add_pdf(self, file_path: str):
        print(f"Processing PDF: {file_path}")
        
        try:
            documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
            print(f"Loaded {len(documents)} pages.")

            if self.index is None:
                print("Creating New Index...")
                storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
                
                self.index = VectorStoreIndex.from_documents(
                    documents, 
                    storage_context=storage_context,
                    show_progress=True
                )
            else:
                print("Inserting into existing Index...")
                for doc in documents:
                    self.index.insert(doc)
            
            self.query_engine = self.index.as_query_engine()
            print(f"Successfully added {file_path} to Database.")

        except Exception as e:
            print(f" Error inside add_pdf:")
            print(f"Details: {str(e)}")
            traceback.print_exc()
            raise Exception(f"Failed to process PDF: {str(e)}")

    def query(self, question: str):
        if self.index is None:
            return "Database is empty. Please upload a PDF first."
        
        try:
            response = self.query_engine.query(question)
            return str(response)
        except Exception as e:
            print(f" Query Error: {e}")
            return "Sorry, I cannot answer right now."

rag_system = RAGEngine()