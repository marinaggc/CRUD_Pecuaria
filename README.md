# Fazenda Tech - Gestão Pecuária Avançada

O **Fazenda Tech** é um sistema *desktop* desenvolvido em Python para a gestão completa de uma fazenda, englobando o controlo de rebanhos/lotes de animais, gestão de clientes, vendedores e um sistema de Frente de Caixa (PDV) para vendas com baixa automática de stock.

##  Funcionalidades

* **Gestão de Animais (Estoque):**
    * Registo completo (CRUD) de lotes de animais (Bovinos, Suínos, Equinos, Ovinos, Caprinos) por raça, finalidade, peso médio e preço.
    * Filtros avançados de pesquisa (por nome, espécie, preço máximo, nascidos em Mari e alerta de stock baixo).
* **Gestão de Pessoas:**
    * Cadastro de Clientes e Vendedores.
    * Consulta de histórico de compras detalhado por cliente.
* **Frente de Caixa (PDV):**
    * Sistema de carrinho de compras.
    * Garantia de integridade: Impede vendas se o stock for insuficiente (validação via Stored Procedure no banco de dados).
    * **Sistema de Descontos Dinâmicos:** Regras de negócio divertidas e automáticas (ex: 10% de desconto se o cliente for de "Sousa", +10% se for adepto do "Flamengo", +10% se assistir a "One Piece").
* **Relatórios (Dashboard):**
    * Visão geral do património estimado da fazenda.
    * Relatório mensal de vendas por vendedor gerado através de *Views* no PostgreSQL.

##  Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Interface Gráfica:** Tkinter / TTK (Natível do Python)
* **Banco de Dados:** PostgreSQL
* **Driver do Banco de Dados:** `pg8000` (biblioteca Python pura)

##  Estrutura do Projeto

* `front.py`: Contém toda a lógica da Interface Gráfica (GUI) construída com Tkinter. É o ficheiro principal para iniciar a aplicação.
* `back.py`: Contém a classe `GerenciadorCRUD`, responsável por toda a comunicação e lógica de negócio com o banco de dados PostgreSQL.
* `banco.sql`: Script DDL para a criação da base de dados, tabelas, índices, *Views* e *Stored Procedures*.
* `zerar.py`: Um script utilitário de emergência para limpar todos os dados do banco (faz *Truncate* em todas as tabelas) e reiniciar as contagens de IDs.

##  Como Configurar e Executar

### Pré-requisitos
1. Ter o **Python 3.x** instalado.
2. Ter o **PostgreSQL** instalado e a correr no seu computador local (`localhost`).

### 1. Instalar as dependências
A única biblioteca externa necessária é o conector do PostgreSQL. Abra o terminal e execute:
```bash
pip install pg8000
