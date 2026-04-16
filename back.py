import pg8000.dbapi
from pg8000.dbapi import Error
import random

class GerenciadorCRUD:
    def __init__(self):
        self.host = "localhost"
        self.database = "pecuaria_db"
        self.user = "postgres"
        self.password = "capitu"  
        self.connection = None
        self.garantir_coluna_status() # Atualiza o banco automaticamente se precisar

    def conectar(self):
        try:
            self.connection = pg8000.dbapi.connect(host=self.host, database=self.database, user=self.user, password=self.password)
            return True
        except Error as e:
            return False

    def desconectar(self):
        if self.connection:
            self.connection.close()

    def garantir_coluna_status(self):
        """Adiciona a coluna de status na tabela de vendas caso não exista (Exigência do PDF)"""
        if self.conectar():
            try:
                cursor = self.connection.cursor()
                cursor.execute("ALTER TABLE venda ADD COLUMN IF NOT EXISTS status_pagamento VARCHAR(50) DEFAULT 'Aprovado';")
                self.connection.commit()
            except Error:
                self.connection.rollback()
            finally:
                self.desconectar()

    # --- ANIMAIS  ---
    def listar_animais(self, filtro_baixo=False, especie="Todas", busca_nome="", preco_max="", filtro_mari=False):
        if self.conectar():
            try:
                cursor = self.connection.cursor()
                query = "SELECT * FROM animal WHERE 1=1 "
                params = []
                
                if filtro_baixo:
                    query += "AND quantidade_estoque < 5 AND quantidade_estoque > 0 "
                if especie != "Todas":
                    query += "AND especie = %s "
                    params.append(especie)
                if busca_nome:
                    query += "AND (codigo ILIKE %s OR raca ILIKE %s) "
                    params.append(f"%{busca_nome}%")
                if preco_max:
                    try:
                        query += "AND preco <= %s "
                        params.append(float(preco_max))
                    except ValueError: pass 
                if filtro_mari:
                    query += "AND nascido_em_mari = TRUE "

                query += "ORDER BY codigo;"
                cursor.execute(query, tuple(params))
                return cursor.fetchall()
            finally:
                self.desconectar()
        return []

    def inserir_animal(self, especie, raca, finalidade, peso, preco, qtd, nascido_mari):
        codigo = f"{especie[:3].upper()}-{random.randint(1000, 9999)}"
        if self.conectar():
            try:
                cursor = self.connection.cursor()
                cursor.execute("INSERT INTO animal (codigo, especie, raca, finalidade, peso_medio_kg, preco, quantidade_estoque, nascido_em_mari) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                               (codigo, especie, raca, finalidade, peso, preco, qtd, nascido_mari))
                self.connection.commit()
                return codigo 
            finally:
                self.desconectar()
        return None

    def alterar_animal(self, codigo, especie, raca, finalidade, peso, preco, qtd, nascido_mari):
        if self.conectar():
            try:
                cursor = self.connection.cursor()
                cursor.execute("UPDATE animal SET especie=%s, raca=%s, finalidade=%s, peso_medio_kg=%s, preco=%s, quantidade_estoque=%s, nascido_em_mari=%s WHERE codigo=%s", 
                               (especie, raca, finalidade, peso, preco, qtd, nascido_mari, codigo))
                self.connection.commit()
                return True
            except Error: return False
            finally: self.desconectar()

    def remover_animal(self, codigo):
        if self.conectar():
            try:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM animal WHERE codigo=%s", (codigo,))
                self.connection.commit()
                return True
            except Error: return False
            finally: self.desconectar()

    # --- CLIENTES E VENDEDORES ---
    def listar_clientes(self):
        if self.conectar():
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT * FROM cliente ORDER BY id;")
                return cursor.fetchall()
            finally: self.desconectar()
        return [] 
    def buscar_cliente(self, id_cliente):
        """Busca os dados cadastrais de um cliente específico"""
        if self.conectar():
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT nome, cidade, time_futebol, assiste_one_piece FROM cliente WHERE id = %s", (id_cliente,))
                return cursor.fetchone()
            finally: self.desconectar()
        return None 

    def inserir_cliente(self, nome, cidade, time, assiste_op):
        if self.conectar():
            try:
                cursor = self.connection.cursor()
                cursor.execute("INSERT INTO cliente (nome, cidade, time_futebol, assiste_one_piece) VALUES (%s, %s, %s, %s)", (nome, cidade, time, assiste_op))
                self.connection.commit()
                return True
            finally: self.desconectar()
        return False

    def listar_vendedores(self):
        if self.conectar():
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT * FROM vendedor ORDER BY id;")
                return cursor.fetchall()
            finally: self.desconectar()
        return []

    def inserir_vendedor(self, nome, matricula):
        if self.conectar():
            try:
                cursor = self.connection.cursor()
                cursor.execute("INSERT INTO vendedor (nome, matricula) VALUES (%s, %s)", (nome, matricula))
                self.connection.commit()
                return True
            finally: self.desconectar()
        return False

    def historico_cliente(self, id_cliente):
        """Busca as compras feitas por um cliente específico"""
        if self.conectar():
            try:
                cursor = self.connection.cursor()
                cursor.execute("""
                    SELECT id, TO_CHAR(data_venda, 'DD/MM/YYYY HH24:MI'), valor_total, forma_pagamento, status_pagamento 
                    FROM venda WHERE id_cliente = %s ORDER BY data_venda DESC;
                """, (id_cliente,))
                return cursor.fetchall()
            finally: self.desconectar()
        return []

    # --- SISTEMA DE VENDAS ---
    def criar_venda(self, id_cliente, id_vendedor, forma_pagamento, status_pagamento):
        if self.conectar():
            try:
                cursor = self.connection.cursor()
                cursor.execute("INSERT INTO venda (id_cliente, id_vendedor, forma_pagamento, status_pagamento) VALUES (%s, %s, %s, %s) RETURNING id;", 
                               (id_cliente, id_vendedor, forma_pagamento, status_pagamento))
                id_venda = cursor.fetchone()[0]
                self.connection.commit()
                return id_venda
            finally: self.desconectar()
        return None

    def adicionar_item(self, id_venda, codigo_animal, quantidade):
        if self.conectar():
            try:
                cursor = self.connection.cursor()
                cursor.execute("CALL sp_inserir_item_venda(%s, %s, %s)", (id_venda, codigo_animal, quantidade))
                self.connection.commit()
                return True
            except Error:
                self.connection.rollback()
                return False
            finally: self.desconectar()
    def obter_desconto_cliente(self, id_cliente):
        """Retorna o valor percentual de desconto de um cliente (ex: 0.10, 0.20)"""
        if self.conectar():
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT cidade, time_futebol, assiste_one_piece FROM cliente WHERE id = %s", (id_cliente,))
                cli = cursor.fetchone()
                if not cli: return 0.0
                
                desc = 0.0
                if cli[0] and cli[0].lower() == 'sousa': desc += 0.10
                if cli[1] and cli[1].lower() == 'flamengo': desc += 0.10
                if cli[2]: desc += 0.10
                
                return desc
            finally: 
                self.desconectar()
        return 0.0

    def aplicar_desconto(self, id_venda, id_cliente):
        if self.conectar():
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT cidade, time_futebol, assiste_one_piece FROM cliente WHERE id = %s", (id_cliente,))
                cli = cursor.fetchone()
                if not cli: return
                
                desc = 0.0
                if cli[0] and cli[0].lower() == 'sousa': desc += 0.10
                if cli[1] and cli[1].lower() == 'flamengo': desc += 0.10
                if cli[2]: desc += 0.10
                
                if desc > 0:
                    cursor.execute("UPDATE venda SET valor_total = valor_total - (valor_total * %s) WHERE id = %s", (desc, id_venda))
                    self.connection.commit()
            finally: self.desconectar()

    def relatorio_vendedores(self):
        if self.conectar():
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT * FROM vw_relatorio_mensal_vendedores;")
                return cursor.fetchall()
            finally: self.desconectar()
        return [] 
    
    def resumo_geral(self):
        """Busca os totais de Estoque e Clientes para o painel de Resumo"""
        if self.conectar():
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT COUNT(codigo), COALESCE(SUM(quantidade_estoque), 0), COALESCE(SUM(preco * quantidade_estoque), 0) FROM animal;")
                estoque = cursor.fetchone()
                cursor.execute("SELECT COUNT(id) FROM cliente;")
                clientes = cursor.fetchone()
                
                return {
                    "total_lotes": estoque[0],
                    "total_cabecas": estoque[1],
                    "valor_patrimonio": estoque[2],
                    "total_clientes": clientes[0]
                }
            finally:
                self.desconectar()

        return {"total_lotes": 0, "total_cabecas": 0, "valor_patrimonio": 0.0, "total_clientes": 0}