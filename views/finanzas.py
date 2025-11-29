import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
st.markdown("""
<style>
/* Agranda el número principal del st.metric */
[data-testid="stMetricValue"] {
    font-size: 42px !important;
    font-weight: 800 !important;
}

/* Agranda el label */
[data-testid="stMetricLabel"] {
    font-size: 16px !important;
}

/* Agranda el delta */
[data-testid="stMetricDelta"] {
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)


def render(df_casos, df_tx, df_master):

    st.markdown('<div class="big-title">Finanzas</div>', unsafe_allow_html=True)

    # ============================
    # LAYOUT SUPERIOR
    # ============================

    col_kpi, col_occ = st.columns([1.1, 2])

    with col_kpi:

        st.markdown('<div class="card">Ingreso vs Costo de Oportunidad</div>', unsafe_allow_html=True)

        ingreso_total = df_tx['amount'].sum()
        usuarios_churn = df_casos[df_casos['churn'] == 1]['id_user'].nunique()
        gasto_promedio_usuario = df_tx.groupby('id_user')['amount'].sum().mean()
        perdida_total = usuarios_churn * gasto_promedio_usuario

        kpi1, kpi2 = st.columns(2)

        with kpi1:
            st.metric(
                label="Ingreso total",
                value=f"${ingreso_total:,.0f}",
                delta=f"+${ingreso_total:,.0f}"
            )

        with kpi2:
            st.metric(
                label="Costo de Oportunidad",
                value=f"${perdida_total:,.0f}",
                delta=f"-${perdida_total:,.0f}"
            )


    # ============================
    # GRAFICA: INGRESO POR OCUPACION
    # ============================

    with col_occ:
        st.markdown('<div class="card">Ingreso Promedio por Ocupación</div>', unsafe_allow_html=True)

        df_tx_merged = df_tx.merge(
            df_master[["id_user", "occupation_category"]],
            on="id_user",
            how="left"
        )

        ingreso_occ = (
            df_tx_merged
            .groupby("occupation_category")["amount"]
            .mean()
            .reset_index()
            .sort_values("amount", ascending=False)
            .head(10)
        )

        fig_occ = px.bar(
            ingreso_occ,
            x="occupation_category",
            y="amount"
        )

        fig_occ.update_layout(height=360)
        st.plotly_chart(fig_occ, use_container_width=True)

    st.write("")

    # ============================
    # MAPA: REVENUE POR ESTADO
    # ============================

    st.markdown('<div class="card">Revenue por Estado</div>', unsafe_allow_html=True)

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

    df_tx_master = df_tx.merge(df_master[["id_user", "state"]], on="id_user", how="left")

    revenue_state = (
        df_tx_master
        .groupby("state")["amount"]
        .sum()
        .reset_index()
    )

    revenue_state["estado_full"] = revenue_state["state"].map(state_mapping)

    with open("data/mx.json", encoding="utf-8") as f:
        geo = json.load(f)

    fig_map = px.choropleth(
        revenue_state,
        geojson=geo,
        locations="estado_full",
        featureidkey="properties.name",
        color="amount",
        color_continuous_scale="Blues",
        hover_name="estado_full",
        labels={"amount": "Revenue"}
    )

    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.update_layout(
        height=430,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig_map, use_container_width=True)
