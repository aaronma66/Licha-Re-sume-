import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib import messages

from .models import DocumentSummary, SimilarityRequest
from .utils import (
    extract_text_from_pdf,
    extract_text_from_docx,
    count_words,
    summarize_text,
    compute_similarity,
)


def index(request):
    """Home page — upload form + list of all summaries."""
    summaries = DocumentSummary.objects.all()
    return render(request, 'app/index.html', {'summaries': summaries})


@require_POST
def upload_document(request):
    """Handle document upload, extract text, summarize, save."""
    uploaded_file = request.FILES.get('document')

    if not uploaded_file:
        messages.error(request, 'No se recibió ningún archivo.')
        return redirect('index')

    # Validate file type
    filename = uploaded_file.name.lower()
    if not (filename.endswith('.pdf') or filename.endswith('.docx') or filename.endswith('.doc')):
        messages.error(request, 'Solo se aceptan archivos PDF o Word (.docx).')
        return redirect('index')

    # Validate file size
    if uploaded_file.size > settings.MAX_UPLOAD_SIZE:
        messages.error(request, 'El archivo supera el límite de 30MB.')
        return redirect('index')

    # Save file temporarily
    from django.core.files.storage import default_storage
    saved_path = default_storage.save(f'documents/{uploaded_file.name}', uploaded_file)
    full_path = os.path.join(settings.MEDIA_ROOT, saved_path)

    try:
        # Extract text
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(full_path)
        else:
            text = extract_text_from_docx(full_path)

        word_count = count_words(text)

        if word_count > 5000:
            os.remove(full_path)
            messages.error(
                request,
                f'El documento tiene {word_count:,} palabras. El máximo permitido es 5,000.'
            )
            return redirect('index')

        if word_count < 20:
            os.remove(full_path)
            messages.error(request, 'El documento parece estar vacío o tiene muy poco texto.')
            return redirect('index')

        # Summarize
        summary = summarize_text(text, max_sentences=5)

        # Save to DB
        doc_summary = DocumentSummary.objects.create(
            original_filename=uploaded_file.name,
            file=saved_path,
            summary=summary,
            word_count=word_count,
        )

        messages.success(request, f'"{uploaded_file.name}" resumido exitosamente.')
        return redirect('detail', pk=doc_summary.pk)

    except (ImportError, ValueError) as e:
        if os.path.exists(full_path):
            os.remove(full_path)
        messages.error(request, f'Error al procesar el archivo: {e}')
        return redirect('index')


def detail(request, pk):
    """Detail view for a single summary."""
    doc = get_object_or_404(DocumentSummary, pk=pk)
    other_docs = DocumentSummary.objects.exclude(pk=pk)
    return render(request, 'app/detail.html', {'doc': doc, 'other_docs': other_docs})


@require_POST
def check_similarity(request, pk):
    """Compare a summary against all others and return similarity scores as JSON."""
    doc = get_object_or_404(DocumentSummary, pk=pk)
    all_others = DocumentSummary.objects.exclude(pk=pk)

    results = []
    for other in all_others:
        score = compute_similarity(doc.summary, other.summary)
        results.append({
            'id': str(other.pk),
            'filename': other.original_filename,
            'score': score,
            'percent': round(score * 100, 1),
            'uploaded_at': other.uploaded_at.strftime('%d/%m/%Y'),
        })

    # Sort by score descending
    results.sort(key=lambda x: x['score'], reverse=True)

    # Save request
    sim_req = SimilarityRequest.objects.create(source=doc, results=results)
    sim_req.compared_with.set(all_others)

    return JsonResponse({'results': results, 'total': len(results)})


def delete_summary(request, pk):
    """Delete a summary."""
    doc = get_object_or_404(DocumentSummary, pk=pk)
    if request.method == 'POST':
        if doc.file and os.path.exists(doc.file.path):
            os.remove(doc.file.path)
        doc.delete()
        messages.success(request, 'Resumen eliminado.')
        return redirect('index')
    return render(request, 'app/confirm_delete.html', {'doc': doc})
