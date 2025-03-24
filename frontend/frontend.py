import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"



#https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state

if "transcription" not in st.session_state:
    st.session_state.transcription = None
if "summary" not in st.session_state:
    st.session_state.summary = None


def obtener_historial():
    response=requests.get(f"{BACKEND_URL}/historial-audios/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error('No se ha obtenido el historial de audios')
        return []

st.title("Transcriptor y Resumen de Reuniones 🎙️✍️")

if st.button("Nuevo audio"):
    st.session_state.transcription = None
    st.session_state.summary = None
    st.experimental_rerun()



st.sidebar.title("Historial de audios")
st.sidebar.write("Aquí encontrarás los audios que has subido anteriormente.")

historial_audios = obtener_historial()

if "historial" in historial_audios:
    for item in historial_audios["historial"]: 
        with st.sidebar.expander(f"{item['file_path']}"):
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

  

# 🔹 Subir archivo de audio
uploaded_file = st.file_uploader("Sube un archivo de audio:", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/mp3")


    # 📌 Paso 1: Subir el archivo al backend
    with uploaded_file as audio_file:
        files = {"file": (uploaded_file.name, audio_file, "audio/mp3")}
        response_upload = requests.post(f"{BACKEND_URL}/upload-audio/", files=files)

    if response_upload.status_code == 200:
        data_upload = response_upload.json()
        file_path = data_upload["file_path"]

        st.success("✅ Archivo subido correctamente.")

        # 📌 Paso 2: Transcribir el audio usando el file_path recibido
        st.write("📝 Transcribiendo el audio...")

        response_transcribe = requests.post(f"{BACKEND_URL}/transcribir-audio/", json={"file_path": file_path})

        if response_transcribe.status_code == 200:
            data_transcribe = response_transcribe.json()
            transcription = data_transcribe["transcription"]

            st.subheader("📄 Transcripción")
            st.text_area("Texto transcrito:", transcription, height=200)



            response_resumir=requests.post(f"{BACKEND_URL}/resumir-transcripcion/", json={"transcription": transcription, "longitud": longitud_seleccionada})
            
            if response_resumir.status_code == 200:
                data_resumen=response_resumir.json()

                if "summary" in data_resumen:
                    resumen=data_resumen['summary']
                    st.subheader("📝 Resumen")
                    st.text_area("Texto resumido:", resumen, height=200)
                else:
                    st.error("❌ La respuesta del backend no contiene summary")
                
            else:
                st.error("❌ Error al resumir el texto. Intenta de nuevo.")
        else:
            st.error("❌ Error al transcribir el audio. Intenta de nuevo.")

    else:
        st.error("❌ Error al subir el archivo. Intenta de nuevo.")

if st.session_state.transcription:
    st.button("Nuevo chat",on_click=lambda: st.experimental_rerun())
