import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# --- CONFIGURACIÓN INICIAL DE LA PÁGINA (ESTILO DARK MODE) ---
st.set_page_config(page_title="Dashboard Comando Institucional", layout="wide", initial_sidebar_state="collapsed")

# CSS personalizado para oscurecer y darle el toque "Sala de Crisis"
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    h1, h2, h3 { color: #E0E0E0 !important; }
    .kpi-box { 
        background-color: #1E2026; padding: 20px; border-radius: 12px; 
        border-left: 5px solid #D4AF37; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .kpi-title { color: #8B929A; font-size: 14px; text-transform: uppercase; font-weight: 600; }
    .kpi-value { color: #D4AF37; font-size: 42px; font-weight: 700; margin: 5px 0; }
    .kpi-sub { color: #E0E0E0; font-size: 16px; }
    .kpi-var { color: #4CAF50; font-size: 14px; font-weight: 500; } # Verde para variación positiva
    .stDataFrame { background-color: #1E2026; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
# IMPORTANTE: Reemplaza 'tu_archivo_json.json' con el nombre de tu archivo de llave API
# Y asegúrate de que esté en la misma carpeta que este script.
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name('/mount/src/dashboard-institucional/tu_archivo_json.json', SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1mAA4Uu7m6UqHvc9X6zysMpkU0hDKBze7HcHDDJIHuEE")
    st.success("✅ Conectado exitosamente a Google Sheets.")
except Exception as e:
    st.error(f"❌ Error de conexión: {e}. Verifica que el archivo JSON esté en la carpeta.")
    st.stop()

# --- 1. EXTRACCIÓN DE DATOS DE DROGAS (HOJA DROGA 2026) ---
ws_drogas = sheet.worksheet("DROGA 2026")

# Leer celdas específicas para el acumulado y variación
total_2025_celda = ws_drogas.acell('D32').value
total_2026_celda = ws_drogas.acell('E32').value
variacion_celda = ws_drogas.acell('G32').value

# Leer la tabla de tipos de droga para el gráfico (Rango C41:C45 y P41:P45)
# Suponiendo que P columna tiene los totales acumulados por tipo de droga para 2026
try:
    tipos_drogas = ws_drogas.range('C41:C45')
    totales_drogas = ws_drogas.range('P41:P45')
    
    # Procesar datos para el gráfico
    data_drogas = {}
    for i in range(5): # 5 tipos de droga
        nombre = tipos_drogas[i].value.strip()
        valor_str = totales_drogas[i].value.replace('.', '').replace(',', '.') # Convertir formato 107.430,3 a 107430.3
        try:
            valor = float(valor_str)
        except:
            valor = 0
        data_drogas[nombre] = valor
        
    df_drogas = pd.DataFrame(list(data_drogas.items()), columns=['Tipo Droga', 'Kilos'])
except Exception as e:
    st.warning("⚠️ No se pudo leer la tabla de drogas. Revisa el rango C41:C45 y P41:P45.")

# --- 2. EXTRACCIÓN DE DATOS DE ARMAS Y VEHÍCULOS (HOJA INFORME 2026) ---
ws_informe = sheet.worksheet("INFORME 2026")

# Leer celdas específicas de Armas
try:
    total_armas = ws_informe.acell('J79').value # Total Armas Fuego
    pistolas = ws_informe.acell('J76').value
    revolver = ws_informe.acell('J75').value
    largas = ws_informe.acell('J77').value
    hechizas = ws_informe.acell('J78').value
except:
    total_armas = pistolas = revolver = largas = hechizas = 0

# Leer celda específica de Vehículos
try:
    total_vehiculos = ws_informe.acell('P14').value
except:
    total_vehiculos = 0

# --- 3. CONSTRUCCIÓN DEL DASHBOARD ---
st.markdown("<h1 style='text-align: center;'>DASHBOARD OPERATIVO DE COMANDO INSTITUCIONAL</h1>", unsafe_allow_html=True)
st.caption(f"📅 Datos actualizados a la semana del {datetime.datetime.now().strftime('%d-%m-%Y')}")

# -- TARJETAS SUPERIORES (KPI's) --
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-title">Drogas Incautadas</div>
        <div class="kpi-value">{total_2026_celda} <span style="font-size:20px; color:#E0E0E0;">Kg</span></div>
        <div class="kpi-sub">Vs 2025: <span class="kpi-var">{variacion_celda}</span></div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-title">Armas de Fuego Incautadas</div>
        <div class="kpi-value">{total_armas}</div>
        <div class="kpi-sub">{pistolas} Pistola · {revolver} Revólver · {largas} Largas · {hechizas} Hechiza</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # Aún no tenemos el dato de bandas en las hojas, es un placeholder
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-title">Asociaciones Delictuales</div>
        <div class="kpi-value">-</div>
        <div class="kpi-sub">Por definir según base de datos</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-title">Vehículos Recuperados</div>
        <div class="kpi-value">{total_vehiculos}</div>
        <div class="kpi-sub">Incautaciones efectivas 2026</div>
    </div>
    """, unsafe_allow_html=True)

# -- GRÁFICO Y DETALLE --
st.markdown("---")
col_graph, col_table = st.columns([2, 1])

with col_graph:
    st.subheader("📊 Distribución de Drogas por Tipo (2026)")
    if 'df_drogas' in locals() and not df_drogas.empty:
        st.bar_chart(df_drogas.set_index('Tipo Droga'), color="#D4AF37")
    else:
        st.write("No hay datos disponibles para el gráfico de drogas.")

with col_table:
    st.subheader("📋 Resumen Operativo")
    datos_tabla = {
        "Indicador": ["Armas Totales", "Pistolas", "Revólveres", "Largas/Hechizas", "Vehículos"],
        "Cantidad": [total_armas, pistolas, revolver, f"{largas} / {hechizas}", total_vehiculos]
    }
    df_resumen = pd.DataFrame(datos_tabla)
    st.dataframe(df_resumen, use_container_width=True, hide_index=True)

st.success("🚀 Dashboard ejecutándose correctamente. Puedes actualizar la página si los datos en Google Sheets cambian.")
