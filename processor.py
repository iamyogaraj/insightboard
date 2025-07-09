import fitz
import pytesseract
from PIL import Image
import io
import re
import logging
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer, util
from .constants import METHOD_QUESTIONS, FORESIGHT_QUESTIONS, SYNONYMS_MAP, SIMILARITY_THRESHOLD, OCR_CONFIG

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self._init_ocr()
    
    def _init_ocr(self):
        """Initialize OCR configuration"""
        try:
            pytesseract.pytesseract.tesseract_cmd = self._find_tesseract()
        except Exception as e:
            logger.error(f"OCR initialization failed: {str(e)}")
            raise

    def _find_tesseract(self) -> str:
        """Locate Tesseract executable"""
        try:
            import shutil
            return shutil.which("tesseract") or "/usr/bin/tesseract"
        except:
            return "/usr/bin/tesseract"

    def extract_text(self, pdf_file: io.BytesIO) -> Tuple[List[str], bool]:
        """
        Extract text from PDF, handling both text and image-based
        Returns (pages, is_scanned)
        """
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            pages = []
            is_scanned = True
            
            for page in doc:
                text = page.get_text()
                if text.strip():
                    is_scanned = False
                    pages.append(text)
                else:
                    try:
                        pix = page.get_pixmap(dpi=300)
                        img = Image.open(io.BytesIO(pix.tobytes("png")))
                        img = img.convert('L')  # Grayscale
                        text = pytesseract.image_to_string(img, config=OCR_CONFIG)
                        pages.append(text)
                    except Exception as e:
                        logger.warning(f"OCR failed on page {page.number}: {str(e)}")
                        pages.append("")
            
            return pages, is_scanned
        except Exception as e:
            logger.error(f"PDF processing failed: {str(e)}")
            raise

    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize text"""
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into meaningful paragraphs"""
        paras = re.split(r'\n{2,}|\s{4,}', text)
        return [self._preprocess_text(p) for p in paras if p.strip()]

    def _find_by_synonyms(self, question: str, pages: List[str]) -> Dict:
        """Find answers using synonym matching"""
        best = {"text": "", "page": -1, "score": 0}
        
        for page_num, page_text in enumerate(pages, 1):
            page_text_lower = page_text.lower()
            
            # Check all synonyms for this question
            for syn in SYNONYMS_MAP.get(question, []):
                if syn.lower() in page_text_lower:
                    # Find the sentence containing the synonym
                    for sentence in re.split(r'[.!?]\s+', page_text):
                        if syn.lower() in sentence.lower():
                            return {
                                "text": self._preprocess_text(sentence),
                                "page": page_num,
                                "score": SIMILARITY_THRESHOLD + 0.1,
                                "method": "synonym"
                            }
        return best

    def _extract_answer(self, question: str, text: str) -> str:
        """Extract precise answer based on question type"""
        if not text:
            return "Not found"
        
        # Yes/No questions
        if question.lower().startswith(('is ', 'are ', 'does ', 'do ', 'have ', 'has ')):
            match = re.search(r'\b(yes|no)\b', text, re.IGNORECASE)
            if match:
                explanation = re.search(r'(?:yes|no)[\s:;-]+(.+?)(?=[.!?]|$)', text[match.end():], re.IGNORECASE)
                if explanation:
                    return f"{match.group(0).capitalize()}. {explanation.group(1).strip()}"
                return match.group(0).capitalize()
        
        # Numeric questions
        if any(kw in question.lower() for kw in ["maximum", "minimum", "how many", "how much", "percentage", "number of"]):
            match = re.search(r'(\d+\.?\d*)\s*(feet|ft|meters|m|%|percent)?', text, re.IGNORECASE)
            if match:
                unit = match.group(2).lower() if match.group(2) else ""
                unit = unit.replace("percent", "%").replace("foot", "feet")
                return f"{match.group(1)} {unit}".strip()
        
        # Default: return most relevant sentence
        sentences = re.split(r'[.!?]', text)
        if sentences:
            return sentences[0].strip()
        return text[:200] + "..." if len(text) > 200 else text

    def find_answers(self, pages: List[str], question_set: str) -> List[Dict]:
        """Find answers to questions for the selected question set"""
        questions = METHOD_QUESTIONS if question_set == "Method" else FORESIGHT_QUESTIONS
        results = []
        
        for question in questions:
            # First try synonym matching
            synonym_match = self._find_by_synonyms(question, pages)
            
            # Then try semantic search
            semantic_match = {"text": "", "page": -1, "score": 0, "method": "semantic"}
            question_embed = self.embedder.encode(question, convert_to_tensor=True)
            
            for page_num, page_text in enumerate(pages, 1):
                for para in self._split_paragraphs(page_text):
                    para_embed = self.embedder.encode(para, convert_to_tensor=True)
                    similarity = util.pytorch_cos_sim(question_embed, para_embed).item()
                    
                    if similarity > semantic_match["score"]:
                        semantic_match = {
                            "text": para,
                            "page": page_num,
                            "score": similarity,
                            "method": "semantic"
                        }
            
            # Choose best match
            best_match = synonym_match if synonym_match["score"] > semantic_match["score"] else semantic_match
            answer = self._extract_answer(question, best_match["text"])
            
            results.append({
                "question": question,
                "answer": answer if answer else "Not found",
                "page": best_match["page"] if answer != "Not found" else -1,
                "confidence": round(best_match["score"], 2),
                "method": best_match["method"]
            })
        
        return results