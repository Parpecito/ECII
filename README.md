# 🎙️ Transcriptor y Resumidor de Reuniones

Este proyecto permite transcribir audios (por ejemplo, de reuniones) y generar automáticamente un resumen del contenido, utilizando **Whisper** para la transcripción y la **API de Mistral** para el resumen. Incluye una interfaz web construida con **Streamlit** y un backend desarrollado con **FastAPI**.

---

## 🚀 Funcionalidades

- Subida de archivos de audio (`.mp3`, `.wav`, `.m4a`)
- Transcripción automática mediante Whisper (modelo `medium`, en local)
- Resumen automático (corto, medio o largo) usando la API pública de Mistral
- Visualización de transcripción y resumen
- Historial de audios procesados
- Interfaz sencilla y clara desarrollada con Streamlit

---

## 🛠️ Tecnologías utilizadas

| Componente     | Tecnología           |
|----------------|----------------------|
| Backend        | FastAPI              |
| Frontend       | Streamlit            |
| IA - Transcripción | Whisper (local) |
| IA - Resumen   | API de Mistral       |
| Base de datos  | PostgreSQL           |

---

## Este programa se va a ejecutar en local
### 1. Clona el repositorio
```bash
git clone https://github.com/Parpecito/ECII.git
cd ECII
```
### 2. Crea un entorno virtual e instala todas las dependencias
```bash
python -m venv venv
venv\Scripts\activate         # En Windows
# o en macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```
### 3. Configura las variables de entorno
Tendrás que crear un arhivo .env con las claves necesarias para que funcione el programa en el ordenador (Nos encontraremos un ejemplo en env.example)
### 4. Ejecuta el programa
```bash
python main.py
```
## Para que la aplicación funcione correctamente en local, necesitarás instalar PostgreSQL y crear una base de datos siguiendo estos pasos:
```bash
host="localhost",
    dbname='postgres',
    user='postgres',
    password=os.getenv("POSTGRES_PASSWORD"),
    port=5432
```
---
Si cambias algun nombre lo tienes que cambiar en tu código (Es recomendable llamarlo de la misma forma)
