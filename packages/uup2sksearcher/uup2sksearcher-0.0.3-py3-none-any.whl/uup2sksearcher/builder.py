import sqlite3
import fitz
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
import re
from langchain.text_splitter import TokenTextSplitter
import json
from langchain_chroma import Chroma

class ChromaBuilder:
    def __init__(self):
        self.model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        self.embedding_model = HuggingFaceEmbeddings(model_name=self.model_name)
        self.vector_store = Chroma(
            embedding_function=self.embedding_model,
            persist_directory='./chroma_db_uup2sk',
            collection_name='uup2sk',
            collection_metadata={"hnsw:space": "cosine"}
        )
    
    def contstruct_db(self,text_content):
        # Buat database SQLite
        db_path = "./datas/uup2sk.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Buat tabel jika belum ada
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS peraturan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nomor TEXT,
            tahun INTEGER,
            judul TEXT,
            isi TEXT
        )
        """)

        # Simpan data ke dalam tabel
        nomor_uu = "4"
        tahun_uu = "2023"
        judul_uu = "Undang-Undang tentang Pengembangan dan Penguatan Sektor Keuangan"

        cursor.execute("INSERT INTO peraturan (nomor, tahun, judul, isi) VALUES (?, ?, ?, ?)", 
                    (nomor_uu, tahun_uu, judul_uu, text_content))

        # Commit dan tutup koneksi
        conn.commit()
        conn.close()
        
    def construct_pdf_MuPdf(self,pdf_path="./datas/UU_NO_4_2023_Hukumonline.pdf"):
        import sqlite3
        import fitz
        # Path file PDF yang diunggah
        pdf_path = pdf_path
        doc = fitz.open(pdf_path)
        text_content = ""
        for page in doc:
            text_content += page.get_text("text") + "\n"
        
        self.contstruct_db(text_content)
    
    def read_db(self,db_path):
        # Path database SQLite
        db_path = "./datas/uup2sk.db"

        # Koneksi ke database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Ambil teks dari tabel peraturan
        cursor.execute("SELECT nomor, tahun, judul, isi FROM peraturan")
        data = cursor.fetchone()

        # Tampilkan hasil
        nomor, tahun, judul, isi = data
        #print(f"UU Nomor {nomor} Tahun {tahun}: {judul}\n")
        #print(isi[:1000])  # Tampilkan hanya sebagian isi

        # Tutup koneksi
        conn.close()
        return {"nomor": nomor,"tahun":tahun,"judul":judul,"isi":data}
    
    def split_law_text(self,text):
        structure = {}  # Dictionary untuk menyimpan hasil
        current_bab = None
        current_bagian = None
        current_pasal = None
        pending_bab = None  # Menyimpan BAB yang belum memiliki judul
        pending_bagian=None
        pending_pasal=None
        
        def extract_pasal_number(pasal_text):
            """Ekstrak angka dari string 'Pasal X' menjadi integer X."""
            match = re.search(r"Pasal\s+(\d+)", pasal_text)
            return int(match.group(1)) if match else None

        def clean_text(text):
            """Membersihkan teks dari karakter aneh dan memastikan format yang rapi."""
            text = re.sub(r'\d+/\d+\s*\n?', '', text)  # Hapus baris yang mengandung angka seperti "7/545"
            #text = re.sub(r'\\n', ' ', text)  # Ganti "\n" dalam string mentah dengan spasi
            text = re.sub(r'\s+', ' ', text)  # Hapus spasi ekstra
            return text.strip()

        # Regex untuk mendeteksi BAB, Bagian, dan Pasal
        bab_pattern = re.compile(r"\b(BAB\s+[IVXLCDM]+)(?:\s+([A-Z][^\n]*))?", re.IGNORECASE)
        #bagian_pattern = re.compile(r"\b(Bagian\s+[A-Za-z0-9\-]+)(?:\s+([A-Z][^\n]*))?", re.IGNORECASE)
        bagian_pattern = re.compile(r"\b(Bagian\s+[A-Za-z0-9\-]+)\b(?=\s*$|\s*[.,;:])", re.IGNORECASE)
        pasal_pattern = re.compile(r"^\s*(Pasal\s+\d+)\s*$", re.IGNORECASE)  # Hanya Pasal di satu baris penuh
        
        # Bersihkan teks sebelum diproses
        text_data= clean_text(text)
        
        lines = text_data.split("\\n")  # Pisahkan teks menjadi baris

        for i, line in enumerate(lines, start=1):
            line = line.strip()
            
            if not line:
                continue  # Lewati baris kosong
            
            # Cek apakah baris adalah BAB
            bab_match = bab_pattern.match(line)
            if bab_match:
                pending_bab = bab_match.group(1)  # Simpan BAB sementara, cari judulnya nanti
                continue  

            # Jika BAB sebelumnya belum memiliki judul, gunakan baris ini sebagai judul BAB
            if pending_bab:
                current_bab = pending_bab
                structure[current_bab] = {"judul": line}  # Simpan judulnya
                pending_bab = None
                current_bagian = None
                current_pasal = None
                continue  
            
            
            bagian_match = bagian_pattern.match(line)
            if bagian_match and current_bab:
                pending_bagian = bagian_match.group(1)  # Simpan BAB sementara, cari judulnya nanti
                continue  
            
            if pending_bagian:
                current_bagian = pending_bagian
                structure[current_bab][current_bagian] = {"judul": line}  # Simpan judulnya
                pending_bagian= None
                current_pasal = None
                continue  
            
            pasal_match = pasal_pattern.match(line)
            if pasal_match:
                pending_pasal = pasal_match.group(1)  # Contoh: "Pasal 1"
                new_pasal_num = extract_pasal_number(pending_pasal)
                current_pasal_num = extract_pasal_number(current_pasal) if current_pasal else None

                if current_pasal_num is not None and new_pasal_num <= current_pasal_num:
                    if current_bab:
                        if current_bagian:
                            structure[current_bab][current_bagian][current_pasal].append(line)
                        else:
                            structure[current_bab][current_pasal].append(line)
                        
                    pending_pasal=current_pasal
                    
                continue
            
            if pending_pasal:
                current_pasal = pending_pasal
                if current_bab:
                    if current_bagian:
                        if current_pasal not in structure[current_bab][current_bagian]:
                            structure[current_bab][current_bagian][current_pasal]=[]
                        structure[current_bab][current_bagian][current_pasal].append(line)
                    else:
                        if current_pasal not in structure[current_bab]:
                            structure[current_bab][current_pasal] = []
                        structure[current_bab][current_pasal].append(line)
                else:
                    if "Pendahuluan" not in structure:
                        structure["Pendahuluan"] = {"pengantar": []}
                    structure["Pendahuluan"]["pengantar"].append(line)
                
                pending_pasal= None
                continue  
            
            
            if line=="PENJELASAN" and current_pasal=="Pasal 341":
                current_bab=None
                current_bagian=None
                current_pasal=None
                if "Penjelasan" not in structure:
                    structure["Penjelasan"] = {"pengantar": []}
                
            if current_bab:
                if current_pasal:
                    if current_bagian:
                        structure[current_bab][current_bagian][current_pasal].append(line)
                    else:
                        structure[current_bab][current_pasal].append(line)
                else:
                    if "pengantar" not in structure[current_bab]:
                        structure[current_bab]["pengantar"] = []
                    structure[current_bab]["pengantar"].append(line)
            else:
                if "Penjelasan" in structure:
                    structure["Penjelasan"]["pengantar"].append(line)
                else:    
                    if "Pendahuluan" not in structure:
                        structure["Pendahuluan"] = {"pengantar": []}
                    structure["Pendahuluan"]["pengantar"].append(line)
                
        return structure
    
    def create_index_chroma(self,db_path="./datas/uup2sk.db"):
        
        json_data = self.read_db(db_path) 
        
        def clean_metadata(metadata):
            return {k: (str(v) if v is not None else "") for k, v in metadata.items()}
        
        text_data = f"UU Nomor {json_data['nomor']} Tahun {json_data['tahun']} - {json_data['judul']}\n{json_data['isi']}"
        structured_data = self.split_law_text(text_data)

        texts = []
        metadata = []

        for bab, bagian_dict in structured_data.items():
            if isinstance(bagian_dict, dict):
                bab_title = bagian_dict.get("judul", "")  # Get BAB title
                
                for bagian, pasal_dict in bagian_dict.items():
                    if bagian == "pengantar":
                        full_text = f"{bab} - {bab_title} - Pengantar: {' '.join(pasal_dict)}"
                        texts.append(full_text)
                        metadata.append({
                            "bab": bab,
                            "bab_title": bab_title.lower(),
                            "bagian": "pengantar",
                            "pasal": None
                        })
                        continue

                    if isinstance(pasal_dict, dict):
                        bagian_title = pasal_dict.get("judul", "") if "Bagian" in bagian else ""
                        for pasal, isi in pasal_dict.items():
                            if pasal.lower() == "judul":
                                continue
                            
                            if not isinstance(isi, list):
                                continue
                            
                            if "Bagian" not in bagian:
                                full_text = f"{bab} - {bab_title} - {pasal}: {' '.join(isi)}"
                                metadata.append({
                                    "bab": bab,
                                    "bab_title": bab_title.lower(),
                                    "bagian": None,
                                    "pasal": pasal 
                                })
                            else:
                                full_text = f"{bab} - {bab_title} - {bagian} - {bagian_title} - {pasal}: {' '.join(isi)}"
                                metadata.append({
                                    "bab": bab,
                                    "bab_title": bab_title.lower(),
                                    "bagian": bagian,
                                    "bagian_title": bagian_title.lower(),
                                    "pasal": pasal
                                })
                                
                            texts.append(full_text)

                    elif isinstance(pasal_dict, list):
                        full_text = f"{bab} - {bab_title} - {bagian}: {' '.join(pasal_dict)}"
                        metadata.append({
                            "bab": bab,
                            "bab_title": bab_title.lower(),
                            "bagian": None,
                            "pasal": bagian
                        })
                        texts.append(full_text)
        # Debugging: Melihat hasil metadata
        documents=[]
        
        # Debugging: Melihat hasil metadata
        documents=[]
        cleaned_metadata = [clean_metadata(meta) for meta in metadata]
        
        for meta, text in zip(cleaned_metadata, texts):
            #print(meta, "\n", text, "\n")
            documents.append(Document(page_content=str(text), metadata=meta))
        
        embed_model = self.embedding_model
        
        # Create and persist a Chroma vector database from the chunked documents
        vs = Chroma.from_documents(
            documents=documents,
            embedding=embed_model,
            persist_directory="chroma_db_uup2sk",  # Local mode with in-memory storage only
            collection_name="uup2sk",
            collection_metadata={"hnsw:space": "cosine"}
        )
        print('Vector DB created successfully !')