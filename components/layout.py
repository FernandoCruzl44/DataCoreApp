import streamlit as st 
import pandas as pd
import numpy as np

def base_layout():
    st.set_page_config( page_title="DataCore App", layout="wide" )

    st.markdown( 
        """
        <style>
        .main { background-color:#020824; }
        .sidebar .sidebar-content { background-color:#020824; }
        .card { padding:15px 20px; border-radius:10px;
                background-color:#07112f; border:1px solid #1f2b4d; }
        .big-title { font-size:26px; font-weight:700; color:white; }
        .kpi-number { font-size:28px; font-weight:700; color:white; }
        .kpi-label { font-size:12px; color:#9da9d8; }
        </style>""", unsafe_allow_html=True
    )

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
    