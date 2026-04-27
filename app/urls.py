from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_document, name='upload'),
    path('resumen/<uuid:pk>/', views.detail, name='detail'),
    path('resumen/<uuid:pk>/similitud/', views.check_similarity, name='similarity'),
    path('resumen/<uuid:pk>/eliminar/', views.delete_summary, name='delete'),
]
