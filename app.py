import streamlit as st
import pandas as pd
import datetime as dt
import firebase_admin
from firebase_admin import credentials, db
import json

# Configurar la conexión con Firebase usando Streamlit Secrets
def conectar_firebase():
    # Cargar las credenciales desde Streamlit Secrets
    credenciales = st.secrets["firebase"]

    # Convertir las credenciales a un formato que Firebase pueda utilizar
    cred_json = {
        "type": credenciales["type"],
        "project_id": credenciales["project_id"],
        "private_key_id": credenciales["private_key_id"],
        "private_key": credenciales["private_key"].replace("\\n", "\n"),
        "client_email": credenciales["client_email"],
        "client_id": credenciales["client_id"],
        "auth_uri": credenciales["auth_uri"],
        "token_uri": credenciales["token_uri"],
        "auth_provider_x509_cert_url": credenciales["auth_provider_x509_cert_url"],
        "client_x509_cert_url": credenciales["client_x509_cert_url"]
    }

    # Inicializar la app de Firebase con las credenciales
    cred = credentials.Certificate(cred_json)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://cartas-fa5ba.firebaseio.com/'
    })

    # Referencia a la base de datos en tiempo real
    return db.reference("/cartas")

# Función para calcular la fecha límite
def calcular_fecha_limite(fecha_inicio, dias_habiles):
    fecha = fecha_inicio
    while dias_habiles > 0:
        fecha += dt.timedelta(days=1)
        if fecha.weekday() < 5:  # Excluir fines de semana
            dias_habiles -= 1
    return fecha

# Título de la app
st.title("Gestión de Cartas en Tiempo Real con Firebase")

# --- Sección 1: Ingresar nueva carta ---
st.header("📩 Ingresar Nueva Carta")
with st.form("nueva_carta_form"):
    trabajador = st.selectbox("Responsable", ["Britcia", "Rosaly", "Anderson", "Renato", "Marisol"])
    nombre_carta = st.text_input("Nombre de la Carta")
    fecha_notificacion = st.date_input("Fecha de Notificación", dt.date.today())
    dias_habiles = st.number_input("Días Hábiles para Responder", min_value=1, step=1)
    
    if st.form_submit_button("Registrar Carta"):
        fecha_limite = calcular_fecha_limite(fecha_notificacion, dias_habiles)
        nueva_carta = {
            "trabajador": trabajador,
            "nombre_carta": nombre_carta,
            "fecha_notificacion": str(fecha_notificacion),
            "dias_habiles": dias_habiles,
            "fecha_limite": str(fecha_limite),
            "estado": "Pendiente",
            "observaciones": "",
            "comentarios": ""
        }

        # Guardar en Firebase
        cartas_ref = conectar_firebase()
        cartas_ref.push(nueva_carta)
        
        st.success("Carta registrada correctamente.")

# --- Sección 2: Visualización de Datos ---
st.header("📊 Visualización de Datos en Tiempo Real")
cartas_ref = conectar_firebase()
cartas_data = cartas_ref.get()

# Convertir los datos de Firebase a un DataFrame
if cartas_data:
    df = pd.DataFrame(cartas_data).T  # Transponer para que las columnas sean las de las cartas
    st.dataframe(df)
else:
    st.warning("No hay datos registrados.")
