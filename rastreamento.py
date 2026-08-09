import streamlit as st
import time
import random

def renderizar_modulo_rastreamento():
    st.title("🚚 Rastreamento do Pedido")
    st.success("Pagamento aprovado! Seu pedido já está em preparação.")
    
    # --- 1. BARRA DE ANDAMENTO DA PRODUÇÃO ---
    st.markdown("### Andamento da Produção")
    
    if 'progresso_producao' not in st.session_state:
        st.session_state.progresso_producao = 0
        st.session_state.etapa_atual = "Recebido"
        
    barra_progresso = st.progress(st.session_state.progresso_producao)
    texto_status = st.empty()
    
    etapas = [
        (20, "Recebido"), 
        (40, "Preparando a massa"), 
        (60, "Assando os cupcakes"), 
        (80, "Decorando"), 
        (100, "Pronto para entrega!")
    ]

    # Simulação visual do progresso (executa apenas uma vez por pedido finalizado)
    if st.session_state.progresso_producao < 100:
        progresso_atual = 0
        for limite, nome_etapa in etapas:
            while progresso_atual <= limite:
                barra_progresso.progress(progresso_atual)
                texto_status.write(f"**Status:** {nome_etapa}")
                progresso_atual += 2
                time.sleep(0.05)
        st.session_state.progresso_producao = 100
        st.session_state.etapa_atual = "Pronto para entrega!"
    else:
        barra_progresso.progress(100)
        texto_status.write(f"**Status:** {st.session_state.etapa_atual}")

    # --- 2. JANELA DE PREVISÃO (Aprox. 5 cm x 5 cm) ---
    if 'tempo_estimado' not in st.session_state:
        st.session_state.tempo_estimado = random.randint(20, 45)
        
    # 5 cm equivalem a aproximadamente 190 pixels na maioria dos monitores
    html_janela = f"""
    <div style="
        width: 190px; 
        height: 190px; 
        background-color: #f9f9fa; 
        border: 2px solid #ff4b4b; 
        border-radius: 8px; 
        display: flex; 
        flex-direction: column;
        align-items: center; 
        justify-content: center; 
        text-align: center; 
        margin: 20px 0;
        padding: 10px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    ">
        <span style="color: #31333F; font-size: 14px; font-weight: 600;">Seu pedido chegará em aproximadamente</span>
        <br>
        <span style="color: #ff4b4b; font-size: 24px; font-weight: 900;">{st.session_state.tempo_estimado} min</span>
    </div>
    """
    st.markdown(html_janela, unsafe_allow_html=True)
    
    # --- 3. DADOS DE ENTREGA ---
    cliente = st.session_state.cliente
    cep_loja = "14403-374"
    cep_cliente = cliente['cep']
    
    st.markdown(f"**Endereço de Destino:** {cliente['logradouro']}, {cliente['numero']} - {cliente['bairro']}, {cliente['cidade']}/{cliente['uf']}")
    st.markdown("### Rota de Entrega (Google Maps)")
    
    url_mapa = f"https://www.google.com/maps/dir/?api=1&origin={cep_loja}&destination={cep_cliente}"
    
    st.info("Para acompanhar o trajeto detalhado do seu pedido com trânsito em tempo real, clique no botão abaixo:")
    st.link_button("🗺️ Acompanhar Rota no Google Maps", url_mapa, use_container_width=True)
    
    st.divider()
    if st.button("Fazer Novo Pedido", use_container_width=True):
        st.session_state.carrinho = []
        st.session_state.modo_checkout = False
        st.session_state.pedido_finalizado = False
        st.session_state.frete_calculado = None
        # Resetando as variáveis locais criadas
        if 'progresso_producao' in st.session_state:
            del st.session_state['progresso_producao']
        if 'tempo_estimado' in st.session_state:
            del st.session_state['tempo_estimado']
        st.rerun()