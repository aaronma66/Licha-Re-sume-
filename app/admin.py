from django.contrib import admin
from .models import DocumentSummary, SimilarityRequest

@admin.register(DocumentSummary)
class DocumentSummaryAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'word_count', 'uploaded_at']
    readonly_fields = ['id', 'uploaded_at']

@admin.register(SimilarityRequest)
class SimilarityRequestAdmin(admin.ModelAdmin):
    list_display = ['source', 'requested_at']
    readonly_fields = ['requested_at']
