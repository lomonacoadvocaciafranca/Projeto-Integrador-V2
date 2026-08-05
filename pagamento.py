import streamlit as st
import requests
import uuid
import re

API_URL = "http://127.0.0.1:8000"
CEP_ORIGEM = "14403374"  # CEP Matriz Base (Franca / SP)

@st.cache_data(ttl=3600)
def calcular_frete_por_cep(cep_destino: str) -> dict:
    """
    Calcula o valor do frete e estimativa de entrega com base no CEP do cliente
    tendo como referência a origem no CEP 14.403-374.
    """
    cep_limpo = re.sub(r"\D", "", str(cep_destino or ""))
    
    if len(cep_limpo) != 8:
        return {"valor": 15.00, "prazo": "Prazo a consultar", "erro": True}

    # Regra de proximidade imediata (mesmo bairro/microregião do 14403-374)
    if cep_limpo.startswith("14403"):
        return {"valor": 5.00, "prazo": "Entrega Expressa (Mesmo Dia)", "erro": False}

    # Validação geográfica via ViaCEP API
    try:
        res = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=3)
        if res.status_code == 200 and not res.json().get("erro"):
            data = res.json()
            cidade = data.get("localidade", "")
            uf = data.get("uf", "")

            if cidade.lower() == "franca":
                return {"valor": 8.00, "prazo": "Até 1 dia útil", "erro": False}
            elif uf == "SP":
                return {"valor": 16.50, "prazo": "1 a 3 dias úteis", "erro": False}
            elif uf in ["MG", "RJ", "ES", "PR", "SC", "RS"]:
                return {"valor": 24.90, "prazo": "3 a 5 dias úteis", "erro": False}
            else:
                return {"valor": 34.90, "prazo": "5 a 8 dias úteis", "erro": False}
    except Exception:
        pass

    # Fallback determinístico offline por faixa numérica
    if cep_limpo.startswith("144"):
        return {"valor": 8.00, "prazo": "1 a 2 dias úteis", "erro": False}
    elif cep_limpo.startswith("1"):
        return {"valor": 16.50, "prazo": "2 a 4 dias úteis", "erro": False}
    
    return {"valor": 29.90, "prazo": "4 a 7 dias úteis", "erro": False}


def processar_pagamento(metodo: str):
    numero = str(uuid.uuid4()).split('-')[0].upper()
    cli = st.session_state.get('cliente', {})
    
    logradouro = cli.get('logradouro', '')
    num_res = cli.get('numero', '')
    bairro = cli.get('bairro', '')
    cidade = cli.get('cidade', '')
    uf = cli.get('uf', '')
    
    endereco_formatado = f"{logradouro}, {num_res} - {bairro} ({cidade}/{uf})"
    
    info_frete = calcular_frete_por_cep(cli.get('cep', ''))
    valor_frete = info_frete["valor"]
    
    carrinho = st.session_state.get('carrinho', [])
    subtotal = sum(float(c.get('preco', 0.0)) for c in carrinho)
    total = subtotal + valor_frete
    
    itens_payload = [
        {
            "id": int(c.get("id", 0)),
            "nome": str(c.get("nome", "")),
            "preco": float(c.get("preco", 0.0))
        } for c in carrinho
    ]
    
    payload_pedido = {
        "numero": numero,
        "cliente_cpf": str(cli.get("cpf", "")),
        "total": round(total, 2),
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
        st.error(f"Erro de conexão com o backend: {e}")


def renderizar_modulo_pagamento():
    st.title("🛒 Checkout e Pagamento")
    cli = st.session_state.get('cliente', {})
    carrinho = st.session_state.get('carrinho', [])
    
    if not carrinho:
        st.warning("Seu carrinho está vazio.")
        if st.button("Voltar à Loja"):
            st.session_state.modo_checkout = False
            st.rerun()
        return

    cep_cliente = cli.get('cep', '')
    info_frete = calcular_frete_por_cep(cep_cliente)
    valor_frete = info_frete["valor"]
    prazo_frete = info_frete["prazo"]

    col_entrega, col_pagamento = st.columns([1.5, 1])
    
    with col_entrega:
        st.subheader("1. Endereço de Entrega")
        st.info(f"**Cliente:** {cli.get('nome', '')} | **Tel:** {cli.get('telefone', '')}")
        st.write(f"**Endereço:** {cli.get('logradouro', '')}, {cli.get('numero', '')} {cli.get('complemento', '')}")
        st.write(f"**Bairro:** {cli.get('bairro', '')} | **Cidade:** {cli.get('cidade', '')}/{cli.get('uf', '')} - **CEP:** {cep_cliente}")
        
        st.divider()
        st.subheader("2. Resumo do Pedido")
        
        subtotal = sum(float(c.get('preco', 0.0)) for c in carrinho)
        total_geral = subtotal + valor_frete
        
        for c in carrinho:
            st.write(f"- {c.get('nome')} (R$ {c.get('preco', 0.0):.2f})")
            
        st.write(f"**Subtotal:** R$ {subtotal:.2f}")
        st.write(f"**Frete (Destino CEP {cep_cliente}):** R$ {valor_frete:.2f} _({prazo_frete})_")
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