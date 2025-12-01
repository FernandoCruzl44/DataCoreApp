import time
import json
import pandas as pd
import plotly.express as px
import streamlit as st

from components.layout2 import kpi_card, divider, load_styles

# Colores base
PRIMARY = "#0083b8"
BG = "#06141f"

# Mapping abreviaturas -> nombre completo
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


def render(df_casos: pd.DataFrame,
           df_tx: pd.DataFrame,
           filtros: dict,
           df_semana: pd.DataFrame,
           df_mes: pd.DataFrame):

    print("\n====== [GENERAL TURBO] INICIO RENDER ======")
    t_global0 = time.perf_counter()

    # Estilos globales
    load_styles()

    # ---------------------------------------------------------
    # TÍTULO
    # ---------------------------------------------------------
    st.markdown("<h1 style='color:white;'>Dashboard General</h1>", unsafe_allow_html=True)

    df = df_casos.copy()
    df_tx_local = df_tx.copy()

    # ---------------------------------------------------------
    # KPIs
    # ---------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4, gap="small")

    total_casos = df.shape[0]
    total_tx = int(df_tx_local['n_tx'].sum()) if 'n_tx' in df_tx_local.columns else 0
    ingresos = df_tx_local['amount'].sum() if 'amount' in df_tx_local.columns else 0

    churn_count = df[df.get('churn', 0) == 1].shape[0] if 'churn' in df.columns else 0
    churn_rate = 0 if total_casos == 0 else round((churn_count / total_casos) * 100, 2)

    with col1:
        kpi_card("Total de Casos", f"{total_casos:,}", meta_text="Meta: 5,000")

    with col2:
        kpi_card("Ingresos", f"${ingresos:,.0f}")

    with col3:
        kpi_card("Churn %", f"{churn_rate}%")

    with col4:
        kpi_card("Total Transacciones", f"{total_tx:,}", meta_text="Meta: 500,000,000")

    divider()

    # ---------------------------------------------------------
    # LAYERS
    # Row 1 → Mapa | Ingresos
    # Row 2 → Tipificaciones | Ocupaciones
    # ---------------------------------------------------------
    row1_col1, row1_col2 = st.columns(2, gap="large")
    row2_col1, row2_col2 = st.columns(2, gap="large")

    # ======================================================
    # MAPA PLOTLY (% CHURN por estado)
    # ======================================================
    with row1_col1:
        st.subheader(" % churn por estado (México)")

        if "state" in df_casos.columns:
            df_usuarios = (
                df_casos[["id_user", "state", "churn"]]
                .dropna()
                .drop_duplicates()
            )
        else:
            st.warning("No se encontró la columna 'state' en df_casos.")
            df_usuarios = None

        if df_usuarios is not None and not df_usuarios.empty:

            resumen_estados = (
                df_usuarios
                .groupby("state")
                .agg(
                    total_usuarios=("id_user", "nunique"),
                    churn_usuarios=("churn", lambda x: (x == 1).sum())
                )
                .reset_index()
            )

            resumen_estados["porcentaje_churn"] = (
                resumen_estados["churn_usuarios"] / resumen_estados["total_usuarios"]
            ).fillna(0) * 100

            resumen_estados["estado_full"] = resumen_estados["state"].map(state_mapping)

            with open("data/mx.json", encoding="utf-8") as f:
                geo = json.load(f)

            fig_map = px.choropleth(
                resumen_estados,
                geojson=geo,
                locations="estado_full",
                featureidkey="properties.name",
                color="porcentaje_churn",
                color_continuous_scale=[
                    "#00121a", "#00334d", "#00557a", "#0077a6", "#0083b8", "#35a5d1"
                ],
                hover_name="estado_full",
                hover_data={
                    "total_usuarios": True,
                    "churn_usuarios": True,
                    "porcentaje_churn": ':.2f'
                },
                labels={"porcentaje_churn": "% churn"},
            )

            # BORDES BLANCOS COMO TU GRÁFICA ORIGINAL
            fig_map.update_traces(marker_line_width=0.8, marker_line_color="white")

            # FONDO OSCURO REAL
            fig_map.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor="#06141f",    # Fondo del dashboard
                plot_bgcolor="#06141f",
                geo=dict(bgcolor="#06141f"),
                font=dict(color="white"),
                coloraxis_colorbar=dict(
                    tickfont=dict(color="white"),
                    title=dict(font=dict(color="white"))
                ),
            )

            # Mantener el mapa centrado y visible
            fig_map.update_geos(
                fitbounds="locations",
                visible=False,
                bgcolor="#06141f"
            )

            st.plotly_chart(fig_map, use_container_width=True)

        else:
            st.info("No hay usuarios suficientes para mostrar el mapa con estos filtros.")

    # ======================================================
    # INGRESOS
    # df_semana / df_mes TURBO
    # ======================================================
    with row1_col2:
        st.subheader("Ingresos en el tiempo")

        año = filtros.get("año")
        mes = filtros.get("mes")

        fig = None

        # Sin año → vista por semana
        if año is None:
            df_plot = df_semana.copy()
            df_plot["periodo"] = df_plot["semana"]
            fig = px.line(df_plot, x="periodo", y="amount", markers=True)

        # Solo año → meses
        elif año is not None and mes is None:
            df_plot = df_mes[df_mes["año"] == año].copy()
            df_plot["periodo"] = df_plot["mes"].astype(str)
            fig = px.line(df_plot, x="periodo", y="amount", markers=True)

        # Año + mes → semanas mes-1, mes, mes+1
        else:
            df_plot = df_semana.copy()
            df_plot = df_plot[
                (df_plot["semana"].dt.year == año) &
                (df_plot["semana"].dt.month.between(mes - 1, mes + 1))
            ]
            df_plot["periodo"] = df_plot["semana"]

            if df_plot.empty:
                st.warning("No hay suficientes semanas alrededor del mes seleccionado.")
                fig = None
            else:
                fig = px.line(df_plot, x="periodo", y="amount", markers=True)

        if fig is not None:
            fig.update_layout(
                height=350,
                plot_bgcolor=BG,
                paper_bgcolor=BG,
                font_color="white",
                margin=dict(l=10, r=10, t=10, b=10),
            )
            fig.update_xaxes(color="white", showgrid=False)
            fig.update_yaxes(color="white", showgrid=False)
            st.plotly_chart(fig, use_container_width=True)

    # ======================================================
    # TIPIFICACIONES churn
    # ======================================================
    with row2_col1:
        st.subheader("Tipificaciones más comunes (solo usuarios churn)")

        df_churn = df[df['churn'] == 1].copy() if "churn" in df.columns else pd.DataFrame()

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
                height=350,
                margin=dict(l=10, r=10, t=10, b=10)
            )

            fig_tips.update_yaxes(autorange="reversed", color="white")
            fig_tips.update_xaxes(color="white")

            st.plotly_chart(fig_tips, use_container_width=True)

    # ======================================================
    # OCUPACIONES churn
    # ======================================================
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
                height=350,
                margin=dict(l=10, r=10, t=10, b=10)
            )

            fig_ocp.update_xaxes(color="white", showgrid=False)
            fig_ocp.update_yaxes(color="white", autorange="reversed", showgrid=False)

            st.plotly_chart(fig_ocp, use_container_width=True)

    print(f"====== [GENERAL TURBO] Render total: {time.perf_counter() - t_global0:.2f} s ======\n")
