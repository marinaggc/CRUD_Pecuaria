--  Criação do Banco de Dados 
DROP DATABASE IF EXISTS pecuaria_db;
CREATE DATABASE pecuaria_db;
\c pecuaria_db;

--  TABELA DE ANIMAIS / LOTES DE ESTOQUE
CREATE TABLE animal (
    codigo VARCHAR(20) PRIMARY KEY, -- Ex: BOV-4021, SUI-9912 
    especie VARCHAR(50) NOT NULL,    
    raca VARCHAR(50) NOT NULL,       
    finalidade VARCHAR(50) NOT NULL, 
    peso_medio_kg DECIMAL(10,2),
    preco DECIMAL(10,2) NOT NULL,
    quantidade_estoque INT NOT NULL, 
    nascido_em_mari BOOLEAN DEFAULT FALSE
);

--  TABELA DE CLIENTES 
CREATE TABLE cliente (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cidade VARCHAR(100),
    time_futebol VARCHAR(50),
    assiste_one_piece BOOLEAN DEFAULT FALSE
);

--  TABELA DE VENDEDORES
CREATE TABLE vendedor (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    matricula VARCHAR(50) UNIQUE NOT NULL
);

--  TABELA DE VENDAS (A Nota Fiscal / Pedido)
CREATE TABLE venda (
    id SERIAL PRIMARY KEY,
    id_cliente INT REFERENCES cliente(id) ON DELETE CASCADE,
    id_vendedor INT REFERENCES vendedor(id) ON DELETE SET NULL,
    forma_pagamento VARCHAR(50) NOT NULL,
    status_pagamento VARCHAR(50) DEFAULT 'Aprovado', 
    valor_total DECIMAL(10,2) DEFAULT 0.00,
    data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--  TABELA DE ITENS DA VENDA (O Carrinho de Compras)
CREATE TABLE item_venda (
    id SERIAL PRIMARY KEY,
    id_venda INT REFERENCES venda(id) ON DELETE CASCADE,
    codigo_animal VARCHAR(20) REFERENCES animal(codigo) ON DELETE RESTRICT,
    quantidade INT NOT NULL,
    preco_unitario DECIMAL(10,2) NOT NULL
);

--  ÍNDICES 
CREATE INDEX idx_animal_estoque ON animal(quantidade_estoque);
CREATE INDEX idx_venda_data ON venda(data_venda);
CREATE INDEX idx_cliente_nome ON cliente(nome);

--  VIEW: Relatório Mensal de Desempenho dos Vendedores 
CREATE VIEW vw_relatorio_mensal_vendedores AS
SELECT 
    v.id AS id_vendedor, 
    v.nome AS nome_vendedor, 
    COUNT(DISTINCT vd.id) AS total_vendas, 
    COALESCE(SUM(vd.valor_total), 0) AS valor_total_vendido, 
    TO_CHAR(vd.data_venda, 'MM/YYYY') AS mes_ano
FROM vendedor v 
LEFT JOIN venda vd ON v.id = vd.id_vendedor 
GROUP BY v.id, v.nome, TO_CHAR(vd.data_venda, 'MM/YYYY');

--  STORED PROCEDURE: Processamento de Itens e Baixa de Estoque 
CREATE OR REPLACE PROCEDURE sp_inserir_item_venda(p_id_venda INT, p_codigo_animal VARCHAR, p_quantidade INT)
LANGUAGE plpgsql AS $$
DECLARE
    v_preco_unitario DECIMAL(10,2);
    v_estoque_atual INT;
BEGIN
    -- Busca o preço atual do animal e o estoque disponível
    SELECT quantidade_estoque, preco INTO v_estoque_atual, v_preco_unitario 
    FROM animal WHERE codigo = p_codigo_animal;

    -- Proteção rigorosa contra venda sem estoque no banco de dados
    IF v_estoque_atual < p_quantidade THEN 
        RAISE EXCEPTION 'Estoque insuficiente para a venda do lote %!', p_codigo_animal; 
    END IF;

    -- Insere o item no carrinho da nota fiscal
    INSERT INTO item_venda (id_venda, codigo_animal, quantidade, preco_unitario) 
    VALUES (p_id_venda, p_codigo_animal, p_quantidade, v_preco_unitario);

    -- Dá baixa automática no estoque
    UPDATE animal SET quantidade_estoque = quantidade_estoque - p_quantidade WHERE codigo = p_codigo_animal;

    -- Atualiza o valor total da venda na tabela principal
    UPDATE venda SET valor_total = valor_total + (v_preco_unitario * p_quantidade) WHERE id = p_id_venda;
END; $$;
