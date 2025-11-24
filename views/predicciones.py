import streamlit as st


def render(df_risk):
    st.title("Predicciones de Riesgo")


    st.markdown("Selecciona un grupo de riesgo para ver algunos usuarios:")


    col1, col2, col3 = st.columns(3)


    # Definir thresholds
    high_threshold = 0.66
    medium_low = 0.33


    # Filtrar grupos
    riesgo_alto = df_risk[df_risk["prob_churn"] >= high_threshold]
    riesgo_medio = df_risk[(df_risk["prob_churn"] < high_threshold) & (df_risk["prob_churn"] >= medium_low)]
    riesgo_bajo = df_risk[df_risk["prob_churn"] < medium_low]


    # ------------------------
    # RIESGO ALTO
    # ------------------------
    with col1:
        if st.button("🔥 Riesgo Alto", use_container_width=True):
            st.subheader("Usuarios con Riesgo Alto")
            df_display = riesgo_alto[["id_user", "prob_churn"]].sort_values("prob_churn", ascending=False).head(10)
            st.dataframe(df_display, use_container_width=True)


            # --- ACCIONES: MENSAJE Y PROMO ---
            st.markdown("### Acciones sugeridas")
            col_msg, col_promo = st.columns(2)


            with col_msg:
                if st.button("✉️ Mensaje sugerido - Alto"):
                    st.info(
                        """
                        **Mensaje sugerido (Riesgo Alto):**


                        Hola 👋  
                        Notamos que recientemente has tenido menos actividad en tu cuenta.  
                        Queremos asegurarnos de que estás aprovechando todos los beneficios.


                        Si tienes dudas o quieres explorar nuevas herramientas financieras,  
                        estamos aquí para apoyarte 💙


                        *Tu estabilidad financiera es nuestra prioridad.*
                        """
                    )
           
            with col_promo:
                if st.button("🎁 Promo sugerida - Alto"):
                    st.success(
                        """
                        **Promo para retención (Riesgo Alto):**


                        🎉 *Oferta exclusiva*  
                        Recibe **$150 MXN de cashback** al realizar **3 pagos de servicios** en los próximos 7 días.


                        Queremos ayudarte a mantener el control de tus finanzas de forma fácil y segura 💰
                        """
                    )


    # ------------------------
    # RIESGO MEDIO
    # ------------------------
    with col2:
        if st.button("🟡 Riesgo Medio", use_container_width=True):
            st.subheader("Usuarios con Riesgo Medio")
            df_display = riesgo_medio[["id_user", "prob_churn"]].sort_values("prob_churn", ascending=False).head(10)
            st.dataframe(df_display, use_container_width=True)


            # --- ACCIONES: MENSAJE Y PROMO ---
            st.markdown("### Acciones sugeridas")
            col_msg, col_promo = st.columns(2)


            with col_msg:
                if st.button("✉️ Mensaje sugerido - Medio"):
                    st.info(
                        """
                        **Mensaje sugerido (Riesgo Medio):**


                        Hola 👋  
                        Hemos visto que tu actividad ha bajado un poco.  
                        Queremos recordarte que puedes seguir administrando tus finanzas con herramientas fáciles de usar.


                        Si necesitas apoyo o resolver dudas, estamos listos para ayudarte 💙
                        """
                    )
           
            with col_promo:
                if st.button("🎁 Promo sugerida - Medio"):
                    st.success(
                        """
                        **Promo para retención (Riesgo Medio):**


                        Aprovecha un **bono del 1%** por cada transferencia SPEI  
                        realizada esta semana, acumulable hasta **$50 MXN**.


                        ¡Gracias por seguir con nosotros! 🙌
                        """
                    )


    # ------------------------
    # RIESGO BAJO / ESTABLE
    # ------------------------
    with col3:
        if st.button("🔵 Riesgo Estable", use_container_width=True):
            st.subheader("Usuarios con Riesgo Estable")
            df_display = riesgo_bajo[["id_user", "prob_churn"]].sort_values("prob_churn", ascending=False).head(10)
            st.dataframe(df_display, use_container_width=True)


            # --- ACCIONES: MENSAJE Y PROMO ---
            st.markdown("### Acciones sugeridas")
            col_msg, col_promo = st.columns(2)


            with col_msg:
                if st.button("✉️ Mensaje sugerido - Estable"):
                    st.info(
                        """
                        **Mensaje sugerido (Riesgo Estable):**


                        ¡Gracias por seguir usando nuestra plataforma! 💙  
                        Queremos que sigas aprovechando todas las herramientas que tenemos para ti.


                        Si en algún momento necesitas ayuda o asesoría, estamos listos para apoyarte.
                        """
                    )
           
            with col_promo:
                if st.button("🎁 Promo sugerida - Estable"):
                    st.success(
                        """
                        **Promo (Usuarios Estables):**


                        🎁 Obtén **$20 MXN de cashback** al completar un pago recurrente nuevo  
                        durante esta semana.


                        ¡Gracias por ser un usuario activo de nuestra fintech! 🚀
                        """
                    )


