import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

def conectar_firebase():
    # Obtener las credenciales de Streamlit Secrets
    cred_json = {
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"],
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
    }
    
    # Inicializar la conexión con Firebase si aún no está conectada
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.Certificate(cred_json))
    
    # Acceder a la base de datos Firestore
    db = firestore.client()
    return db

def mostrar_datos():
    db = conectar_firebase()
    # Acceder a una colección de ejemplo en Firestore
    cartas_ref = db.collection('cartas')
    docs = cartas_ref.stream()

    # Mostrar los datos en Streamlit
    for doc in docs:
        st.write(f"ID: {doc.id}, Data: {doc.to_dict()}")

# Título de la app
st.title('Conexión a Firebase Firestore')

# Llamada para mostrar los datos
mostrar_datos()
