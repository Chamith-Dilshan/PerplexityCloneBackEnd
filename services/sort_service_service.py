from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np


class SortSourceService:
    def __init__(self) -> None:
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    def sort_service(self,query:str, search_result: List[dict]):
        try:
            relevant_docs = []
            # here we using cos similarity search
            query_embedding = self.embedding_model.encode(query)
            for result in search_result:
                if "content" in result:
                    content_embedding = self.embedding_model.encode(result["content"])
                    # Here we computes the cosine similarity between query_embedding and content_embedding
                    similarity = float(np.dot(query_embedding, content_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(content_embedding)))
                    
                    result["relavance_score"] = similarity

                    if similarity > 0.3:  # threshold for relevance
                        relevant_docs.append(result)

            # Sort the relevant documents by their relevance score in descending order
            print(f"Sorting is done, found {len(relevant_docs)} relevant documents.")
            return sorted(relevant_docs, key=lambda x: x["relavance_score"], reverse=True)
        except Exception as e:
            print(f"An error occurred while sorting the sources: {str(e)}")
            return []