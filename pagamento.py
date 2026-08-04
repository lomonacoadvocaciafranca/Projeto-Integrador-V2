import streamlit as st
import requests
import uuid

API_URL = "http://127.0.0.1:8000"
VALOR_FRETE = 5.00  # Taxa fixa de frete definida

def processar_pagamento(metodo):
    numero = str(uuid.uuid4()).split('-')[0].upper()
    cli = st.session_state.cliente
    endereco_formatado = f"{cli['logradouro']}, {cli['numero']} - {cli['bairro']} ({cli['cidade']}/{cli['uf']})"
    
    # 1. Calcula o subtotal dos produtos no carrinho
    subtotal = sum(float(c.get('preco', 0.0)) for c in st.session_state.carrinho)
    
    # 2. Soma o frete obrigatoriamente para obter o total geral correto
    total = subtotal + VALOR_FRETE
    
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
        "total": total,  # Envia o valor total correto já com o frete incluso
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
            detalhe = res.json().get("detail", "Erro ao gravar pedido.")
            st.error(f"Falha ({res.status_code}): {detalhe}")
    except Exception as e:
        st.error(f"Erro de conexão: {e}")

def renderizar_modulo_pagamento():
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
        
        # Garante a exibição visual correta do frete na tela de pagamento
        subtotal = sum(float(c.get('preco', 0.0)) for c in st.session_state.carrinho)
        total_geral = subtotal + VALOR_FRETE
        
        for c in st.session_state.carrinho:
            st.write(f"- {c.get('nome')} (R$ {c.get('preco', 0.0):.2f})")
            
        st.write(f"**Subtotal:** R$ {subtotal:.2f}")
        st.write(f"**Taxa de Entrega (Frete):** R$ {VALOR_FRETE:.2f}")
        st.markdown(f"### **Total Geral:** R$ {total_geral:.2f}")
        
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
