import streamlit as st
import matplotlib.pyplot as plt
import json
import geopandas as gpd
import time



def render(df_casos, df_tx):

    t0 = time.perf_counter()

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
                <div class="kpi-title">Meta</div>
                <div class="kpi-value">500,000,000</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Total casos contact center</div>
                <div class="kpi-value">{total_casos:,}</div>
                <div class="kpi-title">Meta</div>
                <div class="kpi-value">5000</div>
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

    #Mapeo de los estados de mexico 
    state_mapping = {
        'AG': 'Aguascalientes','BC': 'Baja California','BS': 'Baja California Sur',
        'CM': 'Campeche','CS': 'Chiapas','CH': 'Chihuahua','CO': 'Coahuila de Zaragoza',
        'CL': 'Colima','DF': 'Ciudad de México','DG': 'Durango','GT': 'Guanajuato',
        'GR': 'Guerrero','HG': 'Hidalgo','JA': 'Jalisco','EM': 'México',
        'MI': 'Michoacán de Ocampo','MO': 'Morelos','NL': 'Nuevo León','OA': 'Oaxaca',
        'PU': 'Puebla','QT': 'Querétaro','QR': 'Quintana Roo','SL': 'San Luis Potosí',
        'SI': 'Sinaloa','SO': 'Sonora','TB': 'Tabasco','TM': 'Tamaulipas',
        'TL': 'Tlaxcala','VE': 'Veracruz de Ignacio de la Llave','YU': 'Yucatán','ZA': 'Zacatecas'
    }

    # Ejemplos de graficas random

    col_g1, col_g2 = st.columns(2)
    col_g4, col_g5 = st.columns(2)

    # Ejemplo conteo de transacciones por dia 
    with col_g1:
        st.markdown('<div class="card">Mapa de personas churn por estado</div>', unsafe_allow_html=True)

        if "state" in df_casos.columns:
            df_usuarios = (
                df_casos[["id_user", "state","churn"]]
                .dropna()
                .drop_duplicates()
            )
        else:
            st.warning("No se encontró la columna 'state' en df_casos.")
            df_usuarios = None

        if df_usuarios is not None and not df_usuarios.empty:

            # Agrupar por estado (abreviatura)
            resumen_estados = (
                df_usuarios
                .groupby("state")
                .agg(
                    total_usuarios=("id_user", "nunique"),
                    churn_usuarios=("churn", lambda x: (x == 1).sum())
                )
                .reset_index()
            )

            # Evitar división entre cero
            resumen_estados["porcentaje_churn"] = (
                resumen_estados["churn_usuarios"] / resumen_estados["total_usuarios"]
            ).fillna(0) * 100

            resumen_estados["estado_full"] = resumen_estados["state"].map(state_mapping)

            # Cargar GeoJSON
            with open("data/mx.json", encoding="utf-8") as f:
                geo = json.load(f)

            gdf_mex = gpd.GeoDataFrame.from_features(geo["features"])

            # Unir el mapa con los datos
            gdf_mex = gdf_mex.merge(
                resumen_estados,
                left_on="name",          # nombre de estado en el geojson
                right_on="estado_full",  # nombre completo mapeado
                how="left"
            )

            gdf_mex["porcentaje_churn"] = gdf_mex["porcentaje_churn"].fillna(0)

            fig_map, ax_map = plt.subplots(figsize=(8, 6))
            gdf_mex.plot(
                column="porcentaje_churn",
                cmap="Reds",          # si quieres otro, aquí lo cambias
                linewidth=0.6,
                edgecolor="black",
                legend=True,
                ax=ax_map
            )

            ax_map.set_axis_off()
            ax_map.set_title("Porcentaje de usuarios churn por estado", fontsize=12)
            st.pyplot(fig_map)

        else:
            st.info("No hay usuarios suficientes para mostrar el mapa con estos filtros.")

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
            .groupby('tipificacion_proceso')     
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
            .groupby('occupation_category')['id_user']
            .nunique()
            .reset_index(name='num_users')
            .sort_values('num_users', ascending=False)     
            .head(5)       # TOP 5
        )

        # Gráfica
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        ax3.barh(conteo_ocp['occupation_category'], conteo_ocp['num_users'])
        ax3.invert_yaxis()
        ax3.set_xlabel("Usuarios churn")
        ax3.set_ylabel("Categoría de ocupación")
        ax3.set_title("Top 5 categorías de ocupación (usuarios churn)")

        st.pyplot(fig3)

        t1 = time.perf_counter()
        print(f"[render] Tiempo render: {t1 - t0:.2f} s")
        


    # Aquí abajo puedes agregar más filas de gráficas
    # para: ganancias vs pérdidas, tipificación más común, etc.
