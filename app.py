import streamlit as st
import pandas as pd
import io

st.set_page_config(
    page_title="Procesador SIGCOM – Rut + Ley",
    layout="wide",
    page_icon="📊"
)

# --- Estilos CSS ---
st.markdown("""
    <style>
        .reportview-container { 
            background-color: #f5f7fa; 
        }
        .main { 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
        }
        .title {
            font-size: 32px;
            font-weight: 700;
            color: #2b6cb0;
        }
        .sub {
            font-size: 18px;
            color: #4a5568;
        }
    </style>
""", unsafe_allow_html=True)

# Título
st.markdown("<div class='title'>📘 Procesador SIGCOM – AGRUPACIÓN RUT + LEY</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Sube tu archivo SIGCOM y se generará automáticamente el resumen consolidado sin duplicar RUT por Ley.</div>", unsafe_allow_html=True)
st.write("")

# --- Subida de archivo ---
uploaded_file = st.file_uploader("📤 Sube tu archivo Excel SIGCOM", type=["xlsx"])

if uploaded_file:

    st.success("Archivo cargado correctamente ✔")

    # Intentar leer la hoja DOTACION; si no existe, leer la primera hoja
    try:
        df = pd.read_excel(uploaded_file, sheet_name="DOTACION")
    except Exception:
        df = pd.read_excel(uploaded_file)

    st.subheader("📋 Vista previa del archivo original")
    st.dataframe(df.head(20), use_container_width=True)

    # Guardar orden original de columnas
    columnas_originales = list(df.columns)

    # Detectar nombre exacto de la columna de Horas realizadas
    # Puede ser "Horas \nrealizadas" o "Horas realizadas"
    col_horas_realizadas = None
    for posible in ["Horas \nrealizadas", "Horas realizadas"]:
        if posible in df.columns:
            col_horas_realizadas = posible
            break

    # Columnas de montos (a sumar) + horas realizadas
    cols_montos = [
        "Remuneración",
        "Honorarios",
        "Horas \nExtras",
        "Reemplazo /\nSuplencia",
        "Bonos",
        "Asignación \nde Zona",
        "Compra \nServicios RRHH",
        "Comisión de Servicio Recibido",
        "Comisión de Servicio Cedido",
    ]

    # Agregar Horas realizadas si existe la columna
    if col_horas_realizadas is not None:
        cols_montos.append(col_horas_realizadas)

    # Convertir montos y horas realizadas a números
    for c in cols_montos:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # Agrupar por Rut + Nro Ley (regla que definimos)
    group_cols = ["Rut", "Nro Ley"]

    # Diccionario de agregación: montos y horas → suma
    agg_dict = {c: "sum" for c in cols_montos}

    # Otras columnas → tomar la primera aparición
    for c in df.columns:
        if c not in group_cols and c not in cols_montos:
            agg_dict[c] = "first"

    # Agrupación final
    resumen = df.groupby(group_cols, as_index=False).agg(agg_dict)

    # Mantener el orden original de columnas en la salida
    columnas_finales = [c for c in columnas_originales if c in resumen.columns]
    resumen = resumen[columnas_finales]

    st.subheader("📊 Resultado Consolidado (Sin duplicados de RUT por Ley)")
    st.dataframe(resumen, use_container_width=True)

    # Preparar archivo Excel para descarga
    buffer = io.BytesIO()
    resumen.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="📥 Descargar archivo consolidado",
        data=buffer,
        file_name="SIGCOM_Procesado_Rut_Ley.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Por favor, sube un archivo Excel para comenzar.")

st.markdown("---")
st.markdown("### 💡 *Desarrollado por Alejandra Rodríguez*")
