import tkinter as tk
from tkinter import ttk, messagebox
from back import GerenciadorCRUD

class AppPecuaria:
    def __init__(self, root):
        self.root = root
        self.root.title("Fazenda Tech - Gestão Pecuária Avançada")
        self.root.geometry("1100x750")
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'), background="#2E7D32", foreground="white")

        self.db = GerenciadorCRUD()
        self.carrinho = [] 
        self.codigo_em_edicao = None 

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_animais = ttk.Frame(self.notebook)
        self.tab_pessoas = ttk.Frame(self.notebook)
        self.tab_pdv = ttk.Frame(self.notebook)
        self.tab_relatorios = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_animais, text=" Animais (CRUD Completo)")
        self.notebook.add(self.tab_pessoas, text=" Clientes & Histórico")
        self.notebook.add(self.tab_pdv, text=" PDV (Vendas)")
        self.notebook.add(self.tab_relatorios, text=" Relatórios (VIEW)")

        self.racas_por_especie = {
            "Bovino": ["Nelore", "Angus", "Brahman", "Senepol", "Gir Leiteiro"],
            "Suíno": ["Landrace", "Large White", "Duroc", "Pietrain"],
            "Equino": ["Mangalarga", "Quarto de Milha", "Crioulo", "Campolina"],
            "Ovino": ["Santa Inês", "Dorper", "Suffolk"],
            "Caprino": ["Boer", "Saanen", "Anglo-Nubiano"]
        }

        self.criar_aba_animais()
        self.criar_aba_pessoas()
        self.criar_aba_pdv()
        self.criar_aba_relatorios()

        self.carregar_dados()

    # --- ABA 1: ANIMAIS ---
    def criar_aba_animais(self):
        self.frame_form = ttk.LabelFrame(self.tab_animais, text="Formulário de Lote / Animal", padding=10)
        self.frame_form.pack(fill="x", padx=10, pady=5)

        ttk.Label(self.frame_form, text="Espécie:").grid(row=0, column=0, sticky="w", padx=5)
        self.e_especie = ttk.Combobox(self.frame_form, values=list(self.racas_por_especie.keys()), state="readonly")
        self.e_especie.grid(row=0, column=1, padx=5, pady=5)
        self.e_especie.bind("<<ComboboxSelected>>", self.atualizar_dropdown_racas)

        ttk.Label(self.frame_form, text="Raça:").grid(row=0, column=2, sticky="w", padx=5)
        self.e_raca = ttk.Combobox(self.frame_form, state="readonly")
        self.e_raca.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(self.frame_form, text="Finalidade:").grid(row=1, column=0, sticky="w", padx=5)
        self.e_finalidade = ttk.Combobox(self.frame_form, values=["Abate", "Leite", "Reprodução", "Montaria", "Genética"], state="readonly")
        self.e_finalidade.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.frame_form, text="Peso Médio (Kg):").grid(row=1, column=2, sticky="w", padx=5)
        self.e_peso = ttk.Entry(self.frame_form)
        self.e_peso.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(self.frame_form, text="Preço/Cabeça (R$):").grid(row=2, column=0, sticky="w", padx=5)
        self.e_preco = ttk.Entry(self.frame_form)
        self.e_preco.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.frame_form, text="Qtd Cabeças:").grid(row=2, column=2, sticky="w", padx=5)
        self.e_qtd = ttk.Entry(self.frame_form)
        self.e_qtd.grid(row=2, column=3, padx=5, pady=5)
        self.e_mari = tk.BooleanVar()
        ttk.Checkbutton(self.frame_form, text="Nascido em Mari?", variable=self.e_mari).grid(row=2, column=4, padx=5, sticky="w")
       
        self.btn_salvar = ttk.Button(self.frame_form, text="Salvar Novo Animal", command=self.salvar_animal)
        self.btn_salvar.grid(row=3, column=0, columnspan=4, pady=10)

        # Filtros e Pesquisa
        frame_filtros = ttk.LabelFrame(self.tab_animais, text="Pesquisa e Filtros Avançados", padding=5)
        frame_filtros.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame_filtros, text="Nome/Código:").pack(side="left", padx=5)
        self.f_nome = ttk.Entry(frame_filtros, width=15)
        self.f_nome.pack(side="left", padx=5)

        ttk.Label(frame_filtros, text="Preço Máx:").pack(side="left", padx=5)
        self.f_preco = ttk.Entry(frame_filtros, width=10)
        self.f_preco.pack(side="left", padx=5)

        ttk.Label(frame_filtros, text="Espécie:").pack(side="left", padx=5)
        self.filtro_especie = ttk.Combobox(frame_filtros, values=["Todas"] + list(self.racas_por_especie.keys()), state="readonly", width=12)
        self.filtro_especie.set("Todas")
        self.filtro_especie.pack(side="left", padx=5) 
        self.f_mari = tk.BooleanVar()
        ttk.Checkbutton(frame_filtros, text="📍 Apenas de Mari", variable=self.f_mari).pack(side="left", padx=5)

        ttk.Button(frame_filtros, text="🔍 Buscar", command=self.carregar_animais).pack(side="left", padx=5)
        ttk.Button(frame_filtros, text="🚨 Ver Estoque Baixo", command=lambda: self.carregar_animais(baixo_estoque=True)).pack(side="right", padx=5)

        # Tabela (Height ajustado para 5 para caber no ecrã)
        colunas = ("Código/Lote", "Espécie", "Raça", "Finalidade", "Peso(Kg)", "Preço(Cab)", "Qtd Cabeças", "Nascido em Mari", "Status")
        self.tree_animais = ttk.Treeview(self.tab_animais, columns=colunas, show="headings", height=5)
        
        self.tree_animais.column("Código/Lote", width=100, anchor="center")
        self.tree_animais.column("Espécie", width=100)
        self.tree_animais.column("Raça", width=120)
        self.tree_animais.column("Finalidade", width=100)
        self.tree_animais.column("Peso(Kg)", width=80, anchor="center")
        self.tree_animais.column("Preço(Cab)", width=100, anchor="center")
        self.tree_animais.column("Qtd Cabeças", width=100, anchor="center") 
        self.tree_animais.column("Status", width=150, anchor="center")

        for col in colunas: self.tree_animais.heading(col, text=col)
        self.tree_animais.pack(fill="both", expand=True, padx=10, pady=5)

        frame_acoes = ttk.Frame(self.tab_animais)
        frame_acoes.pack(fill="x", padx=10, pady=5)
        ttk.Button(frame_acoes, text="✏️ Editar Selecionado", command=self.carregar_edicao).pack(side="left", padx=5)
        ttk.Button(frame_acoes, text="🗑️ Excluir Selecionado", command=self.excluir_animal).pack(side="left", padx=5)
        ttk.Button(frame_acoes, text="❌ Cancelar Edição", command=self.limpar_formulario).pack(side="left", padx=20)

    def atualizar_dropdown_racas(self, event):
        especie_selecionada = self.e_especie.get()
        if especie_selecionada in self.racas_por_especie:
            self.e_raca['values'] = self.racas_por_especie[especie_selecionada]
            self.e_raca.set('')

    def salvar_animal(self):
        try:
            esp = self.e_especie.get(); rac = self.e_raca.get(); fin = self.e_finalidade.get()
            pes = float(self.e_peso.get()); pre = float(self.e_preco.get()); qtd = int(self.e_qtd.get())
            mari = self.e_mari.get() 

            if self.codigo_em_edicao:
                if self.db.alterar_animal(self.codigo_em_edicao, esp, rac, fin, pes, pre, qtd, mari):
                    messagebox.showinfo("Sucesso", "Animal atualizado com sucesso!")
            else:
                codigo = self.db.inserir_animal(esp, rac, fin, pes, pre, qtd, mari)
                if codigo: messagebox.showinfo("Sucesso", f"Lote salvo! Código: {codigo}")

            self.limpar_formulario()
            self.carregar_animais()
            self.carregar_combos_venda()
        except Exception:
            messagebox.showerror("Erro", "Preencha corretamente os números.")

    def carregar_edicao(self):
        selecionado = self.tree_animais.selection()
        if not selecionado: return
        item = self.tree_animais.item(selecionado[0])['values']
        self.codigo_em_edicao = item[0]
        self.e_especie.set(item[1]); self.atualizar_dropdown_racas(None)
        self.e_raca.set(item[2]); self.e_finalidade.set(item[3])
        self.e_peso.delete(0, 'end'); self.e_peso.insert(0, item[4])
        self.e_preco.delete(0, 'end'); self.e_preco.insert(0, item[5])
        self.e_qtd.delete(0, 'end'); self.e_qtd.insert(0, item[6])
        animais = self.db.listar_animais(busca_nome=self.codigo_em_edicao)
        if animais:
            self.e_mari.set(animais[0][7])
        self.btn_salvar.config(text="Atualizar Dados do Lote")
        self.frame_form.config(text=f"Editando Lote: {self.codigo_em_edicao}")

    def excluir_animal(self):
        selecionado = self.tree_animais.selection()
        if not selecionado: return
        codigo = self.tree_animais.item(selecionado[0])['values'][0]
        if messagebox.askyesno("Confirmação", f"EXCLUIR o lote {codigo}?"):
            if self.db.remover_animal(codigo):
                messagebox.showinfo("Sucesso", "Excluído!")
                self.carregar_animais()
                self.carregar_combos_venda()

    def limpar_formulario(self):
        self.codigo_em_edicao = None
        self.e_especie.set(''); self.e_raca.set(''); self.e_finalidade.set('')
        self.e_peso.delete(0, 'end'); self.e_preco.delete(0, 'end'); self.e_qtd.delete(0, 'end') 
        self.e_mari.set(False)
        self.btn_salvar.config(text="Salvar Novo Animal")
        self.frame_form.config(text="Formulário de Lote / Animal")

    # --- ABA 2: PESSOAS E HISTÓRICO 
    def criar_aba_pessoas(self):
        f_cima = ttk.Frame(self.tab_pessoas)
        f_cima.pack(fill="x", padx=10, pady=5)

        #  FORMULÁRIO DE NOVO CLIENTE
        fc = ttk.LabelFrame(f_cima, text="Novo Cliente", padding=10)
        fc.pack(side="left", fill="both", expand=True, padx=5)
        ttk.Label(fc, text="Nome:").grid(row=0, column=0); self.c_nome = ttk.Entry(fc); self.c_nome.grid(row=0, column=1)
        ttk.Label(fc, text="Cidade:").grid(row=0, column=2); self.c_cid = ttk.Entry(fc); self.c_cid.grid(row=0, column=3)
        ttk.Label(fc, text="Time:").grid(row=1, column=0); self.c_time = ttk.Entry(fc); self.c_time.grid(row=1, column=1)
        self.c_anime = tk.BooleanVar()
        ttk.Checkbutton(fc, text="Assiste One Piece?", variable=self.c_anime).grid(row=1, column=2, columnspan=2)
        ttk.Button(fc, text="Salvar Cliente", command=self.salvar_cliente).grid(row=2, column=0, columnspan=4, pady=5)

        #  FORMULÁRIO DE NOVO VENDEDOR 
        fv = ttk.LabelFrame(f_cima, text="Novo Vendedor", padding=10)
        fv.pack(side="right", fill="both", expand=True, padx=5)
        ttk.Label(fv, text="Nome:").grid(row=0, column=0); self.v_nome = ttk.Entry(fv); self.v_nome.grid(row=0, column=1)
        ttk.Label(fv, text="Matrícula:").grid(row=0, column=2); self.v_mat = ttk.Entry(fv); self.v_mat.grid(row=0, column=3)
        ttk.Button(fv, text="Salvar Vendedor", command=self.salvar_vendedor).grid(row=1, column=0, columnspan=4, pady=5)

        # HISTÓRICO DE PEDIDOS E DADOS 
        f_hist = ttk.LabelFrame(self.tab_pessoas, text="Consultar Dados Cadastrais e Histórico do Cliente", padding=10)
        f_hist.pack(fill="both", expand=True, padx=10, pady=5)
        
        ttk.Label(f_hist, text="Selecione o Cliente:").pack(side="top", pady=5)
        self.cb_cliente_hist = ttk.Combobox(f_hist, width=40, state="readonly")
        self.cb_cliente_hist.pack(side="top")
        ttk.Button(f_hist, text="Buscar Histórico e Dados", command=self.ver_historico).pack(side="top", pady=5)

        # Área dos Dados Cadastrais
        self.frame_dados_cli = ttk.LabelFrame(f_hist, text="Dados Cadastrais", padding=5)
        self.frame_dados_cli.pack(fill="x", padx=5, pady=5)
        
        self.lbl_hist_nome = ttk.Label(self.frame_dados_cli, text="Nome: -")
        self.lbl_hist_nome.grid(row=0, column=0, sticky="w", padx=10)
        
        self.lbl_hist_cid = ttk.Label(self.frame_dados_cli, text="Cidade: -")
        self.lbl_hist_cid.grid(row=0, column=1, sticky="w", padx=10)
        
        self.lbl_hist_time = ttk.Label(self.frame_dados_cli, text="Time: -")
        self.lbl_hist_time.grid(row=1, column=0, sticky="w", padx=10)
        
        self.lbl_hist_anime = ttk.Label(self.frame_dados_cli, text="Assiste One Piece: -")
        self.lbl_hist_anime.grid(row=1, column=1, sticky="w", padx=10)

        # Tabela de Histórico
        self.tree_hist = ttk.Treeview(f_hist, columns=("ID Venda", "Data", "Total (R$)", "Forma Pagto", "Status"), show="headings", height=4)
        for col in self.tree_hist["columns"]: self.tree_hist.heading(col, text=col)
        self.tree_hist.pack(fill="both", expand=True, padx=5, pady=5)

    def salvar_cliente(self):
        if self.db.inserir_cliente(self.c_nome.get(), self.c_cid.get(), self.c_time.get(), self.c_anime.get()):
            messagebox.showinfo("OK", "Cliente salvo!"); self.carregar_combos_venda()

    def salvar_vendedor(self):
        if self.db.inserir_vendedor(self.v_nome.get(), self.v_mat.get()):
            messagebox.showinfo("OK", "Vendedor salvo!"); self.carregar_combos_venda()

    def ver_historico(self):
        try:
            id_cli = int(self.cb_cliente_hist.get().split(" - ")[0])
            
            # 1. Atualizar Dados Cadastrais
            cliente = self.db.buscar_cliente(id_cli)
            if cliente:
                self.lbl_hist_nome.config(text=f"Nome: {cliente[0]}")
                self.lbl_hist_cid.config(text=f"Cidade: {cliente[1] if cliente[1] else 'Não informada'}")
                self.lbl_hist_time.config(text=f"Time: {cliente[2] if cliente[2] else 'Não informado'}")
                anime_txt = "Sim" if cliente[3] else "Não"
                self.lbl_hist_anime.config(text=f"Assiste One Piece: {anime_txt}")

            # 2. Atualizar Histórico de Vendas
            for row in self.tree_hist.get_children(): self.tree_hist.delete(row)
            for v in self.db.historico_cliente(id_cli):
                self.tree_hist.insert("", "end", values=(v[0], v[1], f"R$ {v[2]:.2f}", v[3], v[4]))
                
        except Exception as e:
            messagebox.showerror("Erro Interno", f"Ocorreu uma falha ao buscar os dados:\n\n{e}")

    # --- ABA 3: PDV (CARRINHO E PAGAMENTO) ---
    def criar_aba_pdv(self):
        f_dados = ttk.Frame(self.tab_pdv)
        f_dados.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(f_dados, text="1. Cliente:").grid(row=0, column=0, sticky="w")
        self.cb_cliente = ttk.Combobox(f_dados, width=40, state="readonly")
        self.cb_cliente.grid(row=0, column=1, padx=5)
        self.cb_cliente.bind("<<ComboboxSelected>>", self.atualizar_total_carrinho)

        ttk.Label(f_dados, text="2. Vendedor:").grid(row=0, column=2, sticky="w", padx=10)
        self.cb_vendedor = ttk.Combobox(f_dados, width=30, state="readonly")
        self.cb_vendedor.grid(row=0, column=3, padx=5)

        f_add = ttk.LabelFrame(self.tab_pdv, text="3. Adicionar Lotes ao Carrinho", padding=10)
        f_add.pack(fill="x", padx=10, pady=10)
        ttk.Label(f_add, text="Selecione o Lote:").grid(row=0, column=0)
        self.cb_animal = ttk.Combobox(f_add, width=60, state="readonly")
        self.cb_animal.grid(row=0, column=1, padx=5)
        ttk.Label(f_add, text="Qtd:").grid(row=0, column=2)
        self.qtd_venda = ttk.Entry(f_add, width=10)
        self.qtd_venda.grid(row=0, column=3, padx=5)
        ttk.Button(f_add, text="Adicionar ➕", command=self.adicionar_ao_carrinho).grid(row=0, column=4, padx=10)

        self.tree_carrinho = ttk.Treeview(self.tab_pdv, columns=("Código", "Animal", "Qtd", "Preço", "Subtotal"), show="headings", height=4)
        for col in self.tree_carrinho["columns"]: self.tree_carrinho.heading(col, text=col)
        self.tree_carrinho.pack(fill="x", padx=10, pady=5)

        # Formas de Pagamento e Status
        f_pagto = ttk.Frame(self.tab_pdv)
        f_pagto.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(f_pagto, text="Forma de Pagto:").pack(side="left")
        self.cb_pagto = ttk.Combobox(f_pagto, values=["Cartão", "Boleto", "Pix", "Berries"], state="readonly", width=10)
        self.cb_pagto.set("Pix")
        self.cb_pagto.pack(side="left", padx=5)

        ttk.Label(f_pagto, text="Status:").pack(side="left", padx=10)
        self.cb_status = ttk.Combobox(f_pagto, values=["Aprovado", "Pendente", "Aguardando Confirmação"], state="readonly", width=20)
        self.cb_status.set("Aprovado")
        self.cb_status.pack(side="left", padx=5)

        self.lbl_total = ttk.Label(f_pagto, text="Total: R$ 0.00", font=('Helvetica', 14, 'bold'), foreground="#d32f2f")
        self.lbl_total.pack(side="right", padx=10)

        ttk.Button(self.tab_pdv, text="💳 FINALIZAR COMPRA", command=self.processar_carrinho).pack(pady=10)

    def adicionar_ao_carrinho(self):
        try:
            linha = self.cb_animal.get()
            if not linha: return
            partes = linha.split(" | ")
            codigo_animal = partes[0].split(" - ")[0]
            desc = partes[0].split(" - ")[1]
            estoque_disp = int(partes[1].replace("Disp: ", ""))
            preco_unit = float(partes[2].replace("R$ ", ""))
            qtd_desejada = int(self.qtd_venda.get())

            qtd_ja_no_carrinho = sum(item["qtd"] for item in self.carrinho if item["codigo"] == codigo_animal)
            if (qtd_desejada + qtd_ja_no_carrinho) > estoque_disp:
                messagebox.showerror("ERRO", f"Estoque insuficiente!\nDisponível: {estoque_disp}\nNo carrinho: {qtd_ja_no_carrinho}")
                return

            subtotal = preco_unit * qtd_desejada
            self.carrinho.append({"codigo": codigo_animal, "qtd": qtd_desejada, "subtotal": subtotal})
            self.tree_carrinho.insert("", "end", values=(codigo_animal, desc, qtd_desejada, f"R$ {preco_unit:.2f}", f"R$ {subtotal:.2f}"))
            
            self.atualizar_total_carrinho()
        except: messagebox.showerror("Erro", "Dados inválidos.")

    def processar_carrinho(self):
        if not self.carrinho: return
        try:
            id_cli = int(self.cb_cliente.get().split(" - ")[0])
            id_vend = int(self.cb_vendedor.get().split(" - ")[0])
            pagto = self.cb_pagto.get()
            status = self.cb_status.get()

            id_venda = self.db.criar_venda(id_cli, id_vend, pagto, status)
            if id_venda:
                for item in self.carrinho:
                    self.db.adicionar_item(id_venda, item["codigo"], item["qtd"])
                
                self.db.aplicar_desconto(id_venda, id_cli)
                messagebox.showinfo("Sucesso", f"Compra faturada!\nMétodo: {pagto} | Status: {status}")
                
                self.carrinho.clear()
                for row in self.tree_carrinho.get_children(): self.tree_carrinho.delete(row)
                self.lbl_total.config(text="Total: R$ 0.00")
                self.carregar_animais()
                self.carregar_relatorios()
                self.carregar_combos_venda()
        except: messagebox.showerror("Erro", "Selecione Cliente e Vendedor.") 

    def atualizar_total_carrinho(self, event=None):
        total_bruto = sum(item["subtotal"] for item in self.carrinho)
        
        # Pega o cliente selecionado na combobox
        cliente_selecionado = self.cb_cliente.get()
        desconto_percentual = 0.0
        
        if cliente_selecionado:
            id_cli = int(cliente_selecionado.split(" - ")[0])
            desconto_percentual = self.db.obter_desconto_cliente(id_cli)
            
        total_com_desconto = total_bruto - (total_bruto * desconto_percentual)
        
        # Atualiza o texto da Label na tela
        texto_label = f"Total: R$ {total_com_desconto:.2f}"
        if desconto_percentual > 0:
            texto_label += f" (-{int(desconto_percentual*100)}%)"
            
        self.lbl_total.config(text=texto_label) 

    # --- ABA 4: RELATÓRIOS 
    def criar_aba_relatorios(self):
        self.frame_resumos = ttk.LabelFrame(self.tab_relatorios, text="Resumo Geral da Fazenda (Estoque e Clientes)", padding=10)
        self.frame_resumos.pack(fill="x", padx=10, pady=10)

        self.lbl_resumo_estoque = ttk.Label(self.frame_resumos, text="Carregando dados do estoque...", font=('Helvetica', 11, 'bold'))
        self.lbl_resumo_estoque.pack(anchor="w", pady=5)

        self.lbl_resumo_clientes = ttk.Label(self.frame_resumos, text="Carregando dados de clientes...", font=('Helvetica', 11, 'bold'))
        self.lbl_resumo_clientes.pack(anchor="w", pady=5)
        frame_vendas = ttk.LabelFrame(self.tab_relatorios, text="Relatório Mensal de Vendas por Vendedor", padding=10)
        frame_vendas.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree_rel = ttk.Treeview(frame_vendas, columns=("ID", "Vendedor", "Qtd Vendas", "Valor Arrecadado", "Mês/Ano"), show="headings")
        for col in self.tree_rel["columns"]: self.tree_rel.heading(col, text=col)
        self.tree_rel.pack(fill="both", expand=True)

    # --- CARREGAMENTOS GERAIS 
    def carregar_dados(self):
        self.carregar_animais()
        self.carregar_combos_venda()
        self.carregar_relatorios()

    def carregar_animais(self, baixo_estoque=False):
        especie = self.filtro_especie.get() if hasattr(self, 'filtro_especie') else "Todas"
        nome = self.f_nome.get() if hasattr(self, 'f_nome') else ""
        preco = self.f_preco.get() if hasattr(self, 'f_preco') else ""
        mari = self.f_mari.get() if hasattr(self, 'f_mari') else False 

        for row in self.tree_animais.get_children(): 
            self.tree_animais.delete(row)
        
        for a in self.db.listar_animais(baixo_estoque, especie, nome, preco, mari):
            qtd = a[6]
            nascido_mari_bool = a[7] 
            texto_mari = "Sim" if nascido_mari_bool else "Não"
            status = "🟢 Disponível" if qtd > 0 else "🔴 VENDIDO"
            valores_linha = (a[0], a[1], a[2], a[3], a[4], a[5], a[6], texto_mari, status)
            
            self.tree_animais.insert("", "end", values=valores_linha)

    def carregar_combos_venda(self):
        clientes = [f"{c[0]} - {c[1]}" for c in self.db.listar_clientes()]
        self.cb_cliente['values'] = clientes
        if hasattr(self, 'cb_cliente_hist'): self.cb_cliente_hist['values'] = clientes
        
        self.cb_vendedor['values'] = [f"{v[0]} - {v[1]}" for v in self.db.listar_vendedores()]
        self.cb_animal['values'] = [f"{a[0]} - {a[1]} {a[2]} | Disp: {a[6]} | R$ {a[5]}" for a in self.db.listar_animais() if a[6] > 0]

    def carregar_relatorios(self):
        # Atualiza os textos do Resumo Geral (Estoque e Clientes)
        resumo = self.db.resumo_geral()
        if resumo:
            texto_estoque = f" Estoque: {resumo['total_lotes']} Lote(s) cadastrado(s) | Total de {resumo['total_cabecas']} cabeça(s) disponíveis | Patrimônio Estimado: R$ {resumo['valor_patrimonio']:.2f}"
            self.lbl_resumo_estoque.config(text=texto_estoque)
            
            texto_clientes = f" Clientes: {resumo['total_clientes']} cliente(s) cadastrado(s) na base."
            self.lbl_resumo_clientes.config(text=texto_clientes)

        #  Atualiza a Tabela de Vendedores
        for row in self.tree_rel.get_children(): self.tree_rel.delete(row)
        for r in self.db.relatorio_vendedores():
            self.tree_rel.insert("", "end", values=(r[0], r[1], r[2], f"R$ {r[3]:.2f}", r[4]))

if __name__ == "__main__":
    root = tk.Tk()
    app = AppPecuaria(root)
    root.mainloop()