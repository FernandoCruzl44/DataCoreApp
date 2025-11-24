import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def formato_numero(x):
    try:
        return f"{int(x):,}"
    except:
        return x
def render(df_casos, df_tx, df_master):
    st.markdown('<div class="big-title">Finanzas</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
  
    # grafica 1: ingreso vs perdida
    with col1:
        st.markdown('<div class="card">Ingreso vs Pérdida</div>', unsafe_allow_html=True)
        ingreso_total = df_tx['amount'].sum()
        usuarios_churn = df_casos[df_casos['churn'] == 1]['id_user'].nunique()
        gasto_promedio_usuario = df_tx.groupby('id_user')['amount'].sum().mean()
        perdida_total = usuarios_churn * gasto_promedio_usuario
        categorias = ["Ingreso", "Pérdida"]
        valores = [ingreso_total, perdida_total]
        colores = ["#1f77b4", "#d62728"]
        fig1, ax1 = plt.subplots()
        ax1.bar(categorias, valores, color=colores)
        ax1.tick_params(axis='x', rotation=0)
        fig1.tight_layout()
        st.pyplot(fig1)

    # grafica 2: ingreso promedio por ocupacion
    with col2:
        st.markdown('<div class="card">Ingreso Promedio por Ocupación</div>', unsafe_allow_html=True)
        df_tx_merged = df_tx.merge(df_master[['id_user', 'occupation_category']], on='id_user', how='left')
        ingreso_occ = df_tx_merged.groupby('occupation_category')['amount'].mean().reset_index()
        ingreso_occ['amount'] = ingreso_occ['amount'].apply(lambda x: float(x))
        fig2, ax2 = plt.subplots()
        ax2.bar(ingreso_occ['occupation_category'], ingreso_occ['amount'])
        ax2.tick_params(axis='x', rotation=45)
        fig2.tight_layout()
        st.pyplot(fig2)
      
    # grafica 3: revenue por estado (top 10)
    st.markdown('<div class="card">Revenue por Estado (Top 10)</div>', unsafe_allow_html=True)
    df_tx_master = df_tx.merge(df_master[['id_user', 'state']], on='id_user', how='left')
    revenue_state = df_tx_master.groupby('state')['amount'].sum().reset_index()
    revenue_state = revenue_state.sort_values(by='amount', ascending=False).head(10)
    fig3, ax3 = plt.subplots()
    ax3.bar(revenue_state['state'], revenue_state['amount'])
    ax3.tick_params(axis='x', rotation=45)
    fig3.tight_layout()
    st.pyplot(fig3)
