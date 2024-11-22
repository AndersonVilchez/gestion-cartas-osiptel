import streamlit as st
import pandas as pd
import datetime as dt
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración de Google Sheets
def conectar_google_sheets(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet

# Función para guardar datos en Google Sheets
def guardar_carta_en_sheets(sheet, data):
    sheet.append_row(data)

# Inicializar conexión con la hoja
sheet_name = "Gestión de Cartas"
sheet = conectar_google_sheets(sheet_name)

# Función para calcular fecha límite (días hábiles)
def calcular_fecha_limite(fecha_inicio, dias_habiles):
    fecha = fecha_inicio
    while dias_habiles > 0:
        fecha += dt.timedelta(days=1)
        if fecha.weekday() < 5:  # Excluye sábados y domingos
            dias_habiles -= 1
    return fecha

# Título de la app
st.title("Gestión de Cartas con Google Sheets")

# --- Sección 1: Ingresar nueva carta ---
st.header("📩 Ingresar Nueva Carta")
with st.form("nueva_carta_form"):
    trabajador = st.selectbox("Responsable", ["Britcia", "Rosaly", "Anderson", "Renato", "Marisol"])
    nombre_carta = st.text_input("Nombre de la Carta")
    fecha_notificacion = st.date_input("Fecha de Notificación")
    dias_habiles = st.number_input("Días Hábiles para Responder", min_value=1, step=1)
    
    if st.form_submit_button("Registrar Carta"):
        fecha_limite = calcular_fecha_limite(fecha_notificacion, dias_habiles)
        nueva_carta = [
            len(sheet.get_all_values()) + 1,  # ID autoincremental
            trabajador,
            nombre_carta,
            str(fecha_notificacion),
            dias_habiles,
            str(fecha_limite),
            "Pendiente",
            "",
            ""
        ]
        guardar_carta_en_sheets(sheet, nueva_carta)
        st.success("Carta registrada correctamente.")

# --- Sección 2: Visualización de datos ---
st.header("📊 Visualización de Datos")
data = sheet.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0])  # Salta los encabezados
if not df.empty:
    st.dataframe(df)
else:
    st.warning("No hay datos registrados en la hoja de cálculo.")


