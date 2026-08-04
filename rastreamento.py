import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

def renderizar_modulo_rastreamento():
    """Exibe o progresso de fabricação, despacho e o mapa de entrega"""
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
        value="Em Produção (Forno & Confeitaria)"
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
    
    col_prod, col_desp, col_ent = st.columns(3)
    
    with col_prod:
        st.markdown("### 🏭 1. Produção")
        if status_etapas.index(status_atual) >= 1:
            st.success("✅ **Massa assada & Cobertura**")
            st.caption("Chef: Lucas Silva | Temp: 180°C")
        else:
            st.info("⏳ Fila da cozinha...")
            
    with col_desp:
        st.markdown("### 📦 2. Despacho")
        if status_etapas.index(status_atual) >= 2:
            st.success("✅ **Caixa selada**")
            st.caption("Etiqueta #CPK-8894")
        else:
            st.info("⏳ Em produção...")

    with col_ent:
        st.markdown("### 🛵 3. Entrega")
        if status_etapas.index(status_atual) >= 3:
            st.success("✅ **A caminho**")
            st.caption("Moto Honda CG 160 (ABC-1234)")
        else:
            st.info("⏳ Aguardando despacho...")

    st.divider()
    st.subheader("🗺️ Rastreamento no Mapa")
    
    lat_loja, lon_loja = -20.5387, -47.4009
    
    if status_atual == "Saiu para Entrega":
        lat_entregador, lon_entregador = lat_loja + 0.005, lon_loja + 0.005
        st.info("📍 O entregador está a **1.2 km** de distância (Previsão: 8 minutos).")
    elif status_atual == "Entregue":
        lat_entregador, lon_entregador = lat_loja + 0.010, lon_loja + 0.010
        st.success("📍 Pedido entregue!")
    else:
        lat_entregador, lon_entregador = lat_loja, lon_loja
        st.warning("📍 O pedido está na loja aguardando transporte.")

    dados_mapa = pd.DataFrame({
        "lat": [lat_loja, lat_entregador],
        "lon": [lon_loja, lon_entregador],
        "ponto": ["Loja", "Entregador"]
    })

    st.map(dados_mapa, zoom=14)
    
    link_google_maps = f"https://www.google.com/maps/search/?api=1&query={lat_entregador},{lon_entregador}"
    st.markdown(f"[🔗 Abrir no Google Maps]({link_google_maps})")

    st.divider()
    if st.button("Voltar para a Loja"):
        st.session_state.pedido_finalizado = False
        st.rerun()