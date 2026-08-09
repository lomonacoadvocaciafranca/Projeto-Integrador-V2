import streamlit as st

def calcular_frete():
    # Taxa de entrega fixa solicitada
    return 10.00

def renderizar_modulo_pagamento():
    st.title("💳 Pagamento")
    
    if "frete_calculado" not in st.session_state or st.session_state.frete_calculado is None:
        st.session_state.frete_calculado = calcular_frete()
    
    frete = st.session_state.frete_calculado
    subtotal = st.session_state.valor_subtotal
    total = subtotal + frete
    
    st.write(f"**Subtotal:** R$ {subtotal:.2f}")
    st.write(f"**Taxa de Entrega Fixa:** R$ {frete:.2f}")
    st.markdown(f"### **Total a Pagar:** R$ {total:.2f}")

    metodo = st.radio("Selecione a Forma de Pagamento:", ["PIX", "Cartão de Crédito", "Boleto"])
    
    if st.button("Confirmar Pedido", type="primary", use_container_width=True):
        st.session_state.pedido_finalizado = True
        st.session_state.metodo_pagamento = metodo
        st.session_state.total_pago = total
        st.rerun()
    
    if st.button("Voltar ao Carrinho"):
        st.session_state.modo_checkout = False
        st.session_state.frete_calculado = None
        st.rerun()