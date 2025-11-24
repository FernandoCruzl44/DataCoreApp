import pandas as pd 
from components.layout2 import base_layout, general_sidebar
from views import general2
import streamlit as st

@st.cache_data
def load_data():

    #df_master = pd.read_csv('data/dataset_master.csv')
    df_casos = pd.read_csv('data/CasosContactCenter_limpio.csv', low_memory=True)
    df_tx = pd.read_csv('data/transacciones_cleaned.csv', low_memory=True)
    df_master = pd.read_csv('data/df_master_corregido.csv', low_memory=True)

    df_casos['fecha'] = pd.to_datetime(df_casos['fecha'], errors='coerce')   
    df_casos['año'] = df_casos['fecha'].dt.year
    df_casos['mes'] = df_casos['fecha'].dt.month

    df_tx['fechaf'] = pd.to_datetime(df_tx['fechaf'], errors='coerce')
    df_tx['año'] = df_tx['fechaf'].dt.year
    df_tx['mes'] = df_tx['fechaf'].dt.month

    df_casos = df_casos.merge(df_master[['id_user', 'churn', 'occupation_category', 'qualification', 'tendencia_uso', 'state']], on='id_user', how='left')

    return df_casos, df_tx


def aplicar_filtros(df_casos, df_tx, filtros):
    #Aplicación de filtros año y mes a cada tabla
    df_c = df_casos.copy()
    df_t = df_tx.copy()

    año = filtros["año"]
    mes = filtros["mes"]
    qualif = filtros["qualification"]
    tendencia = filtros["tendencia_uso"]

    # Filtro por año
    if año is not None:
        df_c = df_c[df_c["año"] == año]
        df_t = df_t[df_t["año"] == año]

    # Filtro por mes
    if mes is not None:
        df_c = df_c[df_c["mes"] == mes]
        df_t = df_t[df_t["mes"] == mes]
    
    # Filtro por qualification
    if qualif is not None:
        df_c = df_c[df_c["qualification"] == qualif]
        df_t = df_t[df_t['id_user'].isin(df_c['id_user'].unique())]
    
    # Filtro por tendencia_uso
    if tendencia is not None:
        df_c = df_c[df_c["tendencia_uso"] == tendencia]
        df_t = df_t[df_t['id_user'].isin(df_c['id_user'].unique())]

    return df_c, df_t

def main():
    base_layout()

    df_casos, df_tx = load_data()

    page, filtros = general_sidebar(df_casos, df_tx)

    # Aplicar filtros
    df_casos_f, df_tx_f = aplicar_filtros(df_casos, df_tx, filtros)

    if page == "General":
        general2.render(df_casos_f, df_tx_f)

if __name__ == "__main__":
    main()