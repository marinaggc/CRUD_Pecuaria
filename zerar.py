import pg8000.dbapi

# Conectando ao banco 
conn = pg8000.dbapi.connect(host="localhost", database="pecuaria_db", user="postgres", password="capitu")
cursor = conn.cursor()

try:
    print("Iniciando a limpeza do banco de dados...")
    
    # O comando mágico que limpa tudo e zera os IDs
    comando_sql = "TRUNCATE TABLE cliente, vendedor, animal, venda, item_venda RESTART IDENTITY CASCADE;"
    cursor.execute(comando_sql)
    
    conn.commit()
    print(" Banco de dados ZERADO com sucesso! Todas as tabelas estão limpas e os IDs voltaram para 1.")
    
except Exception as e:
    print(f" Ocorreu um erro: {e}")
    conn.rollback()
finally:
    conn.close()