import pytest
from fastapi.testclient import TestClient
import sqlite3
import os
import time

# Importa a instância do FastAPI do seu arquivo principal
import backend  

client = TestClient(backend.app)
TEST_DB_FILE = 'test_cupcakes.db'

@pytest.fixture(autouse=True)
def setup_banco_teste():
    """
    Fixture que roda antes de cada teste.
    Ela altera o arquivo do banco para um DB temporário de teste e cria as tabelas de forma limpa.
    """
    # Redireciona o banco do backend para o banco de testes
    backend.DB_FILE = TEST_DB_FILE
    
    conn = sqlite3.connect(TEST_DB_FILE)
    cursor = conn.cursor()
    
    # Recriando a estrutura básica para testes (limpando tabelas antigas se existirem)
    cursor.executescript('''
        DROP TABLE IF EXISTS itens_pedido;
        DROP TABLE IF EXISTS pedidos;
        DROP TABLE IF EXISTS clientes;
        DROP TABLE IF EXISTS cupcakes;
    
        CREATE TABLE cupcakes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, preco REAL NOT NULL);
        CREATE TABLE clientes (cpf TEXT UNIQUE NOT NULL, nome TEXT NOT NULL, telefone TEXT NOT NULL, cep TEXT NOT NULL, logradouro TEXT NOT NULL, numero TEXT NOT NULL, complemento TEXT, bairro TEXT NOT NULL, cidade TEXT NOT NULL, uf TEXT NOT NULL);
        CREATE TABLE pedidos (numero TEXT UNIQUE NOT NULL, cliente_cpf TEXT NOT NULL, total REAL NOT NULL, status TEXT NOT NULL, endereco TEXT NOT NULL, metodo_pagamento TEXT NOT NULL, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE itens_pedido (pedido_numero TEXT NOT NULL, cupcake_id INTEGER NOT NULL, nome TEXT NOT NULL, preco REAL NOT NULL);
        
        -- Inserindo um cupcake de teste
        INSERT INTO cupcakes (nome, preco) VALUES ('Cupcake de Teste Integridade', 12.50);
    ''')
    conn.commit()
    conn.close()

    yield  # Aqui os testes são executados

    # Limpa o banco de dados de teste após a execução com tolerância para o Windows
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except PermissionError:
            # Tenta novamente após um breve intervalo para dar tempo do Windows liberar o arquivo
            time.sleep(0.5)
            try:
                os.remove(TEST_DB_FILE)
            except PermissionError:
                pass # Se continuar bloqueado, ignora, pois o DROP TABLE cuidará da limpeza no próximo teste

def test_integridade_cliente():
    """Testa a criação de um cliente e a busca no banco."""
    payload_cliente = {
        "cpf": "00011122233", "nome": "Cliente de Teste", "telefone": "16999999999",
        "cep": "14400-000", "logradouro": "Rua Teste", "numero": "123",
        "complemento": "", "bairro": "Centro", "cidade": "Franca", "uf": "SP"
    }
    
    # 1. Testa a Rota POST (Criação)
    res_post = client.post("/clientes", json=payload_cliente)
    assert res_post.status_code == 200
    assert res_post.json()["message"] == "Cliente cadastrado com sucesso"
    
    # 2. Testa a Rota GET (Leitura e persistência no banco)
    res_get = client.get("/clientes/00011122233")
    assert res_get.status_code == 200
    assert res_get.json()["nome"] == "Cliente de Teste"

def test_integridade_cupcakes():
    """Testa se a vitrine consegue puxar os cupcakes do banco."""
    res = client.get("/cupcakes")
    assert res.status_code == 200
    dados = res.json()
    assert len(dados) == 1
    assert dados[0]["nome"] == "Cupcake de Teste Integridade"

def test_integridade_fluxo_pedidos():
    """Testa o ciclo de vida completo de um pedido: Criar cliente -> Fazer Pedido -> Atualizar Status."""
    
    # 1. Cadastra o cliente que fará o pedido
    client.post("/clientes", json={
        "cpf": "99988877766", "nome": "Comprador", "telefone": "00", "cep": "00", 
        "logradouro": "X", "numero": "1", "bairro": "Y", "cidade": "Z", "uf": "SP"
    })
    
    # 2. Cria o pedido
    payload_pedido = {
        "numero": "PED-999", 
        "cliente_cpf": "99988877766", 
        "total": 12.50,
        "status": "Recebido", 
        "endereco": "Rua X, 1 - Centro", 
        "metodo_pagamento": "PIX",
        "itens": [{"id": 1, "nome": "Cupcake de Teste Integridade", "preco": 12.50}]
    }
    res_post_pedido = client.post("/pedidos", json=payload_pedido)
    assert res_post_pedido.status_code == 200
    
    # 3. Atualiza o status do pedido (Simulando o andamento da produção)
    res_put_status = client.put("/pedidos/PED-999/status", json={"status": "Preparando a massa"})
    assert res_put_status.status_code == 200
    
    # 4. Verifica se o pedido do cliente foi atualizado corretamente no banco
    res_get_pedidos = client.get("/pedidos/cliente/99988877766")
    assert res_get_pedidos.status_code == 200
    pedidos = res_get_pedidos.json()
    assert len(pedidos) == 1
    assert pedidos[0]["numero"] == "PED-999"
    assert pedidos[0]["status"] == "Preparando a massa"