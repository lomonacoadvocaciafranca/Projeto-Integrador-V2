import sqlite3

def criar_banco():
    conn = sqlite3.connect('cupcakes.db')
    cursor = conn.cursor()

    cursor.executescript('''
        DROP TABLE IF EXISTS itens_pedido;
        DROP TABLE IF EXISTS pedidos;
        DROP TABLE IF EXISTS cupcakes;
        DROP TABLE IF EXISTS clientes;

        CREATE TABLE cupcakes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco REAL NOT NULL,
            imagem TEXT,
            estoque INTEGER DEFAULT 0,
            destaque INTEGER DEFAULT 0,
            ingredientes TEXT,
            informacao_nutricional TEXT,
            alergicos TEXT
        );

        CREATE TABLE clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpf TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            cep TEXT NOT NULL,
            logradouro TEXT NOT NULL,
            numero TEXT NOT NULL,
            complemento TEXT,
            bairro TEXT NOT NULL,
            cidade TEXT NOT NULL,
            uf TEXT NOT NULL
        );

        CREATE TABLE pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE NOT NULL,
            cliente_cpf TEXT NOT NULL,
            total REAL NOT NULL,
            status TEXT NOT NULL,
            endereco TEXT NOT NULL,
            metodo_pagamento TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_cpf) REFERENCES clientes(cpf)
        );

        CREATE TABLE itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_numero TEXT NOT NULL,
            cupcake_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            FOREIGN KEY (pedido_numero) REFERENCES pedidos(numero)
        );

        -- Cadastro inicial salvo conforme solicitado
        INSERT INTO clientes (cpf, nome, telefone, cep, logradouro, numero, complemento, bairro, cidade, uf) 
        VALUES ('12345678909', 'Jovem', '16999999999', '14403-374', 'Rua Exemplo', '100', '', 'Centro', 'Franca', 'SP');

        INSERT INTO cupcakes (
            nome, descricao, preco, imagem, estoque, destaque, ingredientes, informacao_nutricional, alergicos
        ) VALUES 
        (
            'Cupcake de Limão', 'Massa cítrica com merengue tostado', 8.00, 'https://images.unsplash.com/photo-1550617931-e17a7b70dce2?auto=format&fit=crop&w=400&q=80', 20, 0, 'Farinha, açúcar, suco de limão, claras em neve.', 'Porção 100g: 300kcal.', 'Contém glúten.'
        ),
        (
            'Cupcake de Chocolate', 'Massa de cacau com cobertura de ganache', 9.50, 'https://images.unsplash.com/photo-1614707267537-b85aaf00c4b7?auto=format&fit=crop&w=400&q=80', 15, 1, 'Farinha, cacau 70%, açúcar, leite, manteiga.', 'Porção 100g: 380kcal.', 'Contém glúten e lactose.'
        ),
        (
            'Cupcake Red Velvet', 'Tradicional red velvet com cream cheese', 10.00, 'https://images.unsplash.com/photo-1616541823729-00fe0aacd32c?auto=format&fit=crop&w=400&q=80', 10, 1, 'Farinha, cacau, corante vermelho, cream cheese.', 'Porção 100g: 350kcal.', 'Contém glúten, lactose e ovos.'
        );
    ''')

    conn.commit()
    conn.close()
    print("Banco de dados 'cupcakes.db' criado com sucesso (cadastro inicial salvo)!")

if __name__ == '__main__':
    criar_banco()
    