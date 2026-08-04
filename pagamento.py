import streamlit as st
import requests
import uuid

API_URL = "http://127.0.0.1:8000"

def processar_pagamento(metodo):
    """Executa a chamada HTTP para gravar o pedido no backend"""
    numero = str(uuid.uuid4()).split('-')[0].upper()
    cli = st.session_state.cliente
    endereco_formatado = f"{cli['logradouro']}, {cli['numero']} - {cli['bairro']} ({cli['cidade']}/{cli['uf']})"
    taxa_entrega = 5.00
    subtotal = sum(float(c.get('preco', 0.0)) for c in st.session_state.carrinho)
    total = subtotal + taxa_entrega
    
    itens_payload = [
        {
            "id": int(c.get("id", 0)),
            "nome": str(c.get("nome", "")),
            "preco": float(c.get("preco", 0.0))
        } for c in st.session_state.carrinho
    ]
    
    payload_pedido = {
        "numero": numero,
        "cliente_cpf": str(cli["cpf"]),
        "total": total,
        "status": "Recebido",
        "endereco": endereco_formatado,
        "metodo_pagamento": metodo,
        "itens": itens_payload
    }
    
    try:
        res = requests.post(f"{API_URL}/pedidos", json=payload_pedido)
        if res.status_code == 200:
            st.session_state.pedido_finalizado = True
            st.session_state.numero_pedido = numero
            st.session_state.modo_checkout = False
            st.session_state.carrinho = []
            st.rerun()
        else:
            try:
                detalhe = res.json().get("detail", "Erro ao gravar pedido.")
            except Exception:
                detalhe = res.text
            st.error(f"Falha ao processar pedido ({res.status_code}): {detalhe}")
    except Exception as e:
        st.error(f"Erro de conexão: {e}")

def renderizar_modulo_pagamento():
    """Interface gráfica exclusiva do Checkout e Pagamento"""
    st.title("🛒 Checkout e Pagamento")
    cli = st.session_state.cliente
    
    if not st.session_state.carrinho:
        st.warning("Seu carrinho está vazio.")
        if st.button("Voltar à Loja"):
            st.session_state.modo_checkout = False
            st.rerun()
        return

    col_entrega, col_pagamento = st.columns([1.5, 1])
    
    with col_entrega:
        st.subheader("1. Endereço de Entrega")
        st.info(f"**Cliente:** {cli['nome']} | **Tel:** {cli['telefone']}")
        st.write(f"**Endereço:** {cli['logradouro']}, {cli['numero']} {cli.get('complemento', '')}")
        st.write(f"**Bairro:** {cli['bairro']} | **Cidade:** {cli['cidade']}/{cli['uf']} - **CEP:** {cli['cep']}")
        
        st.divider()
        st.subheader("2. Resumo do Pedido")
        subtotal = sum(c.get('preco', 0.0) for c in st.session_state.carrinho)
        taxa_entrega = 5.00
        total = subtotal + taxa_entrega
        
        for c in st.session_state.carrinho:
            st.write(f"- {c.get('nome')} (R$ {c.get('preco', 0.0):.2f})")
            
        st.write(f"**Subtotal:** R$ {subtotal:.2f}")
        st.write(f"**Taxa de Entrega:** R$ {taxa_entrega:.2f}")
        st.markdown(f"### **Total:** R$ {total:.2f}")
        
        if st.button("⬅️ Voltar ao Carrinho"):
            st.session_state.modo_checkout = False
            st.rerun()

    with col_pagamento:
        st.subheader("3. Forma de Pagamento")
        metodo = st.radio("Escolha a opção:", ["PIX", "Cartão de Crédito", "Cartão de Débito"])
        
        if metodo == "PIX":
            st.info("Escaneie o QR Code ou use o Copia e Cola.")
            st.image("https://via.placeholder.com/150/000000/FFFFFF?text=QR+CODE+PIX", width=150)
            st.code("00020126580014br.gov.bcb.pix0136fake-pix-key")
            
            if st.button("Simular Pagamento PIX (Aprovar)", type="primary"):
                processar_pagamento("PIX")
                
        else:
            numero_cartao = st.text_input("Número do Cartão (16 dígitos)", max_chars=16)
            c_val, c_cvv = st.columns(2)
            with c_val:
                validade = st.text_input("Validade (MM/AA)", max_chars=5)
            with c_cvv:
                cvv = st.text_input("CVV", max_chars=3)
                
            if st.button(f"Confirmar Pagamento ({metodo})", type="primary"):
                if len(numero_cartao) == 16 and numero_cartao.isdigit():
                    processar_pagamento(metodo)
                else:
                    st.error("❌ Cartão inválido. Digite 16 números.")