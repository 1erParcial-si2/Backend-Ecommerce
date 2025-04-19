# Proyecto SI2-P1-Backend

Este es el backend del proyecto SI2-P1, desarrollado en **Django Rest Framework**.

## 📌 Requisitos
- **Python 3.13** instalado
- **pip** y **virtualenv** disponibles
- **PostgreSQL** (si el proyecto usa esta base de datos)

## 🚀 Instalación

### 1️⃣ Crear y activar el entorno virtual
```bash
# Crear el entorno virtual
python -m venv .venv

# Activar el entorno virtual
# En Windows
.venv\Scripts\activate

# En Linux/Mac
source .venv/bin/activate
```

### 2️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3️⃣ Aplicar migraciones y ejecutar el servidor
```bash
# Aplicar migraciones a la base de datos
python manage.py migrate

# Crear un superusuario (opcional, para acceder al admin)
python manage.py createsuperuser

# Ejecutar el servidor
python manage.py runserver
```

## 📄 Documentación con Swagger
La documentación interactiva de la API está disponible en:

🔗 [http://localhost:8000/swagger/](http://localhost:8000/swagger/)

## 📌 Comandos útiles
- **Salir del entorno virtual**:
  ```bash
  deactivate
  ```
- **Actualizar dependencias y guardar cambios en `requirements.txt`**:
  ```bash
  pip freeze > requirements.txt
  ```

---
MODELO (models.py)
   ↓
SERIALIZER (serializers.py)
   ↓
VIEWSET (views.py)
   ↓
RUTAS (urls.py) → No lo vimos, pero es donde se conectan estas vistas
   ↓
CLIENTE (Angular u otro)


📅 **Fecha de última actualización**: [5/4/2025]

