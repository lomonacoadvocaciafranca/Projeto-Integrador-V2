import streamlit as st
import streamlit.components.v1 as components

def renderizar_modulo_rastreamento():
    st.title("🚚 Rastreamento do Pedido")
    st.success("Pagamento aprovado! Seu pedido já está em preparação e sairá para entrega em breve.")
    
    cliente = st.session_state.cliente
    cep_loja = "14403-374"
    cep_cliente = cliente['cep']
    
    st.markdown(f"**Endereço de Destino:** {cliente['logradouro']}, {cliente['numero']} - {cliente['bairro']}, {cliente['cidade']}/{cliente['uf']}")
    st.markdown("### Rota de Entrega (Google Maps)")
    
    # URL Iframe do Google Maps que traça a rota da origem (saddr) até o destino (daddr)
    url_mapa = f"https://maps.google.com/maps?saddr={cep_loja}&daddr={cep_cliente}&output=embed"
    
    components.html(f'''
        <iframe 
            width="100%" 
            height="500" 
            frameborder="0" 
            style="border:0; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" 
            src="{url_mapa}" 
            allowfullscreen>
        </iframe>
    ''', height=520)
    
    st.divider()
    if st.button("Fazer Novo Pedido", use_container_width=True):
        st.session_state.carrinho = []
        st.session_state.modo_checkout = False
        st.session_state.pedido_finalizado = False
        st.session_state.frete_calculado = None
        st.rerun()