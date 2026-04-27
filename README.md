# ResumIA — Resumidor de documentos

Aplicación Django que resume documentos PDF/Word de menos de 1,000 palabras
y permite comparar similitud entre resúmenes.

## Instalación rápida

```bash
# 1. Clonar / descomprimir el proyecto
cd summarizer/

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear la base de datos
python manage.py migrate

# 5. (Opcional) Crear superusuario para /admin
python manage.py createsuperuser

# 6. Correr el servidor
python manage.py runserver
```

Abrí el navegador en **http://127.0.0.1:8000**

## Estructura del proyecto

```
summarizer/
├── manage.py
├── requirements.txt
├── summarizer/          # Configuración Django
│   ├── settings.py
│   └── urls.py
└── app/                 # Aplicación principal
    ├── models.py        # DocumentSummary, SimilarityRequest
    ├── views.py         # Upload, detalle, similitud
    ├── utils.py         # Extracción de texto + summarización
    ├── urls.py
    └── templates/app/
        ├── base.html    # Layout + animación splash
        ├── index.html   # Página principal
        └── detail.html  # Detalle + comparador
```

## Funcionalidades

- **Splash animado**: Logo guiña el ojo y gira 1 vuelta anti-horaria al cargar (solo 1 vez por sesión)
- **Upload**: PDF o DOCX hasta 1,000 palabras / 5MB
- **Resumen automático**: Extracción por TF (sin APIs externas)
- **Comparador de similitud**: Coseno TF entre resúmenes, con barra visual
- **Colores**: azul #3B82C4, amarillo #F5B800, navy #1A2744 (palette del logo)
- **Responsive**: Bootstrap 5

## Notas

- El resumen es extractivo (no generativo) — no requiere ninguna API de IA
- SQLite incluido para desarrollo; reemplazar por PostgreSQL en producción
- Los archivos subidos se guardan en `media/documents/`
