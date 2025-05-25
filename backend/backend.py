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
    CREATE TABLE IF NOT EXISTS Historial_Audio (
        id SERIAL PRIMARY KEY,
        filename TEXT,
        transcription TEXT,
        summary TEXT
    )
    """)

conn.commit()


app = FastAPI()

carpeta_temporal = "temporal"
os.makedirs(carpeta_temporal, exist_ok=True)

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    audio_path = os.path.join(carpeta_temporal, file.filename)


    with open(audio_path, "wb") as audio_file:
        audio_file.write(await file.read())

    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO Historial_Audio (filename) VALUES (%s) RETURNING id", (file.filename,))
            id_audio = cur.fetchone()[0]
            conn.commit()
            return{
                "message": "Audio subido correctamente",
                "filename": file.filename,
                "id": id_audio
                
           }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al guardar el archivo en la base de datos: {str(e)}")
    


class Transcripcion(BaseModel):
    id: int
    filename: str

model = whisper.load_model("medium")

@app.post('/transcribir-audio/')
def transcribir_audio(request: Transcripcion):

    archivo = request.filename
    archivo_final = os.path.join(carpeta_temporal, archivo)

    if not os.path.exists(archivo_final):
        return HTTPException(status_code=400, detail="Carpeta temporal no existe")
        
    resultado= model.transcribe(archivo_final)
    transcription = resultado["text"]

    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE Historial_Audio SET transcription = %s WHERE id = %s", (transcription, request.id))
            conn.commit()
    except Exception as e:
        return HTTPException(status_code=400, detail=f" Error al guardar la transcripción: {str(e)}")

    return {"transcription": transcription}



class Resumen(BaseModel):
    id: int
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
            "content": (
                f"Quiero que leas el siguiente texto y lo resumas en un único párrafo claro y conciso."
                f"En el resumen, destaca las ideas principales y evita repetir detalles innecesarios o ejemplos."
                f"Utiliza un lenguaje directo, profesional y fácil de entender. "
                f"Este resumen debe ajustarse a un máximo de {tokens} tokens, así que prioriza la información esencial.\n\n"
                f"Texto original:\n{archivo}"
            )

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
                cur.execute("UPDATE Historial_Audio  SET summary=%s WHERE id=%s", (resumen, request.id))
                conn.commit()
        except Exception as e:
            return HTTPException(status_code=400, detail=f"Error al guardar el resumen: {str(e)}")

        return {"summary": resumen}



@app.get("/historial-audios/")
def obtener_historial():
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Historial_Audio")
            historial=[{
                "id": row[0],
                "filename": row[1],
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

