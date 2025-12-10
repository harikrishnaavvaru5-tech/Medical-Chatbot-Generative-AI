from src.helper import load_pdf_file, text_split, download_hugging_face_embeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os


load_dotenv()

extracted_data = load_pdf_file(data='Data/')
text_chunks = text_split(extracted_data)
embeddings = download_hugging_face_embeddings()

# Create FAISS vector store from documents
docsearch = FAISS.from_documents(
    documents=text_chunks,
    embedding=download_hugging_face_embeddings()
)

# Save the FAISS index locally
docsearch.save_local("medical_docs_faiss_index")