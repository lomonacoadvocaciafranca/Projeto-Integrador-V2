import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

def renderizar_modulo_rastreamento():
    st.balloons()
    st.success(f"🎉 Pagamento Aprovado! Seu pedido **#{st.session_state.numero_pedido}** foi confirmado.")
    
    st.markdown("## 🛵 Rastreamento e Status em Tempo Real")
    
    status_etapas = [
        "Recebido", 
        "Em Produção (Forno & Confeitaria)", 
        "Despachado (Embalado p/ Transporte)", 
        "Saiu para Entrega", 
        "Entregue"
    ]
    
    status_atual = st.select_slider(
        "Simular evolução do pedido:",
        options=status_etapas,
        value="Recebido"
    )
    
    if st.button("🔄 Atualizar Status no Backend"):
        try:
            res_up = requests.put(
                f"{API_URL}/pedidos/{st.session_state.numero_pedido}/status",
                json={"status": status_atual}
            )
            if res_up.status_code == 200:
                st.toast("Status atualizado no banco de dados!", icon="✅")
        except Exception as e:
            st.error(f"Erro ao atualizar status: {e}")

    progresso = (status_etapas.index(status_atual) + 1) / len(status_etapas)
    st.progress(progresso)
    
    st.divider()
    if st.button("Voltar para a Loja"):
        st.session_state.pedido_finalizado = False
        st.rerun()
