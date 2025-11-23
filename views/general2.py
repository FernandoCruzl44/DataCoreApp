import streamlit as st
import matplotlib.pyplot as plt


def render(df_casos, df_tx, df_master):
    # Título
    st.markdown('<div class="big-title">Vista General</div>', unsafe_allow_html=True)

    # KPIs
    col1, col2, col3, col4 = st.columns(4)

    total_tx = len(df_tx)
    total_casos = len(df_casos)


    with col1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Total transacciones</div>
                <div class="kpi-value">{total_tx:,}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Total casos contact center</div>
                <div class="kpi-value">{total_casos:,}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Churn %</div>
                <div class="kpi-value">33%</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Ingresos</div>
                <div class="kpi-value">$100,000</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")  # separador

    # Ejemplos de graficas random

    col_g1, col_g2 = st.columns(2)
    col_g4, col_g5 = st.columns(2)

    # Ejemplo conteo de transacciones por dia 
    with col_g1:
        st.markdown('<div class="card">Transacciones por día (ejemplo)</div>', unsafe_allow_html=True)

        if "fechaf" in df_tx.columns:
            tx_dia = (
                df_tx
                .groupby(df_tx["fechaf"].dt.date)
                .size()
                .reset_index(name="conteo")
            )

            fig, ax = plt.subplots()
            ax.plot(tx_dia["fechaf"], tx_dia["conteo"])
            ax.set_xlabel("Fecha")
            ax.set_ylabel("Transacciones")
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)
        else:
            st.write("No existe columna 'fechaf' en df_tx.")

    # ------ Gráfica 2: Conteo de casos por día (ejemplo) ------
    with col_g2:
        st.markdown('<div class="card">Casos por día (ejemplo)</div>', unsafe_allow_html=True)

        if "fecha" in df_casos.columns:
            casos_dia = (
                df_casos
                .groupby(df_casos["fecha"].dt.date)
                .size()
                .reset_index(name="conteo")
            )

            fig2, ax2 = plt.subplots()
            ax2.bar(casos_dia["fecha"], casos_dia["conteo"])
            ax2.set_xlabel("Fecha")
            ax2.set_ylabel("Casos")
            ax2.tick_params(axis='x', rotation=45)
            st.pyplot(fig2)
        else:
            st.write("No existe columna 'fecha' en df_casos.")

    with col_g4:
        # ========== Gráfica: Top Tipificaciones (Usuarios Churn) ==========
        st.markdown('<div class="card">Tipificaciones más comunes (solo usuarios churn)</div>', unsafe_allow_html=True)

        # Filtrar únicamente casos donde churn = 1
        df_churn = df_casos[df_casos['churn'] == 1].copy()

        if df_churn.empty:
            st.warning("No hay casos de usuarios churn en este mes/año.")
            return

        # Agrupar tipificaciones
        conteo_tips = (
            df_churn
            .groupby('tipificacion_proceso')     # 👈 si se llama distinto, cámbialo aquí
            .size()
            .reset_index(name='count')
            .sort_values('count', ascending=False)
            .head(5)       # TOP 5
        )

        # Gráfica
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        ax3.barh(conteo_tips['tipificacion_proceso'], conteo_tips['count'])
        ax3.invert_yaxis()
        ax3.set_xlabel("Cantidad de casos")
        ax3.set_ylabel("Tipificación")
        ax3.set_title("Top 5 tipificaciones más frecuentes (usuarios churn)")

        st.pyplot(fig3)

    with col_g5:
        st.markdown('<div class="card">Ocupaciones (solo usuarios churn)</div>', unsafe_allow_html=True)

        if df_churn.empty:
            st.warning("No hay casos de usuarios churn en este mes/año.")
            return

        # Agrupar tipificaciones
        conteo_ocp = (
            df_churn
            .groupby('tipificacion_proceso')     # 👈 si se llama distinto, cámbialo aquí
            .size()
            .reset_index(name='count')
            .sort_values('count', ascending=False)
            .head(5)       # TOP 5
        )

        # Gráfica
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        ax3.barh(conteo_tips['tipificacion_proceso'], conteo_tips['count'])
        ax3.invert_yaxis()
        ax3.set_xlabel("Cantidad de casos")
        ax3.set_ylabel("Tipificación")
        ax3.set_title("Top 5 tipificaciones más frecuentes (usuarios churn)")

        st.pyplot(fig3)
        


    # Aquí abajo puedes agregar más filas de gráficas
    # para: ganancias vs pérdidas, tipificación más común, etc.
