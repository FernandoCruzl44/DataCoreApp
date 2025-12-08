import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import time 

from components.layout2 import kpi_card, divider, load_styles

PRIMARY = "#0083b8"
BG = "#06141f"


def render(df_casos, df_tx, df_master):
    load_styles()

    # estilos visuales para métricas
    st.markdown("""
        <style>
            [data-testid="stMetricValue"] {
                font-size: 42px !important;
                font-weight: 800 !important;
            }

            [data-testid="stMetricLabel"] {
                font-size: 16px !important;
            }

            [data-testid="stMetricDelta"] {
                font-size: 18px !important;
            }
                    
            [data-testid="stMetric"] {
                background-color: #0d2536;
                padding: 16px 20px;
                border-radius: 8px;
                border: 1px solid #1b3b52;
                width: 100%;
            }
        </style>
        """, unsafe_allow_html=True)

    # título principal
    st.markdown("<h1 style='color:white;'>Finanzas</h1>", unsafe_allow_html=True)

    # sección superior
    col_kpi, col_occ = st.columns([1.1, 2])

    with col_kpi:

        st.subheader("Ingreso vs costo de oportunidad")

        # ingreso total calculado
        ingreso_total = df_tx['amount'].sum()

        # cálculo del costo de oportunidad
        usuarios_churn = df_casos[df_casos['churn'] == 1]['id_user'].nunique()
        gasto_promedio_usuario = df_tx.groupby('id_user')['amount'].sum().mean()
        perdida_total = usuarios_churn * gasto_promedio_usuario

        # kpi de ingreso con delta dummy
        st.metric(
            label="Ingreso total",
            value=f"${ingreso_total:,.0f}",
            delta="+$12.4%"     # valor dummy
        )

        # espacio estético
        st.write("")

        # kpi de costo con delta dummy
        st.metric(
            label="Costo de oportunidad",
            value=f"${perdida_total:,.0f}",
            delta="-$8.3%"      # valor dummy
        )

    # gráfica: ingreso promedio por ocupación
    with col_occ:
        st.subheader("Ingreso promedio por ocupación")

        t0 = time.perf_counter()

        # merge para traer ocupación
        df_tx_merged = df_tx.merge(
            df_master[["id_user", "occupation_category", "state"]],
            on="id_user",
            how="left"
        )

        # cálculo del top 10
        ingreso_occ = (
            df_tx_merged
            .groupby("occupation_category")["amount"]
            .mean()
            .reset_index()
            .sort_values("amount", ascending=False)
            .head(10)
        )

        t1 = time.perf_counter()
        print(f"[finanzas] ingreso por ocupacion tardó: {t1 - t0:.4f} s")

        # gráfica
        fig_occ = px.bar(
            ingreso_occ,
            x="occupation_category",
            y="amount"
        )

        fig_occ.update_layout(height=360)
        st.plotly_chart(fig_occ, use_container_width=True)

    st.write("")

    # mapa: revenue por estado
    st.subheader("Revenue por estado")

    # mapeo de abreviaturas a nombres
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

    t0 = time.perf_counter()

    # agrupar revenue por estado
    revenue_state = (
        df_tx_merged
        .groupby("state")["amount"]
        .sum()
        .reset_index()
    )

    t1 = time.perf_counter()
    print(f"[finanzas] revenue por estado tardó: {t1 - t0:.4f} s")

    # asignar nombre completo
    revenue_state["estado_full"] = revenue_state["state"].map(state_mapping)

    # cargar geojson
    with open("data/mx.json", encoding="utf-8") as f:
        geo = json.load(f)

    # crear mapa
    fig_map = px.choropleth(
        revenue_state,
        geojson=geo,
        locations="estado_full",
        featureidkey="properties.name",
        color="amount",
        color_continuous_scale=[
            "#00121a", "#00334d", "#00557a", "#0077a6", "#0083b8", "#35a5d1"
        ],
        hover_name="estado_full",
        labels={"amount": "Revenue"}
    )

    # bordes blancos
    fig_map.update_traces(marker_line_width=0.8, marker_line_color="white")

    # estilos oscuros
    fig_map.update_layout(
        height=430,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        geo=dict(bgcolor=BG),
        font=dict(color="white"),
        coloraxis_colorbar=dict(
            tickfont=dict(color="white"),
            title=dict(font=dict(color="white"))
        ),
    )

    # centrado y limpieza
    fig_map.update_geos(
        fitbounds="locations",
        visible=False,
        bgcolor=BG
    )

    st.plotly_chart(fig_map, width='stretch')