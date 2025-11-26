import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN (Datos centralizados para mayor claridad) ---
# Usamos esta estructura para mantener todas las promos y datos de métricas juntos
PROMOTIONS = {
    'alto': {
        'name': "Riesgo Alto",
        'color': "🔥",
        'perdida_dummy': 1200000,
        'msg_general': """
                        **Mensaje sugerido (Riesgo Alto):**

                        Hola 👋  
                        Notamos que recientemente has tenido menos actividad en tu cuenta.  
                        Queremos asegurarnos de que estás aprovechando todos los beneficios.

                        Si tienes dudas o quieres explorar nuevas herramientas financieras,  
                        estamos aquí para apoyarte 💙

                        *Tu estabilidad financiera es nuestra prioridad.*
                        """,
        'promo_general': """
                        **Promo para retención (Riesgo Alto):**

                        🎉 *Oferta exclusiva* Recibe **$150 MXN de cashback** al realizar **3 pagos de servicios** en los próximos 7 días.

                        Queremos ayudarte a mantener el control de tus finanzas de forma fácil y segura 💰
                        """,
        'ocupacion': {
            'Hogar': "Oferta Hogar: 3 meses de seguro de hogar gratis al domiciliar 2 servicios.",
            'Educación': "Oferta Educación: Tasa preferencial del 5% en créditos educativos hasta $25,000 MXN.",
            'Empleado General': "Oferta Empleado General: 5% de cashback en todas las compras con tarjeta de débito los fines de semana (tope $200 MXN).",
            'Negocio Propio / Empresario': "Oferta Negocio: 0% de comisión en las primeras 5 transferencias SPEI al mes.",
        }
    },
    'medio': {
        'name': "Riesgo Medio",
        'color': "🟡",
        'perdida_dummy': 450000,
        'msg_general': """
                        **Mensaje sugerido (Riesgo Medio):**

                        Hola 👋  
                        Hemos visto que tu actividad ha bajado un poco.  
                        Queremos recordarte que puedes seguir administrando tus finanzas con herramientas fáciles de usar.
                        """,
        'promo_general': """
                        **Promo para retención (Riesgo Medio):**

                        Aprovecha un **bono del 1%** por cada transferencia SPEI  
                        realizada esta semana, acumulable hasta **$50 MXN**.

                        ¡Gracias por seguir con nosotros! 🙌
                        """,
        'ocupacion': {
            'Hogar': "Oferta Hogar: 2 meses de seguro de hogar gratis al domiciliar 1 servicio.",
            'Educación': "Oferta Educación: Tasa preferencial del 7% en créditos educativos hasta $15,000 MXN.",
            'Empleado General': "Oferta Empleado General: 3% de cashback en todas las compras con tarjeta de débito los fines de semana (tope $100 MXN).",
            'Negocio Propio / Empresario': "Oferta Negocio: 0% de comisión en las primeras 3 transferencias SPEI al mes.",
        }
    },
    'bajo': {
        'name': "Riesgo Estable",
        'color': "🔵",
        'perdida_dummy': 50000,
        'msg_general': """
                        **Mensaje sugerido (Riesgo Estable):**

                        ¡Gracias por seguir usando nuestra plataforma! 💙  
                        Queremos que sigas aprovechando todas las herramientas que tenemos para ti.
                        """,
        'promo_general': """
                        **Promo (Usuarios Estables):**

                        🎁 Obtén **$20 MXN de cashback** al completar un pago recurrente nuevo  
                        durante esta semana.

                        ¡Gracias por ser un usuario activo de nuestra fintech! 🚀
                        """,
        'ocupacion': {
            'Hogar': "Oferta Hogar: Participa en el sorteo de un mes de seguro de hogar al domiciliar un nuevo servicio.",
            'Educación': "Oferta Educación: Bono de $100 MXN al invertir $1,000 MXN o más en fondo educativo.",
            'Empleado General': "Oferta Empleado General: Gana el doble de puntos de lealtad en todas las compras durante el fin de semana.",
            'Negocio Propio / Empresario': "Oferta Negocio: Promoción en terminal punto de venta: 3 meses sin renta.",
        }
    }
}

# Función auxiliar para convertir DataFrame a CSV
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# ----------------------------------------------------------------------
# FUNCIÓN RENDER
# ----------------------------------------------------------------------
def render(df_risk):
    
    # 1. FECHA ACTUAL (Revertido a la hora del sistema)
    fecha_actualizacion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    total_users = len(df_risk)

    # 2. INICIALIZACIÓN DE SESSION STATE
    # Usamos el estado de sesión para controlar qué se muestra en la sección central
    if 'selected_risk' not in st.session_state:
        st.session_state.selected_risk = None
    if 'show_promo_selection' not in st.session_state:
        st.session_state.show_promo_selection = False

    st.title("Predicciones de Riesgo")
    st.markdown("Selecciona un grupo de riesgo para ver algunos usuarios:")

    col1, col2, col3 = st.columns(3)

    # Definir thresholds y filtrar grupos
    high_threshold = 0.66
    medium_low = 0.33
    riesgo_alto = df_risk[df_risk["prob_churn"] >= high_threshold].copy()
    riesgo_medio = df_risk[(df_risk["prob_churn"] < high_threshold) & (df_risk["prob_churn"] >= medium_low)].copy()
    riesgo_bajo = df_risk[df_risk["prob_churn"] < medium_low].copy()

    # Mapeo de riesgo a DataFrame y datos
    RISK_MAP = {
        'alto': (riesgo_alto, len(riesgo_alto)),
        'medio': (riesgo_medio, len(riesgo_medio)),
        'bajo': (riesgo_bajo, len(riesgo_bajo))
    }

    # ------------------------------------
    # BOTONES DE SELECCIÓN (Actualizan el estado)
    # ------------------------------------
    with col1:
        if st.button("🔥 Riesgo Alto", use_container_width=True, key="btn_alto"):
            st.session_state.selected_risk = 'alto'
            st.session_state.show_promo_selection = False # Resetear estado de promo
            
    with col2:
        if st.button("🟡 Riesgo Medio", use_container_width=True, key="btn_medio"):
            st.session_state.selected_risk = 'medio'
            st.session_state.show_promo_selection = False # Resetear estado de promo

    with col3:
        if st.button("🔵 Riesgo Estable", use_container_width=True, key="btn_bajo"):
            st.session_state.selected_risk = 'bajo'
            st.session_state.show_promo_selection = False # Resetear estado de promo


    # ----------------------------------------------------
    # CONTENIDO CENTRAL FIJO (Aparece bajo los botones)
    # ----------------------------------------------------
    if st.session_state.selected_risk:
        risk_key = st.session_state.selected_risk
        df_selected, num_selected = RISK_MAP[risk_key]
        config = PROMOTIONS[risk_key]

        st.markdown("---")
        st.header(f"{config['color']} {config['name']}")
        
        # --- MÉTRICAS (Porcentaje y Pérdidas) ---
        percent_selected = (num_selected / total_users) * 100
        
        # Creamos columnas para las métricas
        col_met1, col_met2, _, _ = st.columns([1, 1, 1, 1]) 

        with col_met1:
            st.metric("Usuarios en Grupo", f"{percent_selected:.1f}%")
        with col_met2:
            # Formato de dinero en español
            st.metric("Pérdidas Potenciales (Dummy)", f"${config['perdida_dummy']:,.0f} MXN")

        st.markdown("---")

        # --- TABLA DE USUARIOS (Fija en el centro) ---
        st.subheader("Top 10 Usuarios para Contacto")
        df_display = df_selected[["id_user", "prob_churn"]].sort_values("prob_churn", ascending=False).head(10)
        st.dataframe(df_display, use_container_width=True)

        # Botón de Descarga
        csv_data = convert_df_to_csv(df_selected)
        st.download_button(
            label=f"📥 Descargar CSV de {config['name']}",
            data=csv_data,
            file_name=f"usuarios_{risk_key}.csv",
            mime='text/csv',
            key=f'download_{risk_key}'
        )
        
        st.markdown("---")

        # --- BOTONES DE ACCIÓN ---
        st.markdown("### Acciones Sugeridas")

        col_msg, col_promo_gral, col_promo_ocup = st.columns(3)

        # 1. Mensaje General
        with col_msg:
            if st.button(f"✉️ Mensaje sugerido", key=f"msg_{risk_key}", use_container_width=True):
                st.info(config['msg_general'])

        # 2. Promo General
        with col_promo_gral:
            if st.button(f"🎁 Promo sugerida", key=f"promo_gral_{risk_key}", use_container_width=True):
                st.success(config['promo_general'])

        # 3. Promoción por Ocupación (Botón que despliega la lista)
        with col_promo_ocup:
            if st.button(f"💼 Promo por Ocupación", key=f"promo_ocup_{risk_key}", use_container_width=True):
                # Cambia el estado para mostrar u ocultar la lista de selección
                st.session_state.show_promo_selection = not st.session_state.show_promo_selection
                
        # --- SELECCIÓN DE OCUPACIÓN (Desplegable si el botón fue presionado) ---
        if st.session_state.show_promo_selection:
            st.markdown("#### Selecciona una Ocupación")
            
            occupation_options = list(config['ocupacion'].keys())
            
            # El selectbox
            selected_option = st.selectbox(
                "Ocupación:", 
                occupation_options,
                index=0, # Selecciona el primer elemento por defecto
                key=f'selectbox_{risk_key}'
            )

            # Mostrar la promoción
            st.info(config['ocupacion'][selected_option])


    # -----------------------------------------------
    # FECHA DE ACTUALIZACIÓN - POSICIÓN INFERIOR DERECHA (Final, Color Blanco)
    # -----------------------------------------------
    st.markdown("---") # Separador visual al final de la app
    
    # Usamos dos columnas [Espacio, Contenido] para alinear a la derecha
    _, col_fecha_bottom = st.columns([5, 1]) 
    with col_fecha_bottom:
        # Usamos HTML para forzar la alineación a la derecha y el color blanco.
        st.markdown(
            f'<p style="text-align: right; color:white; font-size: small;">Última Actualización: {fecha_actualizacion}</p>', 
            unsafe_allow_html=True
        )