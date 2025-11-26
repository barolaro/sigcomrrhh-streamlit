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

# título
st.markdown("<div class='title'>📘 Procesador SIGCOM – AGRUPACIÓN RUT + LEY</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Sube tu archivo SIGCOM y se generará automáticamente el resumen consolidado.</div>", unsafe_allow_html=True)
st.write("")

# --- Subida de archivo ---
uploaded_file = st.file_uploader("📤 Sube tu archivo Excel SIGCOM", type=["xlsx"])

if uploaded_file:

    st.success("Archivo cargado correctamente ✔")
    
    # leer excel (hoja DOTACION)
    try:
        df = pd.read_excel(uploaded_file, sheet_name="DOTACION")
    except:
        df = pd.read_excel(uploaded_file)  # por si la hoja tiene otro nombre

    st.subheader("📋 Vista previa del archivo original")
    st.dataframe(df.head(20), use_container_width=True)

    # guardar orden de columnas
    columnas_originales = list(df.columns)

    # columnas de montos
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

    # convertir montos a números
    for c in cols_montos:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # agrupar por rut + ley
    group_cols = ["Rut", "Nro Ley"]
    agg_dict = {c: "sum" for c in cols_montos}

    # otras columnas → first
    for c in df.columns:
        if c not in group_cols and c not in cols_montos:
            agg_dict[c] = "first"

    # agrupación final
    resumen = df.groupby(group_cols, as_index=False).agg(agg_dict)

    # mantener orden original
    columnas_finales = [c for c in columnas_originales if c in resumen.columns]
    resumen = resumen[columnas_finales]

    st.subheader("📊 Resultado Consolidado (Sin duplicados)")
    st.dataframe(resumen, use_container_width=True)

    # preparar archivo para descarga
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
