from django.db import models
from django.utils import timezone
import uuid


class DocumentSummary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_filename = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    summary = models.TextField()
    word_count = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Resumen de documento'
        verbose_name_plural = 'Resúmenes de documentos'

    def __str__(self):
        return f"{self.original_filename} — {self.uploaded_at.strftime('%d/%m/%Y')}"


class SimilarityRequest(models.Model):
    source = models.ForeignKey(
        DocumentSummary, on_delete=models.CASCADE,
        related_name='similarity_requests'
    )
    compared_with = models.ManyToManyField(
        DocumentSummary,
        related_name='compared_in',
        blank=True
    )
    results = models.JSONField(default=list)
    requested_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-requested_at']
        verbose_name = 'Solicitud de similitud'
        verbose_name_plural = 'Solicitudes de similitud'
