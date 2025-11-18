import streamlit as st 
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

def general_sidebar(df):
    st.sidebar.markdown('# Paginas')

    page = st.sidebar.radio(
        '', 
        ["General", "Finanzas", "Predicciones", "Machine Learning"],
        index=0
    )

    st.sidebar.markdown('# Filtros')

    #Filtro para los años 
    anios_casos = df_casos['año'].unique()
    anios_tx = df_tx['año'].unique()
    anios = sorted( set(anios_casos) | set(anios_tx) )
    selected_anios = st.sidebar.selectbox('Año', anios, )