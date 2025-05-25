import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"



#https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state

if "transcription" not in st.session_state:
    st.session_state.transcription = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "reset_audio" not in st.session_state:
    st.session_state.reset_audio = False
if "subida_exitosa" not in st.session_state:
    st.session_state.subida_exitosa = False
if "file_upload" not in st.session_state:
    st.session_state.file_upload = 0
if "inicio" not in st.session_state:
    st.session_state.inicio = False
if "audio" not in st.session_state:
    st.session_state.audio = None
if "audio_nombrearchivo" not in st.session_state:
    st.session_state.audio_nombrearchivo = None


if st.session_state.reset_audio:
    st.session_state.reset_audio = False
    st.session_state.transcription = None
    st.session_state.summary = None
    st.session_state.inicio=False
    st.session_state.subida_exitosa = False
    st.session_state.audio = None
    st.session_state.audio_nombrearchivo = None
    st.session_state.file_upload += 1
    



def obtener_historial():
    response=requests.get(f"{BACKEND_URL}/historial-audios/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error('No se ha obtenido el historial de audios')
        return []

st.title("Transcriptor y Resumidor de Reuniones 🎙️✍️")




st.sidebar.title("Historial de audios")
st.sidebar.write("Aquí encontrarás los audios que has subido anteriormente.")

historial_audios = obtener_historial()

if "historial" in historial_audios:
    for item in historial_audios["historial"]:
        nombre = item["filename"] if item["filename"] else f"Audio ID {item['id']}"
        with st.sidebar.expander(nombre):
            st.write(f"Transcripción: {item['transcription']}")
            st.write(f"Resumen: {item['summary']}")
else:
    st.sidebar.write("No hay audios en el historial.")



longitud=st.radio("Selecciona la longitud del resumen:", ["Corto", "Medio", "Largo"])
l={
        "Corto": "corto",
        "Medio": "medio",
        "Largo": "largo"
    }
longitud_seleccionada=l[longitud]

  


# Aquí se subira el archivo de audio
uploaded_file = st.file_uploader("Sube un archivo de audio:", type=["mp3", "wav", "m4a"], key=st.session_state.file_upload)

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/mp3")

   
    if not st.session_state.inicio:
        if st.button("Iniciar transcripción"):
            st.session_state.audio = uploaded_file.read()
            st.session_state.audio_nombrearchivo = uploaded_file.name
            st.session_state.inicio = True
            st.rerun()
   

    
    if not st.session_state.subida_exitosa and st.session_state.inicio:
    # El archivo va a pasar al backend
        with uploaded_file as audio_file:
            files = {"file": (st.session_state.audio_nombrearchivo, st.session_state.audio, "audio/mp3")}
            response_upload = requests.post(f"{BACKEND_URL}/upload-audio/", files=files)

        if response_upload.status_code == 200:
            
            data_upload = response_upload.json()
            file_path = data_upload["filename"]
            audio_id = data_upload["id"]
            st.success("✅ Archivo subido correctamente.")
            st.session_state.subida_exitosa = True
        
            #Transcribir el audio usando el file_path recibido
            st.write("📝 Transcribiendo el audio...")

            response_transcribe = requests.post(f"{BACKEND_URL}/transcribir-audio/",
                                                json={
                                                    "filename": file_path,
                                                    "id": audio_id
                                                })

            if response_transcribe.status_code == 200:
                data_transcribe = response_transcribe.json()
                if "transcription" in data_transcribe:
                    transcription = data_transcribe["transcription"]
                else:
                    st.error("❌ La respuesta del backend no contiene transcription")
                    st.stop()


                st.subheader("📄 Transcripción")
                st.text_area("Texto transcrito:", transcription, height=200)



                response_resumir=requests.post(f"{BACKEND_URL}/resumir-transcripcion/", 
                                               json={
                                                    "transcription": transcription,
                                                    "longitud": longitud_seleccionada,
                                                    "id": audio_id
                                                }
                                               )
                
                if response_resumir.status_code == 200:
                    data_resumen=response_resumir.json()

                    if "summary" in data_resumen:
                        resumen=data_resumen['summary']
                        st.session_state.transcription = transcription                                                  #Guardar la transcripción en el estado de sesión
                        st.session_state.summary = resumen                                                              #Guardar el resumen en el estado de sesión
                        
                        st.subheader("📝 Resumen")
                        st.text_area("Texto resumido:", resumen, height=200)

                        historial_audios = obtener_historial()

                        if st.button("Guardar audio"):
                            st.session_state.reset_audio = True
                            
                    else:
                        st.error("❌ La respuesta del backend no contiene summary")
                    
                else:
                    st.error("❌ Error al resumir el texto. Intenta de nuevo.")
            else:
                st.error("❌ Error al transcribir el audio. Intenta de nuevo.")

        else:
            st.error("❌ Error al subir el archivo. Intenta de nuevo.")
