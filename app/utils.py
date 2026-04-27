import re
from collections import Counter


def extract_text_from_pdf(file_path):
    """Extract text from PDF using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except ImportError:
        raise ImportError("PyMuPDF no está instalado. Ejecuta: pip install PyMuPDF")
    except Exception as e:
        raise ValueError(f"Error al leer el PDF: {e}")


def extract_text_from_docx(file_path):
    """Extract text from DOCX using python-docx."""
    try:
        from docx import Document
        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except ImportError:
        raise ImportError("python-docx no está instalado. Ejecuta: pip install python-docx")
    except Exception as e:
        raise ValueError(f"Error al leer el DOCX: {e}")


def count_words(text):
    """Count words in a text."""
    words = re.findall(r'\b\w+\b', text)
    return len(words)


def summarize_text(text, max_sentences=5):
    """
    Simple extractive summarization:
    1. Split into sentences
    2. Score each by word frequency (TF)
    3. Return top N sentences in original order
    """
    # Clean up text
    text = re.sub(r'\s+', ' ', text).strip()

    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if not sentences:
        return text[:500] + "..." if len(text) > 500 else text

    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    # Word frequency scoring (ignore stopwords)
    stopwords = {
        'de', 'la', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las',
        'por', 'un', 'una', 'con', 'no', 'su', 'que', 'es', 'al',
        'lo', 'como', 'más', 'pero', 'sus', 'le', 'ya', 'o', 'este',
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
        'for', 'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been',
        'this', 'that', 'it', 'its', 'from', 'by', 'as', 'not',
    }

    words = re.findall(r'\b\w+\b', text.lower())
    word_freq = Counter(w for w in words if w not in stopwords and len(w) > 2)

    if not word_freq:
        return " ".join(sentences[:max_sentences])

    max_freq = max(word_freq.values())
    word_freq = {w: f / max_freq for w, f in word_freq.items()}

    # Score sentences
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        s_words = re.findall(r'\b\w+\b', sentence.lower())
        score = sum(word_freq.get(w, 0) for w in s_words)
        # Boost first and last sentences slightly
        if i == 0:
            score *= 1.3
        elif i == len(sentences) - 1:
            score *= 1.1
        sentence_scores[i] = score

    # Get top N sentences, sorted by original position
    top_indices = sorted(
        sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:max_sentences]
    )

    summary = " ".join(sentences[i] for i in top_indices)
    return summary


def compute_similarity(summary_a, summary_b):
    """
    Compute cosine similarity between two texts using TF vectors.
    Returns a float between 0 and 1.
    """
    def tokenize(text):
        return re.findall(r'\b\w+\b', text.lower())

    tokens_a = tokenize(summary_a)
    tokens_b = tokenize(summary_b)

    if not tokens_a or not tokens_b:
        return 0.0

    vocab = set(tokens_a) | set(tokens_b)
    freq_a = Counter(tokens_a)
    freq_b = Counter(tokens_b)

    vec_a = [freq_a.get(w, 0) for w in vocab]
    vec_b = [freq_b.get(w, 0) for w in vocab]

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = sum(x ** 2 for x in vec_a) ** 0.5
    mag_b = sum(x ** 2 for x in vec_b) ** 0.5

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return round(dot / (mag_a * mag_b), 4)
