import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from utils.config import Config
from utils.logger import logger

class DocumentProcessor:
    def __init__(self):
        self.chunk_size = Config.CHUNK_SIZE
        self.chunk_overlap = Config.CHUNK_OVERLAP

    def process_file(self, file_path: str, file_type: str) -> List[Dict[str, Any]]:
        logger.info(f"Processing file: {file_path}, type: {file_type}")

        if file_type == "pdf":
            text = self._extract_pdf(file_path)
        elif file_type in ["txt", "md"]:
            text = self._extract_text(file_path)
        elif file_type in ["doc", "docx"]:
            text = self._extract_doc(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_type}")
            return []

        cleaned_text = self._clean_text(text)
        chunks = self._split_chunks(cleaned_text, file_path)

        logger.info(f"Extracted {len(chunks)} chunks from {file_path}")
        return chunks

    def _extract_pdf(self, file_path: str) -> str:
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except ImportError:
            logger.warning("pypdf not installed, using fallback")
            return self._extract_pdf_fallback(file_path)
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return ""

    def _extract_pdf_fallback(self, file_path: str) -> str:
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                text = content.decode('utf-8', errors='ignore')
                text = re.sub(r'[^\x20-\x7E\n\u4e00-\u9fff]', ' ', text)
                return text
        except Exception as e:
            logger.error(f"PDF fallback extraction error: {e}")
            return ""

    def _extract_text(self, file_path: str) -> str:
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
        chunk_size = 1024 * 1024  # 1MB chunks for large files
        
        file_size = Path(file_path).stat().st_size
        is_large_file = file_size > 10 * 1024 * 1024  # >10MB
        
        if is_large_file:
            logger.info(f"Large file detected ({file_size / 1024 / 1024:.1f}MB), using streaming read")
            
        for encoding in encodings:
            try:
                if is_large_file:
                    text_parts = []
                    with open(file_path, 'r', encoding=encoding) as f:
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            text_parts.append(chunk)
                    return ''.join(text_parts)
                else:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
            except:
                continue
                
        with open(file_path, 'r', errors='ignore') as f:
            if is_large_file:
                text_parts = []
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    text_parts.append(chunk)
                return ''.join(text_parts)
            return f.read()

    def _extract_doc(self, file_path: str) -> str:
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except ImportError:
            logger.warning("python-docx not installed, cannot extract .doc/.docx")
            return ""
        except Exception as e:
            logger.error(f"DOC extraction error: {e}")
            return ""

    def _clean_text(self, text: str) -> str:
        chunk_size = 100000
        if len(text) > chunk_size:
            text_parts = []
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                chunk = re.sub(r'\s+', ' ', chunk)
                chunk = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', chunk)
                text_parts.append(chunk)
            return ' '.join(text_parts).strip()
        else:
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
            return text.strip()

    def _split_chunks(self, text: str, source_file: str) -> List[Dict[str, Any]]:
        if not text or len(text.strip()) < 10:
            return []

        chunks = []
        chunk_id = 0
        current_chunk = ""
        current_length = 0
        recent_sentences = []

        for sentence in self._split_by_sentence_generator(text):
            sentence_length = len(sentence)

            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunks.append({
                    "content": current_chunk.strip(),
                    "chunk_id": chunk_id,
                    "source_file": source_file,
                    "char_count": current_length
                })
                chunk_id += 1

                overlap_text = ""
                if self.chunk_overlap > 0 and recent_sentences:
                    overlap_length = 0
                    for prev_sent in reversed(recent_sentences[-5:]):
                        if overlap_length + len(prev_sent) <= self.chunk_overlap:
                            overlap_text = prev_sent + overlap_text
                            overlap_length += len(prev_sent)
                    current_chunk = overlap_text + sentence
                    current_length = len(current_chunk)
                else:
                    current_chunk = sentence
                    current_length = sentence_length

                recent_sentences.append(sentence)
                if len(recent_sentences) > 10:
                    recent_sentences = recent_sentences[-10:]
            else:
                current_chunk += sentence if not current_chunk else " " + sentence
                current_length += sentence_length
                recent_sentences.append(sentence)
                if len(recent_sentences) > 10:
                    recent_sentences = recent_sentences[-10:]

        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "chunk_id": chunk_id,
                "source_file": source_file,
                "char_count": current_length
            })

        return chunks

    def _split_by_sentence_generator(self, text: str):
        sentence_endings = re.compile(r'[。！？；\n\.!?;]+')
        chunk_size = 50000

        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            sentences = sentence_endings.split(chunk)

            for sent in sentences:
                sent = sent.strip()
                if sent:
                    if len(sent) > 50:
                        sub_sentences = self._split_long_sentence(sent)
                        for sub_sent in sub_sentences:
                            yield sub_sent
                    else:
                        yield sent

    def _split_long_sentence(self, text: str, max_length: int = 100) -> List[str]:
        if len(text) <= max_length:
            return [text]

        chunks = []
        words = text.split()
        current_chunk = ""
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= max_length:
                current_chunk += (" " if current_chunk else "") + word
                current_length += len(word) + (1 if current_chunk else 0)
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = word
                current_length = len(word)

        if current_chunk:
            chunks.append(current_chunk)

        return chunks if chunks else [text]
