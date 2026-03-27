from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma.vectorstores import Chroma
# from langchain_ollama import OllamaEmbeddings
from src.config.llm_factory import get_embeddings

BASE_FOLDER = "base"

def create_db():
    """
    Main workflow to prepare the AI's memory.
    """
    # 1. Load the raw files (PDFs, TXT, etc.)
    raw_documents = load_source_data()
    # print(raw_documents)
    
    # 2. Split the documents into smaller, manageable pieces (chunks)
    chunks = split_text_into_chunks(raw_documents)
    print(f"\n\nTotal Chunks: {len(chunks)}\n\n")
    
    # 3. Convert text chunks into vectors and store them in the database
    create_vector_index(chunks)
    pass

def load_source_data():
    loader_source = PyPDFDirectoryLoader(BASE_FOLDER)
    documents = loader_source.load()
    return documents
    
def split_text_into_chunks(documents):
    spliter = RecursiveCharacterTextSplitter(
        chunk_size = 2000, 
        chunk_overlap = 500, 
        length_function = len, 
        add_start_index = True
    )
    chunks = spliter.split_documents(documents)
    return chunks

def create_vector_index(chunks):
    # embeddings = OllamaEmbeddings(model="llama3.2")
    embeddings = get_embeddings()
    db = Chroma.from_documents(chunks, embeddings, persist_directory="chunks_db")
    print("Chunk Data Base created with success")
    pass