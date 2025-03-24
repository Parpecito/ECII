import subprocess
import time


def desplegar_back():
    subprocess.Popen(["powershell", "-NoExit", "-Command", "uvicorn backend.backend:app --reload"], creationflags=subprocess.CREATE_NEW_CONSOLE)

def desplegar_front():
    subprocess.Popen(["powershell", "-NoExit", "-Command", "streamlit run frontend/frontend.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)

if __name__ == '__main__':
    print("Desplegando backend...")
    desplegar_back()
    time.sleep(15)
    print("Desplegando frontend...")
    desplegar_front()