import pandas as pd
from components.layout2 import base_layout, general_sidebar
from views import general2, ml, finanzas, predicciones
import streamlit as st
import time


@st.cache_data
def load_data():
    print("\n====== [LOAD_DATA TURBO] INICIO ======")
    t0 = time.perf_counter()

    # Parquets optimizados (ya con año, mes, churn, etc.)
    df_casos = pd.read_parquet("data/casos_full_opt.parquet")
    df_master = pd.read_parquet("data/master_opt.parquet")

    # Transacciones agregadas + vistas pre-calculadas
    df_tx = pd.read_parquet("data/tx_agregado.parquet")
    df_semana = pd.read_parquet("data/tx_semana.parquet")
    df_mes = pd.read_parquet("data/tx_mes.parquet")
    df_tx_raw = pd.read_parquet("data/tx_raw_opt.parquet")

    # CSV chico
    df_risk = pd.read_csv("data/churn_risk_scores.csv")

    print(f"[LOAD_DATA TURBO] Todo cargado en {time.perf_counter() - t0:.2f} s")
    print("====== [LOAD_DATA TURBO] FIN ======\n")

    return df_casos, df_tx, df_tx_raw, df_risk, df_master, df_semana, df_mes


def aplicar_filtros(df_casos, df_tx, filtros):
    print("\n--- [FILTROS TURBO] Aplicando filtros ---")
    t0 = time.perf_counter()

    año = filtros.get("año")
    mes = filtros.get("mes")
    qualif = filtros.get("qualification")
    tendencia = filtros.get("tendencia_uso")

    df_c = df_casos.copy()
    df_t = df_tx.copy()

    # Año
    if año is not None:
        df_c = df_c[df_c["año"] == año]
        df_t = df_t[df_t["año"] == año]

    # Mes
    if mes is not None:
        df_c = df_c[df_c["mes"] == mes]
        df_t = df_t[df_t["mes"] == mes]

    # Qualification
    if qualif is not None:
        df_c = df_c[df_c["qualification"] == qualif]
        ids = df_c["id_user"].unique()
        df_t = df_t[df_t["id_user"].isin(ids)]

    # Tendencia de uso
    if tendencia is not None:
        df_c = df_c[df_c["tendencia_uso"] == tendencia]
        ids = df_c["id_user"].unique()
        df_t = df_t[df_t["id_user"].isin(ids)]

    print(f"[FILTROS TURBO] Aplicación completa en {time.perf_counter() - t0:.4f} s")
    return df_c, df_t


def main():
    base_layout()

    t0 = time.perf_counter()
    df_casos, df_tx, df_tx_raw, df_risk, df_master, df_semana, df_mes = load_data()
    print(f"[MAIN TURBO] Data cargada total en {time.perf_counter() - t0:.2f} s")

    t_sb0 = time.perf_counter()
    page, filtros = general_sidebar(df_casos, df_tx)
    print(f"[MAIN TURBO] Sidebar generado en {time.perf_counter() - t_sb0:.2f} s")

    if page == "Machine Learning":
        ml.render()
        return

    # Aplicar filtros solo una vez
    t_f0 = time.perf_counter()
    df_casos_f, df_tx_f = aplicar_filtros(df_casos, df_tx, filtros)
    print(f"[MAIN TURBO] Filtros aplicados en {time.perf_counter() - t_f0:.2f} s")

    if page == "General":
        general2.render(df_casos_f, df_tx_f, filtros, df_semana, df_mes)

    elif page == "Predicciones":
        # Pasamos df_risk al argumento 'df_default'. 
        # Esto permite que la función sepa que son datos de respaldo y no datos nuevos.
        predicciones.render(df_default=df_risk)

    elif page == "Finanzas":
        df_casos_f, df_tx_f = aplicar_filtros(df_casos, df_tx, filtros)
        finanzas.render(df_casos_f, df_tx_f, df_master)


if __name__ == "__main__":
    main()
