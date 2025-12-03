import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

PRIMARY = "#0083b8"
from components.layout2 import kpi_card, divider, load_styles

def render():

    # TÍTULO PRINCIPAL (igual que el general) 
    st.markdown("<h1 style='color:white;'>ML Model Performance Indicators</h1>", unsafe_allow_html=True)

    # KPIs
    kpi_container = st.container()
    with kpi_container:
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        kpis = [
            ("Accuracy %", "77 %"),
            ("F1-Score", "76 %"),
            ("Precision", "60 %"),
            ("Recall", "80 %"),
            ("Área Bajo la Curva", "70 %"),
            ("Tiempo de entrenamiento", "30 s"),
        ]

        cols = [col1, col2, col3, col4, col5, col6]

        for col, (title, value) in zip(cols, kpis):
            with col:
                st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-title">{title}</div>
                        <div class="kpi-value">{value}</div>
                    </div>
                """, unsafe_allow_html=True)

    st.write("")

    divider()

    #FILA: THRESHOLD + MATRIZ
    col_g1, col_g2 = st.columns([1.2, 1])

    with col_g1:
        st.subheader("F1-score, Recall y Precision vs Threshold")

        thresholds = np.linspace(0.1, 0.9, 50)

        # Series dummy
        f1_scores = 0.5 + 0.3 * np.exp(-((thresholds - 0.5)**2) / 0.02)
        precision = 0.4 + 0.5 * thresholds
        recall = 1 - 0.8 * thresholds

        fig = go.Figure()

        # F1 Score
        fig.add_trace(go.Scatter(
            x=thresholds, y=f1_scores,
            mode="lines",
            name="F1-score",
            line=dict(width=3, color="#ff4b4b"),  # rojo suave
            hovertemplate="Threshold: %{x:.4f}<br>F1-score: %{y:.4f}<extra></extra>"
        ))

        # Recall
        fig.add_trace(go.Scatter(
            x=thresholds, y=recall,
            mode="lines",
            name="Recall",
            line=dict(width=3, color="#00cc96"),  # verde brillante
            hovertemplate="Threshold: %{x:.4f}<br>Recall: %{y:.4f}<extra></extra>"
        ))

        # Precision
        fig.add_trace(go.Scatter(
            x=thresholds, y=precision,
            mode="lines",
            name="Precision",
            line=dict(width=3, color="#0099f9"),  # azul cielo
            hovertemplate="Threshold: %{x:.4f}<br>Precision: %{y:.4f}<extra></extra>"
        ))

        fig.update_layout(
            xaxis_title="Threshold",
            yaxis_title="Score",
            hovermode="x unified",

            # === Estilo visual igual al dashboard general ===
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white", size=14),

            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(font=dict(color="white", size=12))
        )

        fig.update_xaxes(color="white", gridcolor="rgba(255,255,255,0.08)")
        fig.update_yaxes(color="white", gridcolor="rgba(255,255,255,0.08)")

        st.plotly_chart(fig, use_container_width=True)

    #MATRIZ DE CONFUSIÓN
    with col_g2:
        st.subheader("Matriz de confusión")

        cm = np.array([[149428, 23461],
                       [40600,  48186]])

        df_cm = pd.DataFrame(cm, columns=["Predicho 0", "Predicho 1"], index=["Real 0", "Real 1"])

        fig2 = px.imshow(
            df_cm,
            color_continuous_scale=[[0, "#001f2e"], [1, PRIMARY]],
            text_auto=True
        )

        fig2.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            coloraxis_showscale=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white", size=14)
        )

        fig2.update_xaxes(color="white")
        fig2.update_yaxes(color="white")

        st.plotly_chart(fig2, use_container_width=True)

    st.write("")

    #FEATURE IMPORTANCE
    st.subheader("Variables que más afectan al modelo")

    features = ["tipificacion_mas_comun", "tendencia_uso", "total_amount", "total_tx"]
    importances = [0.21, 0.17, 0.11, 0.08]

    fig3 = go.Figure(go.Bar(
        x=importances,
        y=features,
        orientation="h",
        marker=dict(color=PRIMARY)
    ))

    fig3.update_layout(
        height=300,
        margin=dict(l=10, r=30, t=10, b=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white", size=14)
    )

    fig3.update_yaxes(autorange="reversed", color="white")
    fig3.update_xaxes(color="white")

    st.plotly_chart(fig3, use_container_width=True)
