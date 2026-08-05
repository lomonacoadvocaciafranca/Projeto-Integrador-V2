from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3

app = FastAPI(title="API Loja de Cupcakes")
DB_FILE = 'cupcakes.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

class Cliente(BaseModel):
    cpf: str
    nome: str
    telefone: str
    cep: str
    logradouro: str
    numero: str
    complemento: Optional[str] = ""
    bairro: str
    cidade: str
    uf: str

class ItemPedido(BaseModel):
    id: int
    nome: str
    preco: float

class Pedido(BaseModel):
    numero: str
    cliente_cpf: str
    total: float
    status: str
    endereco: str
    metodo_pagamento: str
    itens: List[ItemPedido]

class StatusUpdate(BaseModel):
    status: str

@app.get("/clientes/{cpf}")
def get_cliente(cpf: str):
    conn = get_db_connection()
    cliente = conn.execute("SELECT * FROM clientes WHERE cpf = ?", (cpf,)).fetchone()
    conn.close()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return dict(cliente)

@app.post("/clientes")
def create_cliente(cliente: Cliente):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO clientes (cpf, nome, telefone, cep, logradouro, numero, complemento, bairro, cidade, uf)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cliente.cpf, cliente.nome, cliente.telefone, cliente.cep, cliente.logradouro, 
              cliente.numero, cliente.complemento, cliente.bairro, cliente.cidade, cliente.uf))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"CPF já cadastrado ou erro: {str(e)}")
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    conn.close()
    return {"message": "Cliente cadastrado com sucesso"}

@app.get("/cupcakes")
def get_cupcakes():
    conn = get_db_connection()
    cupcakes = conn.execute("SELECT * FROM cupcakes").fetchall()
    conn.close()
    return [dict(cupcake) for cupcake in cupcakes]

@app.post("/pedidos")
def create_pedido(pedido: Pedido):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO pedidos (numero, cliente_cpf, total, status, endereco, metodo_pagamento)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (pedido.numero, pedido.cliente_cpf, pedido.total, pedido.status, pedido.endereco, pedido.metodo_pagamento))
        
        for item in pedido.itens:
            cursor.execute('''
                INSERT INTO itens_pedido (pedido_numero, cupcake_id, nome, preco)
                VALUES (?, ?, ?, ?)
            ''', (pedido.numero, item.id, item.nome, item.preco))
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=400, detail=f"Erro ao gravar pedido: {str(e)}")
    
    conn.close()
    return {"message": "Pedido criado com sucesso"}

@app.get("/pedidos/cliente/{cpf}")
def get_pedidos_cliente(cpf: str):
    conn = get_db_connection()
    pedidos = conn.execute("SELECT * FROM pedidos WHERE cliente_cpf = ? ORDER BY data_criacao DESC", (cpf,)).fetchall()
    conn.close()
    return [dict(pedido) for pedido in pedidos]

@app.put("/pedidos/{numero}/status")
def update_status_pedido(numero: str, status_update: StatusUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE pedidos SET status = ? WHERE numero = ?", (status_update.status, numero))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    conn.commit()
    conn.close()
    return {"message": "Status atualizado com sucesso"}