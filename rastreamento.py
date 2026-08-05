import streamlit as st
import streamlit.components.v1 as components
import requests
import urllib.parse

API_URL = "http://127.0.0.1:8000"

def renderizar_modulo_rastreamento():
    st.balloons()
    numero_pedido = st.session_state.get('numero_pedido', 'N/A')
    cli = st.session_state.get('cliente', {})
    
    st.success(f"🎉 Pagamento Aprovado! Seu pedido **#{numero_pedido}** foi confirmado.")
    
    st.markdown("## 🛵 Rastreamento e Status em Tempo Real")
    
    col_status, col_mapa = st.columns([1, 1.2])
    
    with col_status:
        st.subheader("Etapas da Entrega")
        
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
        
        if st.button("🔄 Atualizar Status no Backend", width="stretch"):
            try:
                res_up = requests.put(
                    f"{API_URL}/pedidos/{numero_pedido}/status",
                    json={"status": status_atual}
                )
                if res_up.status_code == 200:
                    st.toast("Status atualizado no banco de dados!", icon="✅")
                else:
                    st.error(f"Erro no backend: HTTP {res_up.status_code}")
            except Exception as e:
                st.error(f"Erro ao atualizar status: {e}")

        progresso = (status_etapas.index(status_atual) + 1) / len(status_etapas)
        st.progress(progresso)
        
        st.divider()
        st.info(
            f"📍 **Endereço de Entrega:**\n\n"
            f"{cli.get('logradouro', 'Alameda Arminda Nogueira')}, {cli.get('numero', '2463')}\n"
            f"{cli.get('bairro', 'Vila Industrial')} - {cli.get('cidade', 'Franca')}/{cli.get('uf', 'SP')}\n"
            f"**CEP:** {cli.get('cep', '14403-374')}"
        )

    with col_mapa:
        st.subheader("🗺️ Localização pelo Google Maps")
        
        logradouro = cli.get('logradouro', 'Alameda Arminda Nogueira')
        numero = cli.get('numero', '2463')
        cidade = cli.get('cidade', 'Franca')
        uf = cli.get('uf', 'SP')
        
        endereco_completo = f"{logradouro}, {numero}, {cidade} - {uf}, Brasil"
        endereco_encoded = urllib.parse.quote(endereco_completo)
        
        mapa_url = f"https://maps.google.com/maps?q={endereco_encoded}&t=&z=15&ie=UTF8&iwloc=&output=embed"
        
        iframe_html = f"""
            <iframe 
                width="100%" 
                height="380" 
                frameborder="0" 
                scrolling="no" 
                marginheight="0" 
                marginwidth="0" 
                src="{mapa_url}"
                style="border: 1px solid #e6e6e6; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            </iframe>
        """
        components.html(iframe_html, height=400)
    
    st.divider()
    if st.button("⬅️ Voltar para a Loja", type="primary"):
        st.session_state.pedido_finalizado = False
        st.session_state.modo_checkout = False
        st.session_state.etapa = "catalogo"
        st.rerun()