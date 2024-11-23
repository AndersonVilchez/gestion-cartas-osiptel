import streamlit as st
import pandas as pd
import datetime as dt
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Acceder a las credenciales desde los secretos de Streamlit
firebase_secrets = st.secrets["firebase"]

# Crear un diccionario con las credenciales
cred_dict = {
    "type": firebase_secrets["type"],
    "project_id": firebase_secrets["project_id"],
    "private_key_id": firebase_secrets["private_key_id"],
    "private_key": firebase_secrets["private_key"].replace("\\n", "\n"),
    "client_email": firebase_secrets["client_email"],
    "client_id": firebase_secrets["client_id"],
    "auth_uri": firebase_secrets["auth_uri"],
    "token_uri": firebase_secrets["token_uri"],
    "auth_provider_x509_cert_url": firebase_secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": firebase_secrets["client_x509_cert_url"]
}

# Inicializar Firebase con las credenciales
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

# Inicialización de Firestore
db = firestore.client()

# Función para calcular la fecha límite (excluye fines de semana)
def calcular_fecha_limite(fecha_inicio, dias_habiles):
    fecha = fecha_inicio
    while dias_habiles > 0:
        fecha += dt.timedelta(days=1)
        if fecha.weekday() < 5:  # Excluye sábados (5) y domingos (6)
            dias_habiles -= 1
    return fecha

# Título principal
st.title("Gestión de Cartas de OSIPTEL")

# --- Sección 1: Ingresar nueva carta ---
st.header("📩 Ingresar Nueva Carta")
with st.form("nueva_carta_form"):
    trabajador = st.selectbox("Responsable", ["Britcia", "Rosaly", "Anderson", "Renato", "Marisol"])
    nombre_carta = st.text_input("Nombre de la Carta")
    fecha_notificacion = st.date_input("Fecha de Notificación")
    dias_habiles = st.number_input("Días Hábiles para Responder", min_value=1, step=1)
    
    if st.form_submit_button("Registrar Carta"):
        fecha_limite = calcular_fecha_limite(fecha_notificacion, dias_habiles)
        nueva_carta = {
            "Trabajador": trabajador,
            "Nombre_Carta": nombre_carta,
            "Fecha_Notificación": fecha_notificacion,
            "Días_Hábiles": dias_habiles,
            "Fecha_Límite": fecha_limite,
            "Estatus": "Pendiente",
            "Fecha_Respuesta": None,
            "Número_Carta_Respuesta": None
        }
        
        # Guardar en Firestore
        db.collection('cartas').add(nueva_carta)
        
        st.success("Carta registrada correctamente.")

# --- Sección 2: Actualizar estado ---
st.header("✅ Actualizar Estado de Carta")
cartas_ref = db.collection('cartas')
cartas = cartas_ref.stream()

cartas_db = pd.DataFrame(columns=["ID", "Trabajador", "Nombre_Carta", "Fecha_Notificación", "Días_Hábiles", 
                                  "Fecha_Límite", "Estatus", "Fecha_Respuesta", "Número_Carta_Respuesta"])

for idx, carta in enumerate(cartas):
    data = carta.to_dict()
    data["ID"] = carta.id
    cartas_db = pd.concat([cartas_db, pd.DataFrame([data])], ignore_index=True)

if not cartas_db.empty:
    with st.form("actualizar_estado_form"):
        opciones_carta = cartas_db["ID"].astype(str) + " - " + cartas_db["Nombre_Carta"]
        id_carta = st.selectbox("Seleccionar Carta (ID - Nombre)", opciones_carta)
        id_carta = id_carta.split(" - ")[0]
        estatus = st.selectbox("Estatus", ["Pendiente", "Atendida"])
        numero_respuesta = st.text_input("Número de Carta de Respuesta (Opcional)")
        fecha_respuesta = st.date_input("Fecha de Respuesta (Opcional)", dt.date.today())
        
        if st.form_submit_button("Actualizar Carta"):
            # Actualizar en Firestore
            carta_ref = db.collection('cartas').document(id_carta)
            carta_ref.update({
                "Estatus": estatus,
                "Número_Carta_Respuesta": numero_respuesta,
                "Fecha_Respuesta": fecha_respuesta
            })
            st.success("Carta actualizada correctamente.")
else:
    st.warning("No hay cartas registradas para actualizar.")

# --- Sección 3: Visualización ---
st.header("📊 Visualización de Datos")
if not cartas_db.empty:
    st.subheader("Base de Datos de Cartas")
    st.dataframe(cartas_db)
