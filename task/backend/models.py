from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    pdf_files = relationship("PDFFile", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")


class PDFFile(Base):
    __tablename__ = "pdf_files"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String(255))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="pdf_files")
    chunks = relationship("PDFChunk", back_populates="pdf_file")


class PDFChunk(Base):
    __tablename__ = "pdf_chunk"
    id = Column(Integer, primary_key=True, index=True)
    pdf_file_id = Column(Integer, ForeignKey("pdf_files.id"))
    faiss_index_id = Column(Integer, unique=True, index=True)
    page_num = Column(Integer)
    chunk_text = Column(Text)

    pdf_file = relationship("PDFFile", back_populates="chunks")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String(20))  # "user" or "assistant"
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_messages")
