import fitz  # PyMuPDF
import re
import io
from PIL import Image
import pytesseract
from sentence_transformers import SentenceTransformer, util

# Load NLP model
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

def extract_text_with_ocr(uploaded_file):
    """
    Extracts text from each page using PyMuPDF, applies OCR if page is empty.
    """
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    full_text = ""

    for page_index in range(len(doc)):
        text = doc[page_index].get_text("text").strip()

        if not text:  # OCR fallback
            pix = doc[page_index].get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_text = pytesseract.image_to_string(img)
            full_text += ocr_text + " "
        else:
            full_text += text + " "

    return re.sub(r"\s+", " ", full_text).strip()

def extract_questions_from_pdf(uploaded_file):
    """
    NLP + OCR-powered extraction of question blocks from mixed-format PDFs.
    """
    full_text = extract_text_with_ocr(uploaded_file)

    blocks = re.split(r"\b(?:Question\s*)?\d{1,3}[.)\-–:]?", full_text)
    question_blocks = [b.strip() for b in blocks if len(b.strip()) > 30]

    indexed_questions = {}
    for i, block in enumerate(question_blocks):
        q_num = str(i + 1)
        block_lower = block.lower()
        answer = "yes" if "yes" in block_lower else ("no" if "no" in block_lower else "unmarked")
        indexed_questions[q_num] = {
            "question": block,
            "answer": answer
        }

    return indexed_questions

def search_question(indexed_data, expected_text):
    """
    Uses transformer embeddings to find closest semantic match.
    """
    target_embedding = model.encode(expected_text, convert_to_tensor=True)

    best_score = 0.0
    best_match = None
    best_qid = None

    for qid, entry in indexed_data.items():
        entry_embedding = model.encode(entry["question"], convert_to_tensor=True)
        score = util.pytorch_cos_sim(target_embedding, entry_embedding)[0].item()

        if score > best_score:
            best_score = score
            best_match = entry
            best_qid = qid

    is_yes = best_match["answer"] == "yes" and best_score > 0.5
    match_percent = round(best_score * 100, 2)

    return (
        f"| Question Number | Question                                               | Answer        |\n"
        f"|-----------------|------------------------------------------------------------|---------------|\n"
        f"| Q{best_qid}           | {best_match['question'].strip()} | {'✅ Yes' if is_yes else '❌ No'} (Match score: {match_percent}%) |"
    )