import streamlit as st
import requests
import time
from pagamento import renderizar_modulo_pagamento
from rastreamento import renderizar_modulo_rastreamento

st.set_page_config(page_title="Loja de Cupcakes", page_icon="🧁", layout="wide")

# Inicialização de variáveis de sessão
for key, default in [
    ("cliente", None),
    ("cupcake_selecionado", None),
    ("carrinho", []),
    ("modo_checkout", False),
    ("pedido_finalizado", False),
    ("numero_pedido", None),
    ("form_logradouro", ""),
    ("form_bairro", ""),
    ("form_cidade", ""),
    ("form_uf", "")
]:
    if key not in st.session_state:
        st.session_state[key] = default

API_URL = "http://127.0.0.1:8000"

def buscar_cep(cep):
    try:
        cep_limpo = cep.replace("-", "").replace(".", "").strip()
        if len(cep_limpo) == 8:
            res = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
            if res.status_code == 200 and "erro" not in res.json():
                return res.json()
    except Exception:
        pass
    return None

def preencher_endereco_por_cep():
    dados = buscar_cep(st.session_state.get("input_cep", ""))
    if dados:
        st.session_state["form_logradouro"] = dados.get("logradouro", "")
        st.session_state["form_bairro"] = dados.get("bairro", "")
        st.session_state["form_cidade"] = dados.get("localidade", "")
        st.session_state["form_uf"] = dados.get("uf", "")

# 1. ROTEAMENTO: CADASTRO/LOGIN
if st.session_state.cliente is None:
    st.title("👋 Bem-vindo à Loja de Cupcakes!")
    col_cpf, col_btn = st.columns([3, 1])
    with col_cpf:
        cpf_input = st.text_input("Informe seu CPF", max_chars=11, key="cpf_busca")
    with col_btn:
        st.write(" ")
        st.write(" ")
        if st.button("Buscar Cadastro", use_container_width=True):
            if len(cpf_input) == 11:
                try:
                    res = requests.get(f"{API_URL}/clientes/{cpf_input}")
                    if res.status_code == 200:
                        st.session_state.cliente = res.json()
                        st.rerun()
                except Exception:
                    st.error("Erro na busca.")

    st.divider()
    st.markdown("### Novo Cadastro")
    c1, c2 = st.columns(2)
    with c1:
        nome = st.text_input("Nome Completo*")
        telefone = st.text_input("Telefone*")
    with c2:
        cep = st.text_input("CEP*", max_chars=9, key="input_cep", on_change=preencher_endereco_por_cep)
        
    c_log, c_num, c_comp = st.columns([2, 1, 1])
    with c_log:
        logradouro = st.text_input("Logradouro*", key="form_logradouro")
    with c_num:
        numero = st.text_input("Número*")
    with c_comp:
        complemento = st.text_input("Complemento")

    c_bair, c_cid, c_uf = st.columns([2, 2, 1])
    with c_bair:
        bairro = st.text_input("Bairro*", key="form_bairro")
    with c_cid:
        cidade = st.text_input("Cidade*", key="form_cidade")
    with c_uf:
        uf = st.text_input("UF*", max_chars=2, key="form_uf")

    if st.button("Salvar e Entrar", type="primary"):
        payload = {
            "cpf": cpf_input, "nome": nome, "telefone": telefone,
            "cep": cep, "logradouro": logradouro, "numero": numero,
            "complemento": complemento, "bairro": bairro, "cidade": cidade, "uf": uf
        }
        try:
            res = requests.post(f"{API_URL}/clientes", json=payload)
            if res.status_code == 200:
                st.session_state.cliente = payload
                st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")
    st.stop()

# 2. ROTEAMENTO: MÓDULO DE RASTREAMENTO
if st.session_state.pedido_finalizado:
    renderizar_modulo_rastreamento()
    st.stop()

# 3. ROTEAMENTO: MÓDULO DE PAGAMENTO
if st.session_state.modo_checkout:
    renderizar_modulo_pagamento()
    st.stop()

# 4. TELA PRINCIPAL DA LOJA (VITRINE)
col_h, col_u = st.columns([3, 1])
with col_h:
    st.title("🧁 Loja de Cupcakes")
with col_u:
    st.write(f"👤 **{st.session_state.cliente['nome']}**")
    if st.button("Sair"):
        st.session_state.cliente = None
        st.rerun()

aba_loja, aba_pedidos = st.tabs(["🧁 Vitrine", "📦 Meus Pedidos"])

with aba_loja:
    try:
        res = requests.get(f"{API_URL}/cupcakes")
        cupcakes = res.json() if res.status_code == 200 else []
    except Exception:
        cupcakes = []

    c_vit, c_det = st.columns([2, 1])
    with c_vit:
        for item in cupcakes:
            st.markdown(f"### {item.get('nome')}")
            st.write(f"Preço: R$ {item.get('preco'):.2f}")
            b1, b2 = st.columns(2)
            with b1:
                if st.button("👁️ Detalhes", key=f"d_{item.get('id')}"):
                    st.session_state.cupcake_selecionado = item
                    st.rerun()
            with b2:
                if st.button("🛒 Adicionar", key=f"a_{item.get('id')}"):
                    st.session_state.carrinho.append(item)
                    st.toast("Item adicionado!")
            st.divider()

    with c_det:
        if st.session_state.cupcake_selecionado:
            item = st.session_state.cupcake_selecionado
            st.markdown(f"### 🔍 {item.get('nome')}")
            st.write(f"**Ingredientes:** {item.get('ingredientes', 'N/A')}")
            st.write(f"**Alérgicos:** {item.get('alergicos', 'Nenhum')}")
            if st.button("❌ Fechar Detalhes"):
                st.session_state.cupcake_selecionado = None
                st.rerun()
            st.divider()

        st.subheader("🛒 Carrinho")
        if st.session_state.carrinho:
            subt = sum(c.get('preco', 0.0) for c in st.session_state.carrinho)
            for c in st.session_state.carrinho:
                st.write(f"- {c.get('nome')} (R$ {c.get('preco'):.2f})")
            st.write(f"**Subtotal:** R$ {subt:.2f}")
            if st.button("💳 Ir para o Pagamento", type="primary"):
                st.session_state.modo_checkout = True
                st.rerun()
        else:
            st.info("Carrinho vazio.")

with aba_pedidos:
    st.title("📦 Meus Pedidos")
    try:
        res_p = requests.get(f"{API_URL}/pedidos/cliente/{st.session_state.cliente['cpf']}")
        if res_p.status_code == 200:
            for p in res_p.json():
                with st.expander(f"Pedido #{p['numero']} - {p['status']} (R$ {p['total']:.2f})"):
                    st.write(f"Entrega: {p['endereco']}")
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")