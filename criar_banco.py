import sqlite3

# Conecta ao banco de dados (cria o arquivo 'cupcakes.db' se não existir)
conn = sqlite3.connect('cupcakes.db')
cursor = conn.cursor()

# Executa o script SQL para estruturar o banco com tabelas de clientes e pedidos
cursor.executescript('''
    -- 1. Remove as tabelas antigas para reinicialização limpa
    DROP TABLE IF EXISTS itens_pedido;
    DROP TABLE IF EXISTS pedidos;
    DROP TABLE IF EXISTS cupcakes;
    DROP TABLE IF EXISTS clientes;

    -- 2. Tabela de cupcakes
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

    -- 3. Tabela de clientes
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

    -- 4. Tabela de pedidos
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

    -- 5. Tabela de itens vinculados aos pedidos
    CREATE TABLE itens_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_numero TEXT NOT NULL,
        cupcake_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        preco REAL NOT NULL,
        FOREIGN KEY (pedido_numero) REFERENCES pedidos(numero)
    );

    -- 6. Inserção de dados iniciais de cupcakes
    INSERT INTO cupcakes (
        nome, 
        descricao, 
        preco, 
        imagem, 
        estoque, 
        destaque, 
        ingredientes, 
        informacao_nutricional, 
        alergicos
    ) VALUES 
    (
        'Cupcake de Limão', 'Massa cítrica com merengue tostado', 8.00, 'https://via.placeholder.com/150/ccffcc/000000?text=Limao', 20, 0, 'Farinha, açúcar, suco de limão, claras em neve.', 'Porção 100g: 300kcal.', 'Contém glúten.'
    ),
    (
        'Cupcake de Chocolate', 'Massa de cacau com cobertura de ganache', 9.50, 'https://via.placeholder.com/150/4d2600/ffffff?text=Chocolate', 15, 1, 'Farinha, cacau 70%, açúcar, leite, manteiga.', 'Porção 100g: 380kcal.', 'Contém glúten e lactose.'
    ),
    (
        'Cupcake Red Velvet', 'Tradicional red velvet com cream cheese', 10.00, 'https://via.placeholder.com/150/800000/ffffff?text=Red+Velvet', 10, 1, 'Farinha, cacau, corante vermelho, cream cheese.', 'Porção 100g: 350kcal.', 'Contém glúten, lactose e ovos.'
    );
''')

conn.commit()
conn.close()

print("Banco de dados 'cupcakes.db' atualizado com tabelas de pedidos e itens!")