import streamlit as st 
import pandas as pd
import numpy as np

def base_layout():
    st.set_page_config(page_title="DataCore App", layout="wide")

    st.markdown("""
        <style>

        /* FONDO GLOBAL */
        .main {
            background-color: #0d1536 !important;
        }

        /* SIDEBAR */
        .sidebar .sidebar-content {
            background-color: #0a0f2b !important;
            padding-top: 20px;
        }
        .sidebar .sidebar-content h1, .sidebar .sidebar-content h2, .sidebar .sidebar-content h3 {
            color: white !important;
        }

        /* TARJETAS KPI */
        .kpi-card {
            background: #111c44;
            padding: 25px 30px;
            border-radius: 16px;
            border: 1px solid #1f2b4d;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
            text-align: center;
            transition: transform .2s ease;
        }
        .kpi-card:hover {
            transform: translateY(-4px);
        }

        .kpi-title {
            color: #9da9d8;
            font-size: 14px;
            font-weight: 500;
        }
        .kpi-value {
            color: white;
            font-size: 32px;
            font-weight: 700;
            margin-top: 5px;
        }

        /* TARJETAS NORMALES (GRÁFICAS) */
        .card {
            padding: 20px;
            border-radius: 14px;
            background-color: #111c44;
            border: 1px solid #1f2b4d;
            margin-top: 15px;
        }

        /* TÍTULOS GRANDES */
        .big-title {
            font-size: 30px;
            font-weight: 700;
            color: white;
            margin-bottom: 20px;
        }

        </style>
    """, unsafe_allow_html=True)

def general_sidebar(df_casos, df_tx):
    st.sidebar.markdown('# Paginas')

    # Inicializar la página si no existe
    if "page" not in st.session_state:
        st.session_state.page = "General"

    # Botones en loop
    paginas = ["General", "Finanzas", "Predicciones", "Machine Learning"]
    for page_name in paginas:
        if st.sidebar.button(page_name):
            st.session_state.page = page_name

    page = st.session_state.page 

    if page == "Machine Learning":
        st.sidebar.markdown('## Hiperparámetros')

        n_estimators = st.sidebar.text_input("N_estimators", "446")
        learning_rate = st.sidebar.text_input("Learning rate", "0.3")
        max_depth = st.sidebar.text_input("Max Depth", "3")
        threshold = st.sidebar.text_input("Threshold", "0.25")

        # Por ahora no usamos estos valores, pero ya queda claro
        # que en el futuro se podrían conectar a un modelo real.
        filtros = None
        return page, filtros

    st.sidebar.markdown('# Filtros')

    #Tabla intermedia para filtros
    df_calendario = (pd.concat([df_casos[['año', 'mes']], df_tx[['año', 'mes']]]).drop_duplicates().sort_values(['año', 'mes']))

    #Filtro Año y mes 
    anios = sorted(df_calendario['año'].unique())
    opciones_anio = ["Ninguno"] + [str(anio) for anio in anios]
    seleccion_a = st.sidebar.selectbox('Año', opciones_anio, index=0)

    if seleccion_a == "Ninguno":
        selected_anio = None
        selected_mes = None
    else:
        selected_anio = int(seleccion_a)
        meses = sorted(df_calendario[df_calendario['año'] == selected_anio]['mes'].unique())
        opciones_mes = ["Ninguno"] + [str(mes) for mes in meses]
        seleccion_m = st.sidebar.selectbox('Mes', opciones_mes, index=0)
        selected_mes = int(seleccion_m) if seleccion_m != "Ninguno" else None
    
    #Filtro de qualification
    qualifications = sorted(df_casos['qualification'].dropna().unique().tolist())
    opciones_qualification = ["Ninguno"] + qualifications
    seleccion_q = st.sidebar.selectbox('Qualification', opciones_qualification, index=0)
    selected_qualification = seleccion_q if seleccion_q != "Ninguno" else None

    #Filtro de tendencia_uso
    tendencias = sorted(df_casos['tendencia_uso'].dropna().unique().tolist())
    opciones_tendencia = ["Ninguno"] + tendencias
    seleccion_t = st.sidebar.selectbox('Tendencia de Uso', opciones_tendencia, index=0)
    selected_tendencia = seleccion_t if seleccion_t != "Ninguno" else None

    filtros = {
        'año': selected_anio,
        'mes': selected_mes,
        'qualification': selected_qualification,
        'tendencia_uso': selected_tendencia
    }

    return page, filtros
