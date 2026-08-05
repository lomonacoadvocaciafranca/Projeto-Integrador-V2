import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests

def buscar_endereco_por_cep(cep):
    try:
        cep_limpo = cep.replace("-", "").replace(".", "").strip()
        res = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
        if res.status_code == 200:
            dados = res.json()
            if "erro" not in dados:
                return f"{dados.get('logradouro', '')}, {dados.get('localidade', '')}, {dados.get('uf', '')}, Brasil"
    except:
        pass
    return f"{cep}, Brasil"

def obter_coordenadas(endereco):
    try:
        geolocator = Nominatim(user_agent="cupcake_store_app")
        location = geolocator.geocode(endereco)
        if location:
            return (location.latitude, location.longitude)
    except:
        pass
    return None

def calcular_frete(cep_loja, cep_cliente):
    if cep_loja.replace("-", "") == cep_cliente.replace("-", ""):
        return 1.50 # Distância mínima
        
    endereco_loja = buscar_endereco_por_cep(cep_loja)
    endereco_cliente = buscar_endereco_por_cep(cep_cliente)

    coords_loja = obter_coordenadas(endereco_loja)
    coords_cliente = obter_coordenadas(endereco_cliente)

    if coords_loja and coords_cliente:
        distancia = geodesic(coords_loja, coords_cliente).km
        return round(distancia * 1.50, 2)
    
    return 10.00 # Taxa padrão caso a geolocalização falhe

def renderizar_modulo_pagamento():
    st.title("💳 Pagamento")
    
    cliente = st.session_state.cliente
    cep_loja = "14403-374"
    cep_cliente = cliente['cep']
    
    if "frete_calculado" not in st.session_state or st.session_state.frete_calculado is None:
        with st.spinner("Calculando o frete via satélite com base no seu CEP..."):
            st.session_state.frete_calculado = calcular_frete(cep_loja, cep_cliente)
    
    frete = st.session_state.frete_calculado
    subtotal = st.session_state.valor_subtotal
    total = subtotal + frete
    
    st.write(f"**Subtotal:** R$ {subtotal:.2f}")
    st.write(f"**Frete (R$ 1,50 por km da loja):** R$ {frete:.2f}")
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