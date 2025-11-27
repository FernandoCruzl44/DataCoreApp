
import streamlit as st
import pandas as pd
# =====================================================
# ===============  ESTILOS Y THEME  ===================
# =====================================================
def load_styles():
    st.markdown("""
        <style>
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #06141f !important;
        }
        [data-testid="stSidebar"] {
            background-color: #0e2a3f !important;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        button[kind="secondary"] {
            background-color: #0e2a3f !important;
            color: white !important;
            border: 1px solid #1f506f !important;
        }
        button[kind="secondary"]:hover {
            background-color: #13405d !important;
        }
        h1, h2, h3, h4, h5, h6, label, p {
            color: white !important;
        }
        .kpi-card {
            background-color: #0d2536;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #1b3b52;
            width: 100%;
        }
        .kpi-title {
            font-size: 14px;
            color: #9fc5dc;
            font-weight: 600;
            margin-bottom: 5px;
        }
        .kpi-value {
            font-size: 28px;
            font-weight: bold;
            color: white;
        }
        .kpi-meta {
            font-size: 11px;
            color: #b3cfe3cc;
            margin-top: 4px;
        }
        .divider {
            width: 100%;
            height: 1px;
            background-color: #1f3a4a;
            margin: 25px 0;
        }
        [data-testid="stMarkdown"] {
            color: white !important;
        }
        [data-testid="stForm"] {
            background-color: #06141f !important;
        }
        </style>
    """, unsafe_allow_html=True)

# =====================================================
# ===============  KPI COMPONENT  =====================
# =====================================================
def kpi_card(title, value, meta_text=None):
    meta_html = f"<div class='kpi-meta'>{meta_text}</div>" if meta_text else ""
    st.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-title'>{title}</div>
            <div class='kpi-value'>{value}</div>
            {meta_html}
        </div>
        """,
        unsafe_allow_html=True
    )

def divider():
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# =====================================================
# ===============  BASE LAYOUT  =======================
# =====================================================
def base_layout():
    """Carga estilos globales y configuración."""
    st.set_page_config(page_title="DataCore App", layout="wide")
    load_styles()

# =====================================================
# ===============  SIDEBAR GENERAL  ====================
# =====================================================
def general_sidebar(df_casos, df_tx):
    st.sidebar.markdown("## Navegación")
    paginas = ["General", "Finanzas", "Predicciones", "Machine Learning"]
    if "page" not in st.session_state:
        st.session_state.page = "General"
    for pagina in paginas:
        if st.sidebar.button(pagina):
            st.session_state.page = pagina
    page = st.session_state.page
    # Sidebar ML
    if page == "Machine Learning":
        st.sidebar.markdown("## Hiperparámetros")
        n_estimators = st.sidebar.text_input("N_estimators", "446")
        learning_rate = st.sidebar.text_input("Learning rate", "0.3")
        max_depth = st.sidebar.text_input("Max Depth", "3")
        threshold = st.sidebar.text_input("Threshold", "0.25")
        return page, None
    # Sidebar General filters
    st.sidebar.markdown("## Filtros")
    df_calendario = (
        pd.concat([df_casos[['año','mes']], df_tx[['año','mes']]])
        .drop_duplicates()
        .sort_values(['año','mes'])
    )
    # Año
    anios = sorted(df_calendario['año'].unique())
    seleccion_anio = st.sidebar.selectbox("Año", ["Ninguno"] + [str(a) for a in anios])
    if seleccion_anio == "Ninguno":
        selected_anio = None
        selected_mes = None
    else:
        selected_anio = int(seleccion_anio)
        meses = sorted(df_calendario[df_calendario['año']==selected_anio]['mes'].unique())
        seleccion_mes = st.sidebar.selectbox("Mes", ["Ninguno"] + [str(m) for m in meses])
        selected_mes = int(seleccion_mes) if seleccion_mes != "Ninguno" else None
    # Qualification
    qualifications = sorted(df_casos['qualification'].dropna().unique().tolist())
    seleccion_q = st.sidebar.selectbox("Qualification", ["Ninguno"] + qualifications)
    selected_q = seleccion_q if seleccion_q != "Ninguno" else None
    # Tendencia de uso
    tendencias = sorted(df_casos['tendencia_uso'].dropna().unique().tolist())
    seleccion_t = st.sidebar.selectbox("Tendencia de Uso", ["Ninguno"] + tendencias)
    selected_tendencia = seleccion_t if seleccion_t != "Ninguno" else None
    filtros = {
        "año": selected_anio,
        "mes": selected_mes,
        "qualification": selected_q,
        "tendencia_uso": selected_tendencia
    }
    return page, filtros

