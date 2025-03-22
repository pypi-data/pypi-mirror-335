from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from rapidfuzz import process, fuzz
import numpy as np
from langchain_chroma import Chroma
import re

class TopikAwareSearcher:
    def __init__(self):
        self.model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        self.embedding_model = HuggingFaceEmbeddings(model_name=self.model_name)
        
        vector_store = Chroma(
            embedding_function=self.embedding_model,
            persist_directory='./chroma_db_uup2sk',
            collection_name='uup2sk',
            collection_metadata={"hnsw:space": "cosine"}
        )
        self.vectorstore = vector_store
        self.all_docs = self._load_documents()
        self.daftar_topik = self._extract_topik_set()

    def _load_documents(self):
        raw = self.vectorstore.get()
        return [
            Document(page_content=content, metadata=meta)
            for content, meta in zip(raw["documents"], raw["metadatas"])
        ]

    def _extract_topik_set(self):
        topik_set = set()
        for doc in self.all_docs:
            bab_title = doc.metadata.get("bab_title", "")
            bagian_title = doc.metadata.get("bagian_title", "")
            if bab_title:
                topik_set.add(bab_title.lower())
            if bagian_title:
                topik_set.add(bagian_title.lower())
        return list(topik_set)

    def _extract_keywords_from_query(self, query):
        tokens = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
        return tokens
    
    def _get_topik_terdekat(self, query, threshold=70):
        best = process.extractOne(query, self.daftar_topik, scorer=fuzz.token_set_ratio, score_cutoff=threshold)
        if best:
            return best[0]

        keywords = self._extract_keywords_from_query(query)
        for keyword in keywords:
            match = process.extractOne(keyword, self.daftar_topik, scorer=fuzz.partial_ratio, score_cutoff=threshold)
            if match:
                return match[0]

        return None

    def _filter_by_topik(self, docs, topik):
        return [
            doc for doc in docs
            if topik and (
                topik in doc.metadata.get("bab_title", "").lower() or
                topik in doc.metadata.get("bagian_title", "").lower()
            )
        ]

    def _cosine_sim(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def _search_within_docs(self, query, docs, top_k):
        q_embedding = self.embedding_model.embed_query(query)
        scored = []
        for doc in docs:
            doc_embedding = self.embedding_model.embed_documents([doc.page_content])[0]
            score = self._cosine_sim(q_embedding, doc_embedding)
            scored.append((score, doc))
        ranked = sorted(scored, key=lambda x: x[0], reverse=True)
        return [doc for _, doc in ranked[:top_k]]

    def search(self, query, top_k=5):
        topik = self._get_topik_terdekat(query)
        if topik:
            print(f"🧠 Topik dikenali: '{topik}' → pencarian difokuskan")
            docs = self._filter_by_topik(self.all_docs, topik)
        else:
            print("⚠️ Topik tidak dikenali, pencarian di seluruh dokumen")
            docs = self.all_docs
        return self._search_within_docs(query, docs, top_k)
