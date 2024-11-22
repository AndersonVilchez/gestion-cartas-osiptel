import streamlit as st
import pandas as pd
import datetime as dt
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configurar conexión con Google Sheets
def conectar_google_sheets(sheet_name):
    # Definir el alcance de permisos
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Leer credenciales desde el archivo JSON
    creds = ServiceAccountCredentials.from_json_keyfile_name("streamlit-sheets-service@root-bricolage-442522-h4.iam.gserviceaccount.com", scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1  # Abrir la primera hoja
    return sheet

# Conectar con la hoja de cálculo
sheet_name = "Gestión de Cartas"  # Nombre de tu hoja en Google Sheets
sheet = conectar_google_sheets(sheet_name)

# Función para calcular la fecha límite
def calcular_fecha_limite(fecha_inicio, dias_habiles):
    fecha = fecha_inicio
    while dias_habiles > 0:
        fecha += dt.timedelta(days=1)
        if fecha.weekday() < 5:  # Excluir fines de semana
            dias_habiles -= 1
    return fecha

# Título de la app
st.title("Gestión de Cartas en Tiempo Real con Google Sheets")

# --- Sección 1: Ingresar nueva carta ---
st.header("📩 Ingresar Nueva Carta")
with st.form("nueva_carta_form"):
    trabajador = st.selectbox("Responsable", ["Britcia", "Rosaly", "Anderson", "Renato", "Marisol"])
    nombre_carta = st.text_input("Nombre de la Carta")
    fecha_notificacion = st.date_input("Fecha de Notificación", dt.date.today())
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
        sheet.append_row(nueva_carta)  # Guardar en Google Sheets
        st.success("Carta registrada correctamente.")

# --- Sección 2: Visualizar datos ---
st.header("📊 Visualización de Datos en Tiempo Real")
data = sheet.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0])  # Ignorar encabezados
if not df.empty:
    st.dataframe(df)
else:
    st.warning("No hay datos registrados.")
