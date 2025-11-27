import streamlit as st
from datetime import datetime
import pandas as pd

# Nota: Asumo que PROMOTIONS y convert_df_to_csv están definidos fuera de esta función
# o en algún lugar accesible. Los he incluido aquí por completitud.

# Definición de PROMOTIONS (Necesaria para que el resto del código funcione)
PROMOTIONS = {
    'alto': {
        'name': "Riesgo Alto",
        'perdida_dummy': 1200000,
        'msg_general': "**Mensaje sugerido (Riesgo Alto):**...",
        'promo_general': "**Promo para retención (Riesgo Alto):**...",
        'ocupacion': {
            'Hogar': "Oferta Hogar:...",
            'Educación': "Oferta Educación:...",
            'Empleado General': "Oferta Empleado General:...",
            'Negocio Propio / Empresario': "Oferta Negocio:...",
        }
    },
    'medio': {
        'name': "Riesgo Medio",
        'perdida_dummy': 450000,
        'msg_general': "**Mensaje sugerido (Riesgo Medio):**...",
        'promo_general': "**Promo para retención (Riesgo Medio):**...",
        'ocupacion': {
            'Hogar': "Oferta Hogar:...",
            'Educación': "Oferta Educación:...",
            'Empleado General': "Oferta Empleado General:...",
            'Negocio Propio / Empresario': "Oferta Negocio:...",
        }
    },
    'bajo': {
        'name': "Riesgo Estable",
        'perdida_dummy': 50000,
        'msg_general': "**Mensaje sugerido (Riesgo Estable):**...",
        'promo_general': "**Promo (Usuarios Estables):**...",
        'ocupacion': {
            'Hogar': "Oferta Hogar:...",
            'Educación': "Oferta Educación:...",
            'Empleado General': "Oferta Empleado General:...",
            'Negocio Propio / Empresario': "Oferta Negocio:...",
        }
    }
}

# Función auxiliar para convertir DataFrame a CSV (Necesaria para que el resto del código funcione)
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')


def render(df_risk):
    
    fecha_actualizacion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    total_users = len(df_risk)

    # Inicialización de SESSION STATE
    if 'selected_risk' not in st.session_state:
        st.session_state.selected_risk = None
    if 'show_promo_selection' not in st.session_state:
        st.session_state.show_promo_selection = False

    st.title("Predicciones de Riesgo")
    st.markdown("Selecciona un grupo de riesgo para ver algunos usuarios:")
# 1. ESTILOS CSS PARA LOS BOTONES DE RIESGO (COLORES SEMÁFORO FIJOS)
    # TÉCNICA EXTREMA: Sobreescribir el color del botón primario directamente.
    st.markdown("""
        <style>
        
        /* Contenedor del Botón (Clase base que Streamlit colorea) */
        
        /* Riesgo Alto: Rojo */
        button[data-testid="stBaseButton-primary"][key="btn_alto"] {
            background-color: #ff4b4b !important; 
            border-color: #ff4b4b !important; 
        }

        /* Riesgo Medio: Naranja */
        button[data-testid="stBaseButton-primary"][key="btn_medio"] {
            background-color: #ff9800 !important; /* NARANJA */
            border-color: #ff9800 !important;
        }

        /* Riesgo Estable: Verde */
        button[data-testid="stBaseButton-primary"][key="btn_bajo"] {
            background-color: #4CAF50 !important; /* VERDE */
            border-color: #4CAF50 !important;
        }
        
        /* ---------------------------------------------------- */
        /* FORZAR COLOR DE TEXTO DENTRO DEL CONTENEDOR MARKDOWN */
        /* ---------------------------------------------------- */
        
        /* Texto: Rojo -> Blanco */
        button[data-testid="stBaseButton-primary"][key="btn_alto"] p { 
            color: white !important; 
        }
        
        /* Texto: Naranja -> Negro */
        button[data-testid="stBaseButton-primary"][key="btn_medio"] p { 
            color: black !important; 
        }

        /* Texto: Verde -> Blanco */
        button[data-testid="stBaseButton-primary"][key="btn_bajo"] p { 
            color: white !important; 
        }

        /* ---------------------------------------------------- */
        /* FORZAR ESTADO HOVER para mantener el color */
        /* ---------------------------------------------------- */
        
        button[data-testid="stBaseButton-primary"][key="btn_alto"]:hover {
            background-color: #e63946 !important; 
            border-color: #e63946 !important;
        }
        button[data-testid="stBaseButton-primary"][key="btn_medio"]:hover {
            background-color: #fb8c00 !important; 
            border-color: #fb8c00 !important;
        }
        button[data-testid="stBaseButton-primary"][key="btn_bajo"]:hover {
            background-color: #388E3C !important; 
            border-color: #388E3C !important;
        }

        </style>
        """, unsafe_allow_html=True)
    # 🚨 SOLUCIÓN AL ERROR: Definir las columnas antes de usarlas
    col1, col2, col3 = st.columns(3)

    # Definir thresholds y filtrar grupos
    high_threshold = 0.66
    medium_low = 0.33
    riesgo_alto = df_risk[df_risk["prob_churn"] >= high_threshold].copy()
    riesgo_medio = df_risk[(df_risk["prob_churn"] < high_threshold) & (df_risk["prob_churn"] >= medium_low)].copy()
    riesgo_bajo = df_risk[df_risk["prob_churn"] < medium_low].copy()

    RISK_MAP = {
        'alto': (riesgo_alto, len(riesgo_alto)),
        'medio': (riesgo_medio, len(riesgo_medio)),
        'bajo': (riesgo_bajo, len(riesgo_bajo))
    }

    # ------------------------------------
    # BOTONES DE SELECCIÓN (Usando type="primary" para activar el CSS)
    # ------------------------------------
    with col1:
        if st.button("Riesgo Alto", use_container_width=True, key="btn_alto", type="primary"):
            st.session_state.selected_risk = 'alto'
            st.session_state.show_promo_selection = False 
            
    with col2:
        if st.button("Riesgo Medio", use_container_width=True, key="btn_medio", type="primary"):
            st.session_state.selected_risk = 'medio'
            st.session_state.show_promo_selection = False 

    with col3:
        if st.button("Riesgo Estable", use_container_width=True, key="btn_bajo", type="primary"):
            st.session_state.selected_risk = 'bajo'
            st.session_state.show_promo_selection = False 


    # ----------------------------------------------------
    # CONTENIDO CENTRAL FIJO (Tabla a la izquierda, Acciones a la derecha)
    # ----------------------------------------------------
    if st.session_state.selected_risk:
        risk_key = st.session_state.selected_risk
        df_selected, num_selected = RISK_MAP[risk_key]
        
        name_map = {'alto': 'Riesgo Alto', 'medio': 'Riesgo Medio', 'bajo': 'Riesgo Estable'}
        config = PROMOTIONS[risk_key]

        st.markdown("---")
        st.header(name_map[risk_key]) 
        
        # --- MÉTRICAS ---
        percent_selected = (num_selected / total_users) * 100
        
        col_met1, col_met2, _, _ = st.columns([1, 1, 1, 1])

        with col_met1:
            st.metric("Usuarios en Grupo", f"{percent_selected:.1f}%")
        with col_met2:
            st.metric("Pérdidas Potenciales (Dummy)", f"${config['perdida_dummy']:,.0f} MXN")

        st.markdown("---")

        # DISTRIBUCIÓN: Tabla (60%) y Acciones (40%) para evitar scroll
        col_tabla, col_acciones = st.columns([3, 2])

        # --- COLUMNA IZQUIERDA: TABLA Y DESCARGA ---
        with col_tabla:
            st.subheader("Top 10 Usuarios para Contacto")
            df_display = df_selected[["id_user", "prob_churn"]].sort_values("prob_churn", ascending=False).head(10)
            st.dataframe(df_display, use_container_width=True)

            # Botón de Descarga debajo de la tabla
            csv_data = convert_df_to_csv(df_selected)
            st.download_button(
                label=f"📥 Descargar CSV de {name_map[risk_key]}",
                data=csv_data,
                file_name=f"usuarios_{risk_key}.csv",
                mime='text/csv',
                key=f'download_{risk_key}',
                use_container_width=True
            )
            
        # --- COLUMNA DERECHA: ACCIONES SUGERIDAS ---
        with col_acciones:
            st.markdown("### Acciones Sugeridas")
            
            # 1. Mensaje General
            if st.button(f"Mensaje sugerido", key=f"msg_{risk_key}", use_container_width=True):
                st.info(config['msg_general'])

            # 2. Promo General
            if st.button(f"Promo sugerida", key=f"promo_gral_{risk_key}", use_container_width=True):
                st.success(config['promo_general'])

            st.markdown("---") 

            # 3. Promoción por Ocupación (Botón que despliega la lista)
            if st.button(f"Promo por Ocupación", key=f"promo_ocup_{risk_key}", use_container_width=True):
                st.session_state.show_promo_selection = not st.session_state.show_promo_selection
                
            # --- SELECCIÓN DE OCUPACIÓN ---
            if st.session_state.show_promo_selection:
                st.markdown("#### Selecciona Ocupación")
                
                occupation_options = list(config['ocupacion'].keys())
                
                selected_option = st.selectbox(
                    "Ocupación:", 
                    occupation_options,
                    index=0, 
                    key=f'selectbox_{risk_key}'
                )

                st.info(config['ocupacion'][selected_option])


    # -----------------------------------------------
    # FECHA DE ACTUALIZACIÓN - POSICIÓN INFERIOR DERECHA
    # -----------------------------------------------
    st.markdown("---") 
    
    _, col_fecha_bottom = st.columns([5, 1]) 
    with col_fecha_bottom:
        st.markdown(
            f'<p style="text-align: right; color:white; font-size: small;">Última Actualización: {fecha_actualizacion}</p>', 
            unsafe_allow_html=True
        )