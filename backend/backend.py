from fastapi import FastAPI, UploadFile, File, HTTPException
import psycopg2
import whisper
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests

load_dotenv()



#https://www.youtube.com/watch?v=miEFm1CyjfM

def db_conexion():
    return psycopg2.connect(
    host="localhost",
    dbname='postgres',
    user='postgres',
    password=os.getenv("POSTGRES_PASSWORD"),
    port=5432
    )

conn=db_conexion()

with conn.cursor() as cur:
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Resumenes (
        id SERIAL PRIMARY KEY,
        transcription TEXT,
        summary TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Historial_Audio (
        id SERIAL PRIMARY KEY,
        file_path TEXT,
        transcription TEXT,
        summary TEXT
    )
    """)

conn.commit()


app = FastAPI()

carpeta_temporal = "temporal"
os.makedirs(carpeta_temporal, exist_ok=True)
model = whisper.load_model("medium")

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    audio_path = os.path.join(carpeta_temporal, file.filename)

    with open(audio_path, "wb") as audio_file:
        audio_file.write(await file.read())

    return{"message": "Audio subido correctamente",
           "file_path": audio_path
           }


class Transcripcion(BaseModel):
    file_path: str

@app.post('/transcribir-audio/')
def transcribir_audio(request: Transcripcion):

    archivo = request.file_path


    if not os.path.exists(archivo):
        return HTTPException(status_code=400, detail="Carpeta temporal no existe")
        
    resultado= model.transcribe(archivo)
    transcription = resultado["text"]

    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO Resumenes (transcription) VALUES (%s)", (transcription,))
            conn.commit()
    except Exception as e:
        return HTTPException(status_code=400, detail=f" Error al guardar la transcripción: {str(e)}")

    return {"transcription": transcription}



class Resumen(BaseModel):
    transcription: str
    longitud: str

@app.post('/resumir-transcripcion/')
def resumir_transcripcion(request: Resumen):
    #https://www.youtube.com/watch?v=11pIpoJJQhQ Esto es para mistral su api
    
    #https://docs.mistral.ai/api/#tag/chat/operation/chat_completion_v1_chat_completions_post Aqui esta lo que devolvería el post
    #https://openrouter.ai/mistralai/mistral-small-24b-instruct-2501:free/api

    API_KEY = os.getenv("MISTRAL_API_KEY")
    API_URL="https://api.mistral.ai/v1/chat/completions" #https://docs.mistral.ai/api/#tag/chat



    if not API_KEY:
        return HTTPException(status_code=400, detail="API KEY no encontrada")
    
    archivo=request.transcription
    longitud=request.longitud

    if longitud=="corto":
        tokens=100
    elif longitud=="medio":
        tokens=200
    elif longitud=="largo":
        tokens=500
    else:
        return HTTPException(status_code=400, detail="Longitud no válida")
    
    headers={
        'Authorization': f"Bearer {API_KEY}",
        'Content-Type': 'application/json'
    }
    
    
    data= {
        "model": 'mistral-small-latest',
        "messages":[
            {"role":"user",
            "content":f"Resume el siguiente texto en un parrafo: {archivo}"
            }],
        "max_tokens": tokens
    }
    response=requests.post(API_URL,json=data,headers=headers)


    if response.status_code != 200:
        return HTTPException(status_code=400, detail=f"Error al resumir el texto:   {response.text}")
    else:
        resumen=response.json()['choices'][0]['message']['content'].strip()
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE Resumenes SET summary=%s WHERE transcription=%s", (resumen, archivo))
                conn.commit()
        except Exception as e:
            return HTTPException(status_code=400, detail=f"Error al guardar el resumen: {str(e)}")

        return {"summary": resumen}


@app.post("/guardar-historial/")
def guardar_historial(file_path: str, transcription: str, summary: str):
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO Historial_Audio (file_path, transcription, summary) VALUES (%s, %s, %s)", (file_path, transcription, summary))
            conn.commit()
    except Exception as e:
        return HTTPException(status_code=400, detail=f"Error al guardar el historial: {str(e)}")

    return {"message": "Historial guardado correctamente"}

@app.get("/historial-audios/")
def obtener_historial():
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Historial_Audio")
            historial=[{
                "id": row[0],
                "file_path": row[1],
                "transcription": row[2],
                "summary": row[3] if row[3] else "No hay resumen disponible"
            } for row in cur.fetchall() 
            
            ]
            
    except Exception as e:
        return HTTPException(status_code=400, detail=f"Error al obtener el historial: {str(e)}")
    
    return {"historial": historial}

@app.get("/")
def read_root():
    return {"message": "Backend is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

