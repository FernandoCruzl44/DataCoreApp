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

    page = st.sidebar.radio(
        '', 
        ["General", "Finanzas", "Predicciones", "Machine Learning"],
        index=0
    )

    st.sidebar.markdown('# Filtros')

    #Tabla intermedia para filtros
    df_calendario = (pd.concat([df_casos[['año', 'mes']], df_tx[['año', 'mes']]]).drop_duplicates().sort_values(['año', 'mes']))

    #Filtro Año
    anios = df_calendario['año'].unique()
    selected_anio = st.sidebar.selectbox('Año', anios)

    #Filtro de Mes solo para ese año en especifico

    meses = df_calendario[df_calendario['año'] == selected_anio]['mes'].unique()
    meses = sorted(meses)
    selected_mes = st.sidebar.selectbox('Mes', meses)

    filtros = {
        'año': selected_anio,
        'mes': selected_mes
    }

    return page, filtros
