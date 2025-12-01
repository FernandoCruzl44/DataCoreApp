import streamlit as st
import pandas as pd
import pickle
import numpy as np
from datetime import datetime


# 1. CONFIGURACIÓN Y DATOS ESTÁTICOS


PROMOTIONS = {
    'alto': {
        'name': "Riesgo Alto",
        'perdida_dummy': 1200000,
        'msg_general': "**Mensaje sugerido (Riesgo Alto):** Hola 👋 Notamos menos actividad reciente. Queremos asegurarnos de que aprovechas todos los beneficios. 💙",
        'promo_general': "**Promo (Riesgo Alto):** 🎉 Recibe **$150 MXN de cashback** al realizar 3 pagos de servicios esta semana.",
        'ocupacion': {
            'Hogar': "Oferta Hogar: 3 meses de seguro gratis al domiciliar 2 servicios.",
            'Educación': "Oferta Educación: Tasa 5% en créditos educativos.",
            'Empleado General': "Oferta Empleado: 5% cashback fines de semana.",
            'Negocio Propio / Empresario': "Oferta Negocio: 0% comisión en transferencias.",
        }
    },
    'medio': {
        'name': "Riesgo Medio",
        'perdida_dummy': 450000,
        'msg_general': "**Mensaje sugerido (Riesgo Medio):** Hola 👋 Tu actividad ha bajado un poco. Recuerda nuestras herramientas financieras.",
        'promo_general': "**Promo (Riesgo Medio):** Bono del 1% por cada transferencia SPEI (max $50).",
        'ocupacion': {
            'Hogar': "Oferta Hogar: 2 meses seguro gratis.",
            'Educación': "Oferta Educación: Tasa preferencial 7%.",
            'Empleado General': "Oferta Empleado: 3% cashback.",
            'Negocio Propio / Empresario': "Oferta Negocio: 0% comisión en 3 transferencias.",
        }
    },
    'bajo': {
        'name': "Riesgo Estable",
        'perdida_dummy': 50000,
        'msg_general': "**Mensaje sugerido (Riesgo Estable):** ¡Gracias por seguir con nosotros! 💙",
        'promo_general': "**Promo (Riesgo Estable):** 🎁 $20 MXN cashback al domiciliar un pago nuevo.",
        'ocupacion': {
            'Hogar': "Oferta Hogar: Sorteo de un mes de seguro.",
            'Educación': "Oferta Educación: Bono $100 al invertir.",
            'Empleado General': "Oferta Empleado: Doble puntos de lealtad.",
            'Negocio Propio / Empresario': "Oferta Negocio: Terminal sin renta 3 meses.",
        }
    }
}

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')


# 2. LÓGICA DE MACHINE LEARNING (Carga y Predicción)


@st.cache_resource
def load_model(path='models/final_xgb_model.pkl'):
    """Carga el modelo pickle."""
    try:
        with open(path, 'rb') as file:
            model = pickle.load(file)
        return model
    except FileNotFoundError:
        return None

def predict_churn_from_csv(df_input, model):
    """
    Aplica el preprocesamiento exacto (One-Hot) y predice.
    """
    # 1. Variables definidas por ti
    num_vars_importantes = ['total_trx', 'calls_per_month', 'avg_amount', 'age']
    cat_vars_importantes = ['tendencia_uso', 'tipificacion_mas_comun', 'qualification', 'category_total_amount']
    
    # 2. Verificar columnas necesarias
    subset_vars = num_vars_importantes + cat_vars_importantes
    missing_cols = [col for col in subset_vars if col not in df_input.columns]
    
    if missing_cols:
        st.error(f"❌ El archivo CSV no tiene estas columnas requeridas: {missing_cols}")
        return None

    # 3. Preparar subset
    df_subset = df_input[subset_vars].copy()
    
    # Separar para procesar
    X_num = df_subset[num_vars_importantes]
    X_cat = df_subset[cat_vars_importantes]
    
    # 4. One-Hot Encoding (pd.get_dummies)
    X_encoded = pd.get_dummies(X_cat, columns=cat_vars_importantes, drop_first=True)
    
    # Unir numéricas y codificadas
    X_final = pd.concat([X_num, X_encoded], axis=1)

    # 5. ALINEACIÓN DE COLUMNAS (Crucial para que el modelo no falle)
    # Obtenemos las columnas que el modelo espera
    if hasattr(model, 'feature_names_in_'):
        model_cols = model.feature_names_in_
    else:
        # Si el modelo es muy viejo y no guarda nombres, usamos las actuales (riesgoso pero necesario fallback)
        model_cols = X_final.columns

    # Reindexamos: Esto agrega columnas faltantes con 0 y quita las que sobran
    X_final = X_final.reindex(columns=model_cols, fill_value=0)

    # 6. Predecir
    try:
        # Probabilidad de clase 1 (Churn)
        probs = model.predict_proba(X_final)[:, 1]
        
        # Preparamos el DF de salida
        df_result = df_input.copy()
        df_result['prob_churn'] = probs
        return df_result
    except Exception as e:
        st.error(f"Error al predecir: {e}")
        return None


# 3. FUNCIÓN RENDER PRINCIPAL


def render(df_default=None):
    
    fecha_actualizacion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Inicialización de SESSION STATE
    if 'selected_risk' not in st.session_state:
        st.session_state.selected_risk = None
    if 'show_promo_selection' not in st.session_state:
        st.session_state.show_promo_selection = False

    st.title("Predicciones de Riesgo (IA)")
    
    
    # CSS: COLORES DE SEMÁFORO (Tus estilos personalizados)
    
    st.markdown("""
        <style>
        /* Riesgo Alto: Rojo */
        button[data-testid="stBaseButton-primary"][key="btn_alto"] {
            background-color: #ff4b4b !important; border-color: #ff4b4b !important; color: white !important;
        }
        button[data-testid="stBaseButton-primary"][key="btn_alto"]:hover {
            background-color: #e63946 !important; border-color: #e63946 !important; color: white !important;
        }

        /* Riesgo Medio: Naranja */
        button[data-testid="stBaseButton-primary"][key="btn_medio"] {
            background-color: #ff9800 !important; border-color: #ff9800 !important; color: black !important;
        }
        button[data-testid="stBaseButton-primary"][key="btn_medio"]:hover {
            background-color: #fb8c00 !important; border-color: #fb8c00 !important; color: black !important;
        }

        /* Riesgo Estable: Verde */
        button[data-testid="stBaseButton-primary"][key="btn_bajo"] {
            background-color: #4CAF50 !important; border-color: #4CAF50 !important; color: white !important;
        }
        button[data-testid="stBaseButton-primary"][key="btn_bajo"]:hover {
            background-color: #388E3C !important; border-color: #388E3C !important; color: white !important;
        }
        
        /* Texto interno */
        button[data-testid="stBaseButton-primary"][key="btn_alto"] p { color: white !important; }
        button[data-testid="stBaseButton-primary"][key="btn_medio"] p { color: black !important; }
        button[data-testid="stBaseButton-primary"][key="btn_bajo"] p { color: white !important; }
        </style>
        """, unsafe_allow_html=True)

    
    # BOTONES DE GRUPO
    
    st.markdown("Selecciona un grupo de riesgo:")
    col1, col2, col3 = st.columns(3)

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


    # CARGA DE DATOS Y PREDICCIÓN
    
    st.markdown("---")
    st.caption("Cargar nuevos datos para predecir:")
    uploaded_file = st.file_uploader("Sube un CSV (con columnas requeridas)", type=['csv'])

    # Lógica de Selección de Datos (Default vs Uploaded)
    df_risk_to_use = None
    
    # Intenta cargar el modelo
    model = load_model() 

    if uploaded_file is not None:
        if model is None:
            st.error("⚠️ No se encontró el modelo 'models/modelo_churn.pkl'.")
        else:
            with st.spinner('Procesando datos y prediciendo...'):
                df_input = pd.read_csv(uploaded_file)
                df_risk_to_use = predict_churn_from_csv(df_input, model)
                if df_risk_to_use is not None:
                    st.success(f"✅ Predicción exitosa para {len(df_risk_to_use)} usuarios.")
    
    elif df_default is not None:
        # Usamos los datos precargados si no suben nada
        df_risk_to_use = df_default
    
    # Si no hay datos validos, terminamos aquí
    if df_risk_to_use is None:
        return

    # VISUALIZACIÓN DE RESULTADOS
    
    # Filtrar por grupos usando la columna 'prob_churn'
    high_threshold = 0.66
    medium_low = 0.33
    
    riesgo_alto = df_risk_to_use[df_risk_to_use["prob_churn"] >= high_threshold].copy()
    riesgo_medio = df_risk_to_use[(df_risk_to_use["prob_churn"] < high_threshold) & (df_risk_to_use["prob_churn"] >= medium_low)].copy()
    riesgo_bajo = df_risk_to_use[df_risk_to_use["prob_churn"] < medium_low].copy()

    RISK_MAP = {
        'alto': (riesgo_alto, len(riesgo_alto)),
        'medio': (riesgo_medio, len(riesgo_medio)),
        'bajo': (riesgo_bajo, len(riesgo_bajo))
    }

    if st.session_state.selected_risk:
        risk_key = st.session_state.selected_risk
        df_selected, num_selected = RISK_MAP[risk_key]
        config = PROMOTIONS[risk_key]
        total_users = len(df_risk_to_use)

        st.markdown("---")
        st.header(config['name']) 
        
        # Métricas
        percent_selected = (num_selected / total_users * 100) if total_users > 0 else 0
        col_met1, col_met2, _, _ = st.columns([1, 1, 1, 1])
        with col_met1:
            st.metric("Usuarios en Grupo", f"{percent_selected:.1f}%")
        with col_met2:
            st.metric("Pérdidas Potenciales", f"${config['perdida_dummy']:,.0f} MXN")

        st.markdown("---")

        col_tabla, col_acciones = st.columns([3, 2])

        # COLUMNA IZQUIERDA: TABLA
        with col_tabla:
            st.subheader("Detalle de Usuarios")
            
            # Columnas a mostrar (Si existen en el DF)
            cols_posibles = ["id_user", "avg_amount", "calls_per_month", "prob_churn"]
            cols_validas = [c for c in cols_posibles if c in df_selected.columns]
            
            df_display = df_selected[cols_validas].sort_values("prob_churn", ascending=False).head(10)
            
            # Renombrar para visualización
            df_viz = df_display.rename(columns={
                "id_user": "User ID",
                "avg_amount": "Avg Amount",
                "calls_per_month": "Calls/Month",
                "prob_churn": "Predicción"
            })
            
            st.dataframe(
                df_viz, 
                use_container_width=True,
                column_config={
                    "Predicción": st.column_config.NumberColumn("Predicción Churn", format="%.1f%%"),
                    "Avg Amount": st.column_config.NumberColumn("Monto Promedio", format="$%.2f")
                }
            )

            # Botón descarga
            st.download_button(
                label=f"📥 Descargar CSV ({config['name']})",
                data=convert_df_to_csv(df_selected),
                file_name=f"usuarios_{risk_key}.csv",
                mime='text/csv',
                key=f'dl_{risk_key}',
                use_container_width=True
            )

        # COLUMNA DERECHA: ACCIONES
        with col_acciones:
            st.markdown("### Acciones Sugeridas")
            
            if st.button("Mensaje sugerido", key=f"msg_{risk_key}", use_container_width=True):
                st.info(config['msg_general'])

            if st.button("Promo sugerida", key=f"promo_{risk_key}", use_container_width=True):
                st.success(config['promo_general'])
            
            st.markdown("---")

            if st.button("Promo por Ocupación", key=f"ocup_{risk_key}", use_container_width=True):
                st.session_state.show_promo_selection = not st.session_state.show_promo_selection
            
            if st.session_state.show_promo_selection:
                opciones = list(config['ocupacion'].keys())
                seleccion = st.selectbox("Ocupación:", opciones, key=f'sb_{risk_key}')
                st.info(config['ocupacion'][seleccion])

    st.markdown("---")
    st.caption(f"Última Actualización: {fecha_actualizacion}", unsafe_allow_html=False)