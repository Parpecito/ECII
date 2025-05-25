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
Tendrás que crear un arhivo .env con las claves APi que tiene el programa para que te funcione en el ordenador
### 4. Ejecuta el programa
```bash
python main.py
```
## Además vas a necesitar descargar PostgreSQL en tu ordenador para que funcione correctamente en local, llamando a la base de datos creada como viene en el backend/backend.py con su user,host, dbname y el puerto.
