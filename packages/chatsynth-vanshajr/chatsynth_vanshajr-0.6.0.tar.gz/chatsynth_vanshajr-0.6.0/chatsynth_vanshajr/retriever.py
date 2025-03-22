from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

class ChatSynthRetriever:
    def __init__(self, vectors):
        """
        Initialize the retriever with a pre-loaded FAISS index.

        Args:
            vectors: A pre-loaded FAISS index.
        """
        self.vectors = vectors
        self.total_docs = vectors.index.ntotal

    def get_retriever(self, k=20):
        """
        Get a retriever with the specified number of documents to fetch.

        Args:
            k (int): Number of documents to retrieve. Defaults to 20.

        Returns:
            A retriever object.
        """
        k = min(k, self.total_docs)  # Fetch up to k docs, or all if less
        return self.vectors.as_retriever(search_kwargs={"k": k})