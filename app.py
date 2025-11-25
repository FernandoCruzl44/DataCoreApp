import pandas as pd 
from components.layout2 import base_layout, general_sidebar
from views import general2, ml, finanzas, predicciones
import streamlit as st
import time


@st.cache_data
def load_data():

    t0 = time.perf_counter()

    #df_master = pd.read_csv('data/dataset_master.csv')
    df_casos = pd.read_csv('data/CasosContactCenter_limpio.csv', low_memory=True)
    df_tx = pd.read_parquet('data/transacciones_part1.parquet')
    df_master = pd.read_csv('data/df_master_corregido.csv', low_memory=True)
    df_risk = pd.read_csv('data/churn_risk_scores.csv')
    t1 = time.perf_counter()
    print(f"Carga de datos en {t1 - t0:.2f} segundos")

    t2 = time.perf_counter()
    df_casos['fecha'] = pd.to_datetime(df_casos['fecha'], errors='coerce')   
    df_casos['año'] = df_casos['fecha'].dt.year
    df_casos['mes'] = df_casos['fecha'].dt.month

    df_tx['fechaf'] = pd.to_datetime(df_tx['fechaf'], errors='coerce')
    df_tx['año'] = df_tx['fechaf'].dt.year
    df_tx['mes'] = df_tx['fechaf'].dt.month
    t3 = time.perf_counter()
    print(f"Procesamiento de fechas en {t3 - t2:.2f} segundos")

    t4 = time.perf_counter()
    df_casos = df_casos.merge(df_master[['id_user', 'churn', 'occupation_category', 'qualification', 'tendencia_uso', 'state']], on='id_user', how='left')
    t5 = time.perf_counter()
    print(f"Merging datos en {t5 - t4:.2f} segundos")

    print(f"Tiempo total de load_data: {t5 - t0:.2f} segundos")
    return df_casos, df_tx, df_risk,df_master


def aplicar_filtros(df_casos, df_tx, filtros):
    
    t0 = time.perf_counter()

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
    
    t1 = time.perf_counter()
    print(f"Tiempo aplicar_filtros: {t1 - t0:.2f} segundos")

    return df_c, df_t

def main():
    base_layout()

    df_casos, df_tx, df_risk, df_master = load_data()

    page, filtros = general_sidebar(df_casos, df_tx)

    if page == "Machine Learning":
        ml.render()
        return 

    # Aplicar filtros
    df_casos_f, df_tx_f = aplicar_filtros(df_casos, df_tx, filtros)

    if page == "General":
        general2.render(df_casos_f, df_tx_f)
    
    elif page == "Predicciones":
        predicciones.render(df_risk)

    elif page == "Finanzas":
        finanzas.render(df_casos_f, df_tx_f, df_master)

if __name__ == "__main__":
    main()