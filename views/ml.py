import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

def render():
    # Título principal
    st.markdown(
        '<div class="big-title">ML model Performance Indicators</div>',
        unsafe_allow_html=True
    )

    #  FILA 1: KPIs GRANDES
    
    kpi_container = st.container()
    with kpi_container:
        col_k1, col_k2, col_k3, col_k4, col_k5, col_k6 = st.columns(6)

        kpis = [
            ("Accuracy %", "77 %"),
            ("F1-Score", "76 %"),
            ("Precision", "60 %"),
            ("Recall", "80 %"),
            ("Área Bajo la Curva", "70 %"),
            ("Tiempo de entrenamiento", "30 s"),
        ]

        cols = [col_k1, col_k2, col_k3, col_k4, col_k5, col_k6]
        for col, (title, value) in zip(cols, kpis):
            with col:
                st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-title">{title}</div>
                        <div class="kpi-value">{value}</div>
                    </div>
                """, unsafe_allow_html=True)

    st.write("")  # espacio

    #  FILA 2: THRESHOLD + MATRIZ DE CONFUSIÓN
    col_g1, col_g2 = st.columns(2)

    # Gráfica de F1 / Precision / Recall vs Threshold (dummy)
    with col_g1:
        st.markdown(
            '<div class="card"><b>F1-score, Recall and Precision vs Threshold</b></div>',
            unsafe_allow_html=True
        )

        thresholds = np.linspace(0.1, 0.9, 50)
        f1 = 0.5 + 0.3 * np.exp(-((thresholds - 0.5) ** 2) / 0.02)
        precision = 0.4 + 0.5 * thresholds
        recall = 1.0 - 0.8 * thresholds

        fig, ax = plt.subplots()
        ax.plot(thresholds, f1, label="F1-score")
        ax.plot(thresholds, precision, label="Precision")
        ax.plot(thresholds, recall, label="Recall")
        ax.set_xlabel("Threshold")
        ax.set_ylabel("Score")
        ax.set_title("F1-score, Recall and Precision vs Threshold")
        ax.legend()
        st.pyplot(fig)

    # Matriz de confusión dummy
    with col_g2:
        st.markdown(
            '<div class="card"><b>Matriz de confusión</b></div>',
            unsafe_allow_html=True
        )

        # Matriz de confusión de ejemplo
        cm = np.array([[149428, 23461],
                       [40600,  48186]])

        fig2, ax2 = plt.subplots()
        im = ax2.imshow(cm, cmap="Blues")

        for (i, j), val in np.ndenumerate(cm):
            ax2.text(j, i, f"{val}", ha="center", va="center", color="black")

        ax2.set_xlabel("Predicho")
        ax2.set_ylabel("Real")
        ax2.set_xticks([0, 1])
        ax2.set_yticks([0, 1])
        ax2.set_title("Matriz de confusión (dummy)")

        fig2.colorbar(im, ax=ax2)
        st.pyplot(fig2)

    #  FILA 3: FEATURE IMPORTANCE
    
    st.write("")
    with st.container():
        st.markdown(
            '<div class="card"><b>Variables que más afectan al modelo</b></div>',
            unsafe_allow_html=True
        )

        features = ["tipificacion_mas_comun", "tendencia_uso", "total_amount", "total_tx"]
        importances = [0.21, 0.17, 0.11, 0.08]

        fig3, ax3 = plt.subplots(figsize=(8, 4))
        ax3.barh(features, importances)
        ax3.invert_yaxis()
        ax3.set_xlabel("Importancia relativa")
        ax3.set_title("Importancia de variables (dummy)")
        st.pyplot(fig3)

