# 🐍 Backend Django - CRM API

Este proyecto es el backend de una aplicación CRM desarrollada con **Django** y **Django REST Framework**. Permite gestionar clientes, interacciones, empresas y cargar datos de prueba para desarrollo frontend.

---

## 📦 Requisitos previos

- Python 3.10 o superior
- Git

---
## 🚀 Pasos para levantar el proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/prodark88/PruebaDjango.git
cd PruebaDjango

### 2. Entorno virtual Windows
python -m venv env
env/scripts/activate

### 3. Entorno virtual MacOS/Linux
python3 -m venv env
source env/bin/activate

### 4. Instalar dependencias
pip install -r requirements.txt

### 5. Migraciones e iniciar BBDD
python manage.py makemigrations
python manage.py migrate

### 6. Levantar servidor
python manage.py runserver

### 7. Ruta
http://127.0.0.1:8000/api/clientes/
