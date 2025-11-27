import json
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import geopandas as gpd

from components.layout2 import kpi_card, divider, load_styles

# Color primario
PRIMARY = "#0083b8"
BG = "#06141f"

# Mapping abreviaturas -> nombre completo (usa el mismo mapping que tienes)
STATE_MAPPING = {
    'AG': 'Aguascalientes','BC': 'Baja California','BS': 'Baja California Sur',
    'CM': 'Campeche','CS': 'Chiapas','CH': 'Chihuahua','CO': 'Coahuila de Zaragoza',
    'CL': 'Colima','DF': 'Ciudad de México','DG': 'Durango','GT': 'Guanajuato',
    'GR': 'Guerrero','HG': 'Hidalgo','JA': 'Jalisco','EM': 'México',
    'MI': 'Michoacán de Ocampo','MO': 'Morelos','NL': 'Nuevo León','OA': 'Oaxaca',
    'PU': 'Puebla','QT': 'Querétaro','QR': 'Quintana Roo','SL': 'San Luis Potosí',
    'SI': 'Sinaloa','SO': 'Sonora','TB': 'Tabasco','TM': 'Tamaulipas',
    'TL': 'Tlaxcala','VE': 'Veracruz de Ignacio de la Llave','YU': 'Yucatán','ZA': 'Zacatecas'
}


def render(df_casos, df_tx):

    # Aplicar estilos globales
    load_styles()

    st.markdown("<h1 style='color:white;'>Dashboard General</h1>", unsafe_allow_html=True)

    df = df_casos.copy()
    df_tx_local = df_tx.copy()

    # -------------------------
    # KPIs (4 en la misma fila)
    # -------------------------
    total_casos = df.shape[0]
    total_tx = int(df_tx_local['n_tx'].sum()) if 'n_tx' in df_tx_local.columns else 0
    ingresos = df_tx_local['amount'].sum() if 'amount' in df_tx_local.columns else 0
    ingresos_fmt = f"${ingresos:,.0f}"

    churn_count = df[df['churn'] == 1].shape[0]
    churn_rate = 0 if total_casos == 0 else round((churn_count / total_casos) * 100, 2)

    col1, col2, col3, col4 = st.columns(4, gap="small")

    # Total de Casos (con meta pequeña abajo)
    with col1:
        # usamos meta_text para el texto pequeño (layout2.kpi_card lo soporta)
        kpi_card("Total de Casos", f"{total_casos:,}", meta_text="Meta: 5,000")

    # Ingresos (reemplaza "Clientes Churn")
    with col2:
        kpi_card("Ingresos", ingresos_fmt)

    # Churn %
    with col3:
        kpi_card("Churn %", f"{churn_rate}%")

    # Total Transacciones + meta pequeña
    with col4:
        kpi_card("Total Transacciones", f"{total_tx:,}", meta_text="Meta: 500,000,000")

    # Separador
    divider()

    # -------------------------
    # GRID 2x2: Row1 (Casos por día | Mapa)
    #         Row2 (Tipificaciones | Ocupaciones)
    # -------------------------
    row1_col1, row1_col2 = st.columns(2, gap="large")

    # ---------- Casos por Día (left, plotly) ----------
    with row1_col1:
        st.subheader("Casos por Día")
        if "fecha" in df.columns:
            casos_dia = df.groupby(df["fecha"].dt.date).size().reset_index(name="casos")
            casos_dia.columns = ["fecha", "casos"]

            fig_dia = px.line(
                casos_dia,
                x="fecha",
                y="casos",
                markers=True,
                color_discrete_sequence=[PRIMARY],
            )
            fig_dia.update_layout(
                plot_bgcolor=BG,
                paper_bgcolor=BG,
                font_color="white",
                margin=dict(l=10, r=10, t=10, b=10),
            )
            fig_dia.update_xaxes(showgrid=False, color="white")
            fig_dia.update_yaxes(showgrid=False, color="white")
            st.plotly_chart(fig_dia, use_container_width=True)
        else:
            st.info("No existe la columna 'fecha' en los datos.")

    # ---------- Mapa de México (right, geopandas + matplotlib) ----------
    with row1_col2:
        st.subheader("Mapa de personas churn por estado (México)")

        # Filtrar churn
        df_churn = df[df['churn'] == 1].copy()

        if df_churn.empty:
            st.info("No hay casos de usuarios churn para mostrar en el mapa.")
        else:
            # Contar churn por abreviatura de estado
            resumen_estados = (
                df_churn
                .groupby("state")
                .agg(total_usuarios=("churn", "size"))
                .reset_index()
            )

            # mapear abreviatura -> nombre completo para casar con geojson
            resumen_estados["estado_full"] = resumen_estados["state"].map(STATE_MAPPING)

            # Cargar geojson de México (ruta relativa al proyecto)
            try:
                with open("data/mx.json", encoding="utf-8") as f:
                    geo = json.load(f)
            except FileNotFoundError:
                st.error("No se encontró 'data/mx.json'. Asegúrate de que exista.")
                resumen_estados = None
                geo = None

            if geo is not None and resumen_estados is not None:
                gdf_mex = gpd.GeoDataFrame.from_features(geo["features"])

                # Unir por nombre completo
                gdf_mex = gdf_mex.merge(
                    resumen_estados,
                    left_on="name",
                    right_on="estado_full",
                    how="left"
                )

                gdf_mex["total_usuarios"] = gdf_mex["total_usuarios"].fillna(0)

                fig_map, ax_map = plt.subplots(1, 1, figsize=(8, 6), facecolor=BG)
                ax_map.set_facecolor(BG)

                # Usamos un cmap azul y edgecolor oscuro; la escala se ajusta a los datos
                gdf_mex.plot(
                    column="total_usuarios",
                    cmap="Blues",
                    linewidth=0.5,
                    edgecolor="#0b2a3a",
                    legend=True,
                    ax=ax_map
                )

                cb = ax_map.get_figure().axes[-1]  # colorbar
                cb.tick_params(labelcolor="white")  # números en blanco
                cb.yaxis.label.set_color("white")  # título blanco (por si acaso)
                cb.set_title("")  
                ax_map.set_axis_off()

                st.pyplot(fig_map)

    row2_col1, row2_col2 = st.columns(2, gap="large")

    # ================================
    # TIPIFICACIONES (CHURN)
    # ================================
    with row2_col1:
        st.subheader("Tipificaciones más comunes (solo usuarios churn)")

        df_churn = df[df['churn'] == 1].copy()

        if df_churn.empty:
            st.warning("No hay casos de usuarios churn en este mes/año.")
        else:

            conteo_tips = (
                df_churn
                .groupby("tipificacion_proceso")
                .size()
                .reset_index(name="count")
                .sort_values("count", ascending=False)
                .head(5)
            )

            fig_tips = px.bar(
                conteo_tips,
                x="count",
                y="tipificacion_proceso",
                orientation="h",
                color_discrete_sequence=[PRIMARY]
            )

            fig_tips.update_layout(
                plot_bgcolor=BG,
                paper_bgcolor=BG,
                font_color="white",
                margin=dict(l=10, r=10, t=10, b=10),
                height=350
            )

            fig_tips.update_xaxes(color="white", showgrid=False)
            fig_tips.update_yaxes(color="white", autorange="reversed", showgrid=False)

            st.plotly_chart(fig_tips, use_container_width=True)


    # ================================
    # OCUPACIONES (CHURN)
    # ================================
    with row2_col2:
        st.subheader("Ocupaciones más comunes (solo usuarios churn)")

        if df_churn.empty:
            st.warning("No hay casos de usuarios churn en este mes/año.")
        else:

            conteo_ocp = (
                df_churn["occupation_category"]
                .fillna("Sin Información")
                .value_counts()
                .head(10)
                .reset_index()
            )

            conteo_ocp.columns = ["occupation_category", "num_users"]

            fig_ocp = px.bar(
                conteo_ocp,
                x="num_users",
                y="occupation_category",
                orientation="h",
                color_discrete_sequence=[PRIMARY]
            )

            fig_ocp.update_layout(
                plot_bgcolor=BG,
                paper_bgcolor=BG,
                font_color="white",
                margin=dict(l=10, r=10, t=10, b=10),
                height=350
            )

            fig_ocp.update_xaxes(color="white", showgrid=False)
            fig_ocp.update_yaxes(color="white", autorange="reversed", showgrid=False)

            st.plotly_chart(fig_ocp, use_container_width=True)
