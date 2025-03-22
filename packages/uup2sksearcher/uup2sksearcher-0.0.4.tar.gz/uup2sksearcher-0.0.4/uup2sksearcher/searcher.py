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
        return ranked[:top_k]

    def search(self, query, top_k=5):
        refs = self._extract_structure_refs(query)
        if any(refs.values()):
            print(f"📘 Struktur dikenali → Bab: {refs['bab']}, Bagian: {refs['bagian']}, Pasal: {refs['pasal']}")
            docs = self._filter_by_structure(refs)
            return [(1.0, doc) for doc in docs]
        
        topik = self._get_topik_terdekat(query)
        if topik:
            print(f"🧠 Topik dikenali: '{topik}' → pencarian difokuskan")
            docs = self._filter_by_topik(self.all_docs, topik)
        else:
            print("⚠️ Topik tidak dikenali, pencarian di seluruh dokumen")
            docs = self.all_docs
        return self._search_within_docs(query, docs, top_k)

    def _filter_by_structure(self, refs):
        """Cocokkan metadata pasal/bab/bagian"""
        results = []
        for doc in self.all_docs:
            meta = doc.metadata
            match = True
            if refs["pasal"] and refs["pasal"].lower() != meta.get("pasal", "").lower():
                match = False
            if refs["bab"] and refs["bab"].lower() != meta.get("bab", "").lower():
                match = False
            if refs["bagian"] and refs["bagian"] not in meta.get("bagian", "").lower():
                match = False
            if match:
                results.append(doc)
        return results
    
    def _extract_structure_refs(self, query):
        query_lower = query.lower()

        def convert_to_roman(num):
            roman_nums = {
                1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V',
                6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X',
                11: 'XI', 12: 'XII', 13: 'XIII', 14: 'XIV', 15: 'XV'
            }
            return roman_nums.get(num)
        # pasal
        pasal = re.search(r'pasal\s+(\d+)', query_lower)

        bab_roman = re.search(r'BAB\s+([IVXLCDM]+)', query_lower, re.IGNORECASE)
        bab_arabic = re.search(r'BAB\s+(\d+)', query_lower, re.IGNORECASE)
            
        # bab bisa angka romawi (i, v, x...) atau angka biasa (digit)
        #bab_match = re.search(r'bab\s+([ivxlcdm]+|\d+)', query_lower)

        # bagian masih deteksi bebas seperti sebelumnya
        bagian = re.search(r'bagian\s+(ke\w+|\w+)', query_lower)

        bab_value = None
        if bab_roman:
            bab_value = f"{bab_roman.group(1).upper()}"
        elif bab_arabic:
            roman_num = convert_to_roman(int(bab_arabic.group(1)))
            if roman_num:
                bab_value = f"{roman_num}"
                    
        bab_final = f"BAB {bab_value.upper()}" if bab_value else None

        return {
            "pasal": f"Pasal {pasal.group(1)}" if pasal else None,
            "bab": bab_final,
            "bagian": bagian.group(1).lower() if bagian else None
        }