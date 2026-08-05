import streamlit as st
import requests
import re

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Sistema de Vendas & Delivery",
    page_icon="🧁",
    layout="wide"
)

from pagamento import renderizar_modulo_pagamento
from rastreamento import renderizar_modulo_rastreamento

PRODUTOS_CATALOGO = [
    {
        "id": 1,
        "nome": "Cupcake Red Velvet",
        "preco": 12.50,
        "descricao": "Massa aveludada de baunilha e cacau com cobertura de cream cheese artesanal.",
        "composicao": "Farinha de trigo, açúcar, manteiga, ovos, cacau em pó, extrato de baunilha, cream cheese e corante natural.",
        "alergicos": "Contém glúten, lactose, derivados de leite e ovos. Pode conter traços de nozes.",
        "imagem": "https://images.unsplash.com/photo-1587668178277-295251f900ce?w=500"
    },
    {
        "id": 2,
        "nome": "Cupcake de Chocolate Belga",
        "preco": 14.00,
        "descricao": "Massa intensa de cacau 70% recheada e coberta com ganache belga gourmet.",
        "composicao": "Cacau em pó 70%, chocolate belga ao leite, farinha de trigo, açúcar mascavo, ovos e creme de leite.",
        "alergicos": "Contém glúten, lactose, derivados de leite, ovos e soja (lecitina).",
        "imagem": "https://images.unsplash.com/photo-1576618148400-f54bed99fcfd?w=500"
    },
    {
        "id": 3,
        "nome": "Cupcake de Morango & Ninho",
        "preco": 13.50,
        "descricao": "Massa leve de baunilha com recheio de morangos frescos e cobertura de Leite Ninho.",
        "composicao": "Farinha de trigo, leite em pó (Ninho), morangos frescos, açúcar, ovos, manteiga e leite condensado.",
        "alergicos": "Contém glúten, lactose, derivados de leite e ovos.",
        "imagem": "https://images.unsplash.com/photo-1519869325930-281384150729?w=500"
    },
    {
        "id": 4,
        "nome": "Cupcake de Doce de Leite",
        "preco": 13.00,
        "descricao": "Massa fofinha de canela recheada com doce de leite cremoso e chantilly.",
        "composicao": "Farinha de trigo, doce de leite artesanal, canela em pó, açúcar, ovos, manteiga e creme de leite batido.",
        "alergicos": "Contém glúten, lactose, derivados de leite e ovos.",
        "imagem": "https://images.unsplash.com/photo-1599785209707-a456fc1337cc?w=500"
    }
]


# Functions de Formatação e Limpeza
def limpar_numeros(texto: str) -> str:
    return re.sub(r"\D", "", str(texto or ""))


def formatar_cpf(cpf_raw: str) -> str:
    nums = limpar_numeros(cpf_raw)[:11]
    if len(nums) == 11:
        return f"{nums[:3]}.{nums[3:6]}.{nums[6:9]}-{nums[9:]}"
    return nums


def formatar_cep(cep_raw: str) -> str:
    nums = limpar_numeros(cep_raw)[:8]
    if len(nums) == 8:
        return f"{nums[:5]}-{nums[5:]}"
    return nums


def formatar_telefone(ddd: str, numero: str) -> str:
    ddd_limpo = limpar_numeros(ddd)[:2]
    num_limpo = limpar_numeros(numero)[:9]
    if len(num_limpo) == 9:
        return f"({ddd_limpo}) {num_limpo[:5]}-{num_limpo[5:]}"
    elif len(num_limpo) == 8:
        return f"({ddd_limpo}) {num_limpo[:4]}-{num_limpo[4:]}"
    return f"({ddd_limpo}) {num_limpo}"


def consultar_viacep(cep_limpo: str) -> dict | None:
    """Busca os dados de endereço na API pública do ViaCEP."""
    if len(cep_limpo) == 8:
        try:
            res = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=3)
            if res.status_code == 200:
                dados = res.json()
                if "erro" not in dados:
                    return {
                        "logradouro": dados.get("logradouro", ""),
                        "bairro": dados.get("bairro", ""),
                        "cidade": dados.get("localidade", ""),
                        "uf": dados.get("uf", "")
                    }
        except Exception:
            pass
    return None


def inicializar_session_state():
    if "banco_clientes" not in st.session_state:
        st.session_state["banco_clientes"] = {
            "00000000000": {
                "nome": "Cliente Exemplo",
                "cpf": "000.000.000-00",
                "telefone": "(16) 99999-9999",
                "logradouro": "Alameda Arminda Nogueira",
                "numero": "2463",
                "complemento": "",
                "bairro": "Vila Industrial",
                "cidade": "Franca",
                "uf": "SP",
                "cep": "14403-374"
            }
        }

    estat_padrao = {
        "etapa": "verificar_cpf",
        "carrinho": [],
        "cliente": {
            "nome": "",
            "cpf": "",
            "telefone": "",
            "logradouro": "",
            "numero": "",
            "complemento": "",
            "bairro": "",
            "cidade": "",
            "uf": "",
            "cep": ""
        },
        "cad_logradouro": "",
        "cad_bairro": "",
        "cad_cidade": "Franca",
        "cad_uf": "SP",
        "modo_checkout": False,
        "pedido_finalizado": False,
        "numero_pedido": None
    }
    
    for chave, valor in estat_padrao.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


def buscar_cliente_por_cpf(cpf_limpo: str) -> dict | None:
    # 1. Busca na memória da sessão
    if cpf_limpo in st.session_state.get("banco_clientes", {}):
        return st.session_state["banco_clientes"][cpf_limpo]

    # 2. Busca no Backend
    try:
        res = requests.get(f"{API_URL}/clientes/{cpf_limpo}", timeout=2)
        if res.status_code == 200:
            dados = res.json()
            st.session_state["banco_clientes"][cpf_limpo] = dados
            return dados
    except Exception:
        pass

    return None


def renderizar_verificacao_cpf():
    st.title("👤 Identificação do Cliente")
    st.write("Digite **somente os números** do seu CPF para consultar o cadastro:")
    
    cpf_input_raw = st.text_input("CPF (Apenas números)", max_chars=11, placeholder="Ex: 00000000000")
    cpf_limpo = limpar_numeros(cpf_input_raw)
    
    if cpf_limpo:
        cpf_formatado_preview = formatar_cpf(cpf_limpo)
        st.caption(f"📌 **CPF Formatado:** `{cpf_formatado_preview}`")
    
    if st.button("Buscar Cadastro 🔍", type="primary"):
        if len(cpf_limpo) != 11:
            st.error("❌ Por favor, digite um CPF válido com exatamente 11 dígitos.")
        else:
            cliente_encontrado = buscar_cliente_por_cpf(cpf_limpo)
            if cliente_encontrado:
                st.session_state.cliente = cliente_encontrado
                st.session_state.etapa = "catalogo"
                st.toast(f"Bem-vindo(a) de volta, {cliente_encontrado.get('nome')}!", icon="👋")
                st.rerun()
            else:
                st.session_state.cliente = {"cpf": formatar_cpf(cpf_limpo), "cpf_limpo": cpf_limpo}
                st.session_state.etapa = "cadastro"
                st.info("Cadastro não encontrado. Preencha seus dados abaixo para continuar.")
                st.rerun()


def renderizar_form_cadastro():
    st.title("📝 Cadastro de Novo Cliente")
    st.write("Preencha seus dados abaixo. Após salvar, você irá direto para o cardápio:")
    
    cli = st.session_state.get("cliente", {})
    cpf_formatado = cli.get("cpf", "")
    cpf_limpo = cli.get("cpf_limpo", limpar_numeros(cpf_formatado))
    
    st.text_input("CPF", value=cpf_formatado, disabled=True)
    
    nome = st.text_input("Nome Completo*", value=cli.get("nome", ""))
    
    # Campo DDD com Parênteses Ativos e Número de Telefone
    st.write("**Telefone / WhatsApp***")
    col_parentes_open, col_ddd, col_parentes_close, col_num = st.columns([0.2, 1, 0.2, 3])
    with col_parentes_open:
        st.markdown("<h3 style='text-align: center; margin-top: 25px;'>(</h3>", unsafe_allow_html=True)
    with col_ddd:
        ddd_input = st.text_input("DDD*", max_chars=2, value="16", placeholder="16")
    with col_parentes_close:
        st.markdown("<h3 style='text-align: center; margin-top: 25px;'>)</h3>", unsafe_allow_html=True)
    with col_num:
        num_input = st.text_input("Número (Somente dígitos)*", max_chars=9, placeholder="999999999")
    
    st.divider()
    st.subheader("📍 Endereço de Entrega")
    
    # Busca Automática de CEP
    col_cep, col_btn_cep = st.columns([2, 1])
    with col_cep:
        cep_input_raw = st.text_input("CEP (Somente números)*", max_chars=8, placeholder="14403374")
    with col_btn_cep:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        btn_buscar_cep = st.button("🔍 Buscar CEP")
        
    cep_limpo = limpar_numeros(cep_input_raw)
    
    if btn_buscar_cep:
        if len(cep_limpo) == 8:
            dados_endereco = consultar_viacep(cep_limpo)
            if dados_endereco:
                st.session_state["cad_logradouro"] = dados_endereco["logradouro"]
                st.session_state["cad_bairro"] = dados_endereco["bairro"]
                st.session_state["cad_cidade"] = dados_endereco["cidade"]
                st.session_state["cad_uf"] = dados_endereco["uf"]
                st.toast("Endereço localizado com sucesso!", icon="✅")
            else:
                st.error("CEP não encontrado. Preencha os campos manualmente.")
        else:
            st.warning("Digite um CEP com 8 dígitos para realizar a busca.")

    col_rua, col_num_rua = st.columns([3, 1])
    with col_rua:
        logradouro = st.text_input("Rua / Logradouro*", value=st.session_state.get("cad_logradouro", ""))
    with col_num_rua:
        numero = st.text_input("Número*", placeholder="123")
        
    complemento = st.text_input("Complemento", placeholder="Apto, Bloco, etc.")
    
    col_bairro, col_cid, col_uf = st.columns([2, 2, 1])
    with col_bairro:
        bairro = st.text_input("Bairro*", value=st.session_state.get("cad_bairro", ""))
    with col_cid:
        cidade = st.text_input("Cidade*", value=st.session_state.get("cad_cidade", "Franca"))
    with col_uf:
        uf = st.text_input("UF*", value=st.session_state.get("cad_uf", "SP"), max_chars=2)
        
    if st.button("Salvar Cadastro e Ir para o Cardápio 🛍️", type="primary", width="stretch"):
        ddd_limpo = limpar_numeros(ddd_input)
        num_limpo = limpar_numeros(num_input)
        
        if not nome or not ddd_limpo or not num_limpo or not logradouro or not numero or not cep_limpo:
            st.error("❌ Por favor, preencha todos os campos obrigatórios (*).")
        elif len(ddd_limpo) != 2:
            st.error("❌ O DDD deve conter exatamente 2 dígitos.")
        elif len(num_limpo) < 8 or len(num_limpo) > 9:
            st.error("❌ O número de telefone deve conter 8 ou 9 dígitos.")
        else:
            telefone_formatado = formatar_telefone(ddd_limpo, num_limpo)
            cep_formatado = formatar_cep(cep_limpo)
            
            novo_cliente = {
                "nome": nome,
                "cpf": formatar_cpf(cpf_limpo),
                "telefone": telefone_formatado,
                "logradouro": logradouro,
                "numero": numero,
                "complemento": complemento,
                "bairro": bairro,
                "cidade": cidade,
                "uf": uf,
                "cep": cep_formatado
            }
            
            # Salva na sessão local e envia para API backend
            st.session_state.cliente = novo_cliente
            st.session_state["banco_clientes"][cpf_limpo] = novo_cliente
            
            try:
                requests.post(f"{API_URL}/clientes", json=novo_cliente, timeout=2)
            except Exception:
                pass
            
            # Redireciona DIRETAMENTE para o Cardápio
            st.session_state.etapa = "catalogo"
            st.toast("Cadastro realizado com sucesso! Bem-vindo(a) ao cardápio.", icon="🎉")
            st.rerun()

    if st.button("⬅️ Voltar e Consultar Outro CPF"):
        st.session_state.etapa = "verificar_cpf"
        st.rerun()


def renderizar_catalogo():
    st.title("🧁 Loja & Cardápio de Cupcakes")
    
    cli = st.session_state.get("cliente", {})
    st.info(
        f"📍 **Cliente:** {cli.get('nome')} | **CPF:** {cli.get('cpf')} | **Tel:** {cli.get('telefone')}\n\n"
        f"**Endereço de Entrega:** {cli.get('logradouro')}, {cli.get('numero')} - {cli.get('bairro')} ({cli.get('cidade')}/{cli.get('uf')}) - CEP: {cli.get('cep')}"
    )
    
    if st.button("🔄 Alterar Cliente / CPF"):
        st.session_state.etapa = "verificar_cpf"
        st.rerun()

    st.divider()
    col_prods, col_carrinho = st.columns([2, 1])
    
    with col_prods:
        st.subheader("Nosso Cardápio")
        for prod in PRODUTOS_CATALOGO:
            with st.container(border=True):
                c_img, c_detalhes = st.columns([1, 2])
                with c_img:
                    st.image(prod["imagem"], width="stretch")
                with c_detalhes:
                    st.markdown(f"### {prod['nome']}")
                    st.write(prod["descricao"])
                    
                    # Detalhes visíveis
                    st.markdown(f"🧪 **Composição Básica:** {prod['composicao']}")
                    st.markdown(f"⚠️ **Alerta de Alergênicos:** {prod['alergicos']}")
                    
                    st.markdown(f"**Preço:** R$ {prod['preco']:.2f}")
                    if st.button(f"➕ Adicionar ao Carrinho", key=f"add_{prod['id']}"):
                        st.session_state.carrinho.append(prod)
                        st.toast(f"{prod['nome']} adicionado ao carrinho!", icon="✅")
                        st.rerun()

    with col_carrinho:
        st.subheader("🛒 Seu Carrinho")
        carrinho = st.session_state.get("carrinho", [])
        
        if not carrinho:
            st.info("Seu carrinho está vazio. Adicione cupcakes ao lado.")
        else:
            subtotal = 0.0
            for idx, item in enumerate(carrinho):
                c_item, c_del = st.columns([3, 1])
                with c_item:
                    st.write(f"**{item['nome']}**")
                    st.write(f"R$ {item['preco']:.2f}")
                with c_del:
                    if st.button("🗑️", key=f"del_{idx}"):
                        st.session_state.carrinho.pop(idx)
                        st.rerun()
                subtotal += float(item['preco'])
                st.divider()
            
            st.markdown(f"### **Subtotal:** R$ {subtotal:.2f}")
            if st.button("Avançar para Checkout e Pagamento 💳", type="primary", width="stretch"):
                st.session_state.modo_checkout = True
                st.session_state.etapa = "checkout"
                st.rerun()


inicializar_session_state()

# Roteador principal por etapa
try:
    if st.session_state.get("pedido_finalizado"):
        renderizar_modulo_rastreamento()
    elif st.session_state.get("etapa") == "verificar_cpf":
        renderizar_verificacao_cpf()
    elif st.session_state.get("etapa") == "cadastro":
        renderizar_form_cadastro()
    elif st.session_state.get("etapa") == "catalogo":
        renderizar_catalogo()
    elif st.session_state.get("etapa") == "checkout" or st.session_state.get("modo_checkout"):
        renderizar_modulo_pagamento()
    else:
        renderizar_verificacao_cpf()
except Exception as e:
    st.error("❌ Ocorreu um erro ao renderizar a interface:")
    st.exception(e)