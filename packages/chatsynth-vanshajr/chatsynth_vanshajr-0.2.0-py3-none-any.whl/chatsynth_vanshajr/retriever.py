from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

class ChatSynthRetriever:
    def __init__(self, faiss_index_path="faiss_index"):
        """
        Initialize the retriever with the FAISS index.
        """
        self.faiss_index_path = faiss_index_path
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectors = FAISS.load_local(self.faiss_index_path, self.embeddings, allow_dangerous_deserialization=True)
        self.total_docs = self.vectors.index.ntotal

    def get_retriever(self, k=20):
        """
        Get a retriever with the specified number of documents to fetch.
        """
        k = min(k, self.total_docs)  # Fetch up to k docs, or all if less
        return self.vectors.as_retriever(search_kwargs={"k": k})