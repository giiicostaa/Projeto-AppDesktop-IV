from abc import ABC, abstractmethod
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox


# ==========================================================
# CLASSES DE DOMÍNIO
# ==========================================================

class Pessoa(ABC):
    def __init__(self, nome, cpf, telefone, id=None):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone

    @abstractmethod
    def resumo(self):
        pass


class Cliente(Pessoa):
    def __init__(self, nome, cpf, telefone, endereco, id=None):
        super().__init__(nome, cpf, telefone, id)
        self.endereco = endereco

    def resumo(self):
        return f"{self.nome} - CPF: {self.cpf}"


class Veterinario(Pessoa):
    def __init__(self, nome, cpf, telefone, crmv, especialidade, id=None):
        super().__init__(nome, cpf, telefone, id)
        self.crmv = crmv
        self.especialidade = especialidade

    def resumo(self):
        return f"{self.nome} - CRMV: {self.crmv}"


class Animal(ABC):
    def __init__(self, nome, idade, peso, raca, cliente_id, id=None):
        self.id = id
        self.nome = nome
        self.idade = idade
        self.peso = peso
        self.raca = raca
        self.cliente_id = cliente_id

    @abstractmethod
    def emitir_som(self):
        pass


class Cachorro(Animal):
    def emitir_som(self):
        return f"{self.nome}: Au Au!"


class Gato(Animal):
    def emitir_som(self):
        return f"{self.nome}: Miau!"


class Consulta:
    def __init__(
        self, cliente_id, animal_id, veterinario_id,
        data, motivo, status="Agendada", id=None
    ):
        self.id = id
        self.cliente_id = cliente_id
        self.animal_id = animal_id
        self.veterinario_id = veterinario_id
        self.data = data
        self.motivo = motivo
        self.status = status

    def concluir(self):
        if self.status != "Cancelada":
            self.status = "Concluída"

    def cancelar(self):
        if self.status != "Concluída":
            self.status = "Cancelada"


# ==========================================================
# BANCO DE DADOS SQLITE
# ==========================================================

class BancoDados:
    def __init__(self, arquivo="vetcare.db"):
        self.conexao = sqlite3.connect(arquivo)
        self.conexao.execute("PRAGMA foreign_keys = ON")
        self.criar_tabelas()

    def criar_tabelas(self):
        cursor = self.conexao.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT NOT NULL UNIQUE,
                telefone TEXT,
                endereco TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS veterinarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT,
                telefone TEXT,
                crmv TEXT NOT NULL UNIQUE,
                especialidade TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS animais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                idade INTEGER NOT NULL,
                peso REAL NOT NULL,
                raca TEXT,
                tipo TEXT NOT NULL,
                cliente_id INTEGER NOT NULL,
                FOREIGN KEY (cliente_id)
                    REFERENCES clientes(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consultas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                animal_id INTEGER NOT NULL,
                veterinario_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                motivo TEXT,
                status TEXT NOT NULL DEFAULT 'Agendada',
                FOREIGN KEY (cliente_id)
                    REFERENCES clientes(id) ON DELETE CASCADE,
                FOREIGN KEY (animal_id)
                    REFERENCES animais(id) ON DELETE CASCADE,
                FOREIGN KEY (veterinario_id)
                    REFERENCES veterinarios(id) ON DELETE CASCADE
            )
        """)

        self.conexao.commit()

    def executar(self, sql, parametros=()):
        cursor = self.conexao.cursor()
        cursor.execute(sql, parametros)
        self.conexao.commit()
        return cursor

    def consultar(self, sql, parametros=()):
        cursor = self.conexao.cursor()
        cursor.execute(sql, parametros)
        return cursor.fetchall()

    def fechar(self):
        self.conexao.close()


# ==========================================================
# JANELAS DE FORMULÁRIO
# ==========================================================

class FormularioBase(tk.Toplevel):
    def __init__(self, app, titulo):
        super().__init__(app)
        self.app = app
        self.title(titulo)
        self.resizable(False, False)
        self.transient(app)
        self.grab_set()
        self.configure(bg="#f5f7fb")
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def campo(self, texto, variavel, linha, mostrar=None):
        ttk.Label(self, text=texto).grid(
            row=linha, column=0, padx=12, pady=8, sticky="w"
        )
        entrada = ttk.Entry(self, textvariable=variavel, width=34, show=mostrar)
        entrada.grid(row=linha, column=1, padx=12, pady=8)
        return entrada

    def botoes(self, linha, comando_salvar):
        frame = ttk.Frame(self)
        frame.grid(row=linha, column=0, columnspan=2, pady=15)
        ttk.Button(frame, text="Salvar", command=comando_salvar).pack(
            side="left", padx=5
        )
        ttk.Button(frame, text="Cancelar", command=self.destroy).pack(
            side="left", padx=5
        )


class FormCliente(FormularioBase):
    def __init__(self, app, cliente=None):
        super().__init__(app, "Cliente")
        self.cliente = cliente
        self.nome = tk.StringVar(value=cliente[1] if cliente else "")
        self.cpf = tk.StringVar(value=cliente[2] if cliente else "")
        self.telefone = tk.StringVar(value=cliente[3] if cliente else "")
        self.endereco = tk.StringVar(value=cliente[4] if cliente else "")

        self.campo("Nome:", self.nome, 0)
        self.campo("CPF:", self.cpf, 1)
        self.campo("Telefone:", self.telefone, 2)
        self.campo("Endereço:", self.endereco, 3)
        self.botoes(4, self.salvar)

    def salvar(self):
        nome = self.nome.get().strip()
        cpf = self.cpf.get().strip()

        if not nome or not cpf:
            messagebox.showwarning(
                "Atenção", "Nome e CPF são obrigatórios.", parent=self
            )
            return

        try:
            if self.cliente:
                self.app.db.executar(
                    """UPDATE clientes
                       SET nome=?, cpf=?, telefone=?, endereco=?
                       WHERE id=?""",
                    (
                        nome,
                        cpf,
                        self.telefone.get().strip(),
                        self.endereco.get().strip(),
                        self.cliente[0],
                    )
                )
            else:
                self.app.db.executar(
                    """INSERT INTO clientes
                       (nome, cpf, telefone, endereco)
                       VALUES (?, ?, ?, ?)""",
                    (
                        nome,
                        cpf,
                        self.telefone.get().strip(),
                        self.endereco.get().strip(),
                    )
                )

            self.app.atualizar_tudo()
            self.destroy()

        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Erro", "Já existe um cliente com esse CPF.", parent=self
            )


class FormVeterinario(FormularioBase):
    def __init__(self, app, veterinario=None):
        super().__init__(app, "Veterinário")
        self.veterinario = veterinario
        self.nome = tk.StringVar(value=veterinario[1] if veterinario else "")
        self.cpf = tk.StringVar(value=veterinario[2] if veterinario else "")
        self.telefone = tk.StringVar(value=veterinario[3] if veterinario else "")
        self.crmv = tk.StringVar(value=veterinario[4] if veterinario else "")
        self.especialidade = tk.StringVar(
            value=veterinario[5] if veterinario else ""
        )

        self.campo("Nome:", self.nome, 0)
        self.campo("CPF:", self.cpf, 1)
        self.campo("Telefone:", self.telefone, 2)
        self.campo("CRMV:", self.crmv, 3)
        self.campo("Especialidade:", self.especialidade, 4)
        self.botoes(5, self.salvar)

    def salvar(self):
        nome = self.nome.get().strip()
        crmv = self.crmv.get().strip()

        if not nome or not crmv:
            messagebox.showwarning(
                "Atenção", "Nome e CRMV são obrigatórios.", parent=self
            )
            return

        try:
            valores = (
                nome,
                self.cpf.get().strip(),
                self.telefone.get().strip(),
                crmv,
                self.especialidade.get().strip(),
            )

            if self.veterinario:
                self.app.db.executar(
                    """UPDATE veterinarios
                       SET nome=?, cpf=?, telefone=?, crmv=?, especialidade=?
                       WHERE id=?""",
                    valores + (self.veterinario[0],)
                )
            else:
                self.app.db.executar(
                    """INSERT INTO veterinarios
                       (nome, cpf, telefone, crmv, especialidade)
                       VALUES (?, ?, ?, ?, ?)""",
                    valores
                )

            self.app.atualizar_tudo()
            self.destroy()

        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Erro", "Já existe um veterinário com esse CRMV.", parent=self
            )


class FormAnimal(FormularioBase):
    def __init__(self, app, animal=None):
        super().__init__(app, "Animal")
        self.animal = animal
        self.nome = tk.StringVar(value=animal[1] if animal else "")
        self.idade = tk.StringVar(value=animal[2] if animal else "")
        self.peso = tk.StringVar(value=animal[3] if animal else "")
        self.raca = tk.StringVar(value=animal[4] if animal else "")
        self.tipo = tk.StringVar(value=animal[5] if animal else "Cachorro")
        self.cliente = tk.StringVar()

        self.campo("Nome:", self.nome, 0)
        self.campo("Idade:", self.idade, 1)
        self.campo("Peso:", self.peso, 2)
        self.campo("Raça:", self.raca, 3)

        ttk.Label(self, text="Tipo:").grid(
            row=4, column=0, padx=12, pady=8, sticky="w"
        )
        ttk.Combobox(
            self,
            textvariable=self.tipo,
            values=["Cachorro", "Gato"],
            state="readonly",
            width=31
        ).grid(row=4, column=1, padx=12, pady=8)

        ttk.Label(self, text="Tutor:").grid(
            row=5, column=0, padx=12, pady=8, sticky="w"
        )

        self.clientes = self.app.db.consultar(
            "SELECT id, nome FROM clientes ORDER BY nome"
        )
        valores = [f"{id_} - {nome}" for id_, nome in self.clientes]

        self.combo_cliente = ttk.Combobox(
            self,
            textvariable=self.cliente,
            values=valores,
            state="readonly",
            width=31
        )
        self.combo_cliente.grid(row=5, column=1, padx=12, pady=8)

        if animal:
            alvo = next(
                (
                    f"{id_} - {nome}"
                    for id_, nome in self.clientes
                    if id_ == animal[6]
                ),
                ""
            )
            self.cliente.set(alvo)
        elif valores:
            self.cliente.set(valores[0])

        self.botoes(6, self.salvar)

    def salvar(self):
        if not self.cliente.get():
            messagebox.showwarning(
                "Atenção", "Cadastre um cliente antes.", parent=self
            )
            return

        try:
            nome = self.nome.get().strip()
            idade = int(self.idade.get())
            peso = float(self.peso.get().replace(",", "."))
            cliente_id = int(self.cliente.get().split(" - ", 1)[0])

            if not nome:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                "Atenção", "Preencha nome, idade e peso corretamente.", parent=self
            )
            return

        valores = (
            nome,
            idade,
            peso,
            self.raca.get().strip(),
            self.tipo.get(),
            cliente_id,
        )

        if self.animal:
            self.app.db.executar(
                """UPDATE animais
                   SET nome=?, idade=?, peso=?, raca=?, tipo=?, cliente_id=?
                   WHERE id=?""",
                valores + (self.animal[0],)
            )
        else:
            self.app.db.executar(
                """INSERT INTO animais
                   (nome, idade, peso, raca, tipo, cliente_id)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                valores
            )

        self.app.atualizar_tudo()
        self.destroy()


class FormConsulta(FormularioBase):
    def __init__(self, app, consulta=None):
        super().__init__(app, "Consulta")
        self.consulta = consulta
        self.animal = tk.StringVar()
        self.veterinario = tk.StringVar()
        self.data = tk.StringVar(value=consulta[4] if consulta else "")
        self.motivo = tk.StringVar(value=consulta[5] if consulta else "")

        ttk.Label(self, text="Animal:").grid(
            row=0, column=0, padx=12, pady=8, sticky="w"
        )
        self.animais = app.db.consultar("""
            SELECT a.id, a.nome, c.nome
            FROM animais a
            JOIN clientes c ON c.id = a.cliente_id
            ORDER BY a.nome
        """)
        valores_animais = [
            f"{id_} - {nome} (Tutor: {tutor})"
            for id_, nome, tutor in self.animais
        ]
        ttk.Combobox(
            self,
            textvariable=self.animal,
            values=valores_animais,
            state="readonly",
            width=31
        ).grid(row=0, column=1, padx=12, pady=8)

        ttk.Label(self, text="Veterinário:").grid(
            row=1, column=0, padx=12, pady=8, sticky="w"
        )
        self.veterinarios = app.db.consultar(
            "SELECT id, nome FROM veterinarios ORDER BY nome"
        )
        valores_vets = [
            f"{id_} - {nome}" for id_, nome in self.veterinarios
        ]
        ttk.Combobox(
            self,
            textvariable=self.veterinario,
            values=valores_vets,
            state="readonly",
            width=31
        ).grid(row=1, column=1, padx=12, pady=8)

        self.campo("Data:", self.data, 2)
        self.campo("Motivo:", self.motivo, 3)

        if consulta:
            self.animal.set(
                next(
                    (
                        item for item in valores_animais
                        if item.startswith(f"{consulta[2]} - ")
                    ),
                    ""
                )
            )
            self.veterinario.set(
                next(
                    (
                        item for item in valores_vets
                        if item.startswith(f"{consulta[3]} - ")
                    ),
                    ""
                )
            )
        else:
            if valores_animais:
                self.animal.set(valores_animais[0])
            if valores_vets:
                self.veterinario.set(valores_vets[0])

        self.botoes(4, self.salvar)

    def salvar(self):
        if not self.animal.get() or not self.veterinario.get():
            messagebox.showwarning(
                "Atenção",
                "Cadastre pelo menos um animal e um veterinário.",
                parent=self
            )
            return

        data = self.data.get().strip()

        if not data:
            messagebox.showwarning(
                "Atenção", "A data é obrigatória.", parent=self
            )
            return

        animal_id = int(self.animal.get().split(" - ", 1)[0])
        vet_id = int(self.veterinario.get().split(" - ", 1)[0])
        cliente_id = self.app.db.consultar(
            "SELECT cliente_id FROM animais WHERE id=?",
            (animal_id,)
        )[0][0]

        if self.consulta:
            self.app.db.executar(
                """UPDATE consultas
                   SET cliente_id=?, animal_id=?, veterinario_id=?,
                       data=?, motivo=?
                   WHERE id=?""",
                (
                    cliente_id,
                    animal_id,
                    vet_id,
                    data,
                    self.motivo.get().strip(),
                    self.consulta[0],
                )
            )
        else:
            self.app.db.executar(
                """INSERT INTO consultas
                   (cliente_id, animal_id, veterinario_id, data, motivo, status)
                   VALUES (?, ?, ?, ?, ?, 'Agendada')""",
                (
                    cliente_id,
                    animal_id,
                    vet_id,
                    data,
                    self.motivo.get().strip(),
                )
            )

        self.app.atualizar_tudo()
        self.destroy()


# ==========================================================
# APLICAÇÃO GRÁFICA
# ==========================================================

class VetCareApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db = BancoDados()

        self.title("VetCare - Clínica Veterinária")
        self.geometry("1100x680")
        self.minsize(960, 600)
        self.configure(bg="#eef2f7")
        self.protocol("WM_DELETE_WINDOW", self.encerrar)

        self.configurar_estilo()
        self.criar_cabecalho()
        self.criar_abas()
        self.criar_barra_status()
        self.atualizar_tudo()

    def configurar_estilo(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")

        estilo.configure(
            "TNotebook",
            background="#eef2f7",
            borderwidth=0
        )
        estilo.configure(
            "TNotebook.Tab",
            font=("Segoe UI", 10, "bold"),
            padding=(18, 9)
        )
        estilo.map(
            "TNotebook.Tab",
            background=[("selected", "#2f6fed")],
            foreground=[("selected", "white")]
        )
        estilo.configure(
            "Treeview",
            font=("Segoe UI", 10),
            rowheight=28,
            background="white",
            fieldbackground="white"
        )
        estilo.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#dfe7f3"
        )
        estilo.configure(
            "TButton",
            font=("Segoe UI", 10),
            padding=(12, 7)
        )
        estilo.configure(
            "Accent.TButton",
            background="#2f6fed",
            foreground="white"
        )
        estilo.map(
            "Accent.TButton",
            background=[("active", "#2459c4")]
        )

    def criar_cabecalho(self):
        frame = tk.Frame(self, bg="#17324d", height=78)
        frame.pack(fill="x")
        frame.pack_propagate(False)

        tk.Label(
            frame,
            text="VETCARE",
            font=("Segoe UI", 22, "bold"),
            fg="white",
            bg="#17324d"
        ).pack(side="left", padx=24)

        tk.Label(
            frame,
            text="Sistema de Clínica Veterinária — Nível 4",
            font=("Segoe UI", 11),
            fg="#d7e4f2",
            bg="#17324d"
        ).pack(side="left", pady=4)

        ttk.Button(
            frame,
            text="Relatório",
            style="Accent.TButton",
            command=self.mostrar_relatorio
        ).pack(side="right", padx=20)

    def criar_abas(self):
        self.abas = ttk.Notebook(self)
        self.abas.pack(fill="both", expand=True, padx=16, pady=16)

        self.aba_clientes = ttk.Frame(self.abas)
        self.aba_vets = ttk.Frame(self.abas)
        self.aba_animais = ttk.Frame(self.abas)
        self.aba_consultas = ttk.Frame(self.abas)

        self.abas.add(self.aba_clientes, text="Clientes")
        self.abas.add(self.aba_vets, text="Veterinários")
        self.abas.add(self.aba_animais, text="Animais")
        self.abas.add(self.aba_consultas, text="Consultas")

        self.tree_clientes = self.criar_tabela(
            self.aba_clientes,
            ("id", "nome", "cpf", "telefone", "endereco"),
            ("ID", "Nome", "CPF", "Telefone", "Endereço")
        )
        self.criar_botoes_crud(
            self.aba_clientes,
            self.novo_cliente,
            self.editar_cliente,
            self.excluir_cliente
        )

        self.tree_vets = self.criar_tabela(
            self.aba_vets,
            ("id", "nome", "cpf", "telefone", "crmv", "especialidade"),
            ("ID", "Nome", "CPF", "Telefone", "CRMV", "Especialidade")
        )
        self.criar_botoes_crud(
            self.aba_vets,
            self.novo_veterinario,
            self.editar_veterinario,
            self.excluir_veterinario
        )

        self.tree_animais = self.criar_tabela(
            self.aba_animais,
            ("id", "nome", "idade", "peso", "raca", "tipo", "tutor"),
            ("ID", "Nome", "Idade", "Peso", "Raça", "Tipo", "Tutor")
        )
        self.criar_botoes_crud(
            self.aba_animais,
            self.novo_animal,
            self.editar_animal,
            self.excluir_animal,
            extra=("Testar sons", self.testar_polimorfismo)
        )

        self.tree_consultas = self.criar_tabela(
            self.aba_consultas,
            (
                "id", "cliente_id", "animal_id", "vet_id",
                "cliente", "animal", "vet", "data", "motivo", "status"
            ),
            (
                "ID", "Cliente ID", "Animal ID", "Vet ID",
                "Cliente", "Animal", "Veterinário",
                "Data", "Motivo", "Status"
            )
        )

        # Oculta colunas de IDs internos na visualização.
        for coluna in ("cliente_id", "animal_id", "vet_id"):
            self.tree_consultas.column(coluna, width=0, stretch=False)
            self.tree_consultas.heading(coluna, text="")

        self.criar_botoes_consultas()

    def criar_tabela(self, pai, colunas, titulos):
        frame = ttk.Frame(pai)
        frame.pack(fill="both", expand=True, padx=12, pady=(12, 4))

        tree = ttk.Treeview(
            frame,
            columns=colunas,
            show="headings",
            selectmode="browse"
        )

        scroll_y = ttk.Scrollbar(
            frame, orient="vertical", command=tree.yview
        )
        scroll_x = ttk.Scrollbar(
            frame, orient="horizontal", command=tree.xview
        )

        tree.configure(
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        for coluna, titulo in zip(colunas, titulos):
            tree.heading(coluna, text=titulo)
            tree.column(coluna, width=130, anchor="center")

        return tree

    def criar_botoes_crud(
        self, pai, novo, editar, excluir, extra=None
    ):
        frame = ttk.Frame(pai)
        frame.pack(fill="x", padx=12, pady=(4, 12))

        ttk.Button(
            frame, text="Novo", style="Accent.TButton", command=novo
        ).pack(side="left", padx=4)
        ttk.Button(
            frame, text="Editar", command=editar
        ).pack(side="left", padx=4)
        ttk.Button(
            frame, text="Excluir", command=excluir
        ).pack(side="left", padx=4)
        ttk.Button(
            frame, text="Atualizar", command=self.atualizar_tudo
        ).pack(side="left", padx=4)

        if extra:
            ttk.Button(
                frame, text=extra[0], command=extra[1]
            ).pack(side="right", padx=4)

    def criar_botoes_consultas(self):
        frame = ttk.Frame(self.aba_consultas)
        frame.pack(fill="x", padx=12, pady=(4, 12))

        ttk.Button(
            frame,
            text="Nova consulta",
            style="Accent.TButton",
            command=self.nova_consulta
        ).pack(side="left", padx=4)
        ttk.Button(
            frame, text="Editar", command=self.editar_consulta
        ).pack(side="left", padx=4)
        ttk.Button(
            frame, text="Concluir", command=self.concluir_consulta
        ).pack(side="left", padx=4)
        ttk.Button(
            frame, text="Cancelar", command=self.cancelar_consulta
        ).pack(side="left", padx=4)
        ttk.Button(
            frame, text="Excluir", command=self.excluir_consulta
        ).pack(side="left", padx=4)
        ttk.Button(
            frame, text="Atualizar", command=self.atualizar_tudo
        ).pack(side="left", padx=4)

    def criar_barra_status(self):
        self.status = tk.StringVar(value="Sistema pronto.")
        tk.Label(
            self,
            textvariable=self.status,
            anchor="w",
            bg="#dfe7f3",
            fg="#17324d",
            font=("Segoe UI", 9)
        ).pack(fill="x", side="bottom")

    @staticmethod
    def limpar_tree(tree):
        for item in tree.get_children():
            tree.delete(item)

    def atualizar_tudo(self):
        self.atualizar_clientes()
        self.atualizar_veterinarios()
        self.atualizar_animais()
        self.atualizar_consultas()
        self.status.set("Dados atualizados com sucesso.")

    def atualizar_clientes(self):
        self.limpar_tree(self.tree_clientes)
        for linha in self.db.consultar(
            "SELECT id, nome, cpf, telefone, endereco FROM clientes ORDER BY nome"
        ):
            self.tree_clientes.insert("", "end", values=linha)

    def atualizar_veterinarios(self):
        self.limpar_tree(self.tree_vets)
        for linha in self.db.consultar(
            """SELECT id, nome, cpf, telefone, crmv, especialidade
               FROM veterinarios ORDER BY nome"""
        ):
            self.tree_vets.insert("", "end", values=linha)

    def atualizar_animais(self):
        self.limpar_tree(self.tree_animais)
        linhas = self.db.consultar("""
            SELECT a.id, a.nome, a.idade, a.peso, a.raca,
                   a.tipo, c.nome
            FROM animais a
            JOIN clientes c ON c.id = a.cliente_id
            ORDER BY a.nome
        """)
        for linha in linhas:
            self.tree_animais.insert("", "end", values=linha)

    def atualizar_consultas(self):
        self.limpar_tree(self.tree_consultas)
        linhas = self.db.consultar("""
            SELECT co.id, co.cliente_id, co.animal_id, co.veterinario_id,
                   c.nome, a.nome, v.nome, co.data, co.motivo, co.status
            FROM consultas co
            JOIN clientes c ON c.id = co.cliente_id
            JOIN animais a ON a.id = co.animal_id
            JOIN veterinarios v ON v.id = co.veterinario_id
            ORDER BY co.id DESC
        """)
        for linha in linhas:
            self.tree_consultas.insert("", "end", values=linha)

    @staticmethod
    def selecionado(tree):
        item = tree.selection()

        if not item:
            return None

        return tree.item(item[0], "values")

    # ---------------------- CLIENTES ----------------------

    def novo_cliente(self):
        FormCliente(self)

    def editar_cliente(self):
        valores = self.selecionado(self.tree_clientes)

        if not valores:
            messagebox.showinfo("Informação", "Selecione um cliente.")
            return

        cliente = (
            int(valores[0]), valores[1], valores[2], valores[3], valores[4]
        )
        FormCliente(self, cliente)

    def excluir_cliente(self):
        valores = self.selecionado(self.tree_clientes)

        if not valores:
            messagebox.showinfo("Informação", "Selecione um cliente.")
            return

        if messagebox.askyesno(
            "Confirmar",
            "Excluir o cliente e todos os registros relacionados?"
        ):
            self.db.executar(
                "DELETE FROM clientes WHERE id=?",
                (valores[0],)
            )
            self.atualizar_tudo()

    # ---------------------- VETERINÁRIOS ----------------------

    def novo_veterinario(self):
        FormVeterinario(self)

    def editar_veterinario(self):
        valores = self.selecionado(self.tree_vets)

        if not valores:
            messagebox.showinfo("Informação", "Selecione um veterinário.")
            return

        veterinario = (
            int(valores[0]), valores[1], valores[2],
            valores[3], valores[4], valores[5]
        )
        FormVeterinario(self, veterinario)

    def excluir_veterinario(self):
        valores = self.selecionado(self.tree_vets)

        if not valores:
            messagebox.showinfo("Informação", "Selecione um veterinário.")
            return

        if messagebox.askyesno(
            "Confirmar",
            "Excluir o veterinário e suas consultas?"
        ):
            self.db.executar(
                "DELETE FROM veterinarios WHERE id=?",
                (valores[0],)
            )
            self.atualizar_tudo()

    # ---------------------- ANIMAIS ----------------------

    def novo_animal(self):
        if not self.db.consultar("SELECT id FROM clientes LIMIT 1"):
            messagebox.showwarning(
                "Atenção", "Cadastre um cliente antes de cadastrar animais."
            )
            return

        FormAnimal(self)

    def editar_animal(self):
        valores = self.selecionado(self.tree_animais)

        if not valores:
            messagebox.showinfo("Informação", "Selecione um animal.")
            return

        cliente_id = self.db.consultar(
            "SELECT cliente_id FROM animais WHERE id=?",
            (valores[0],)
        )[0][0]

        animal = (
            int(valores[0]),
            valores[1],
            int(valores[2]),
            float(valores[3]),
            valores[4],
            valores[5],
            cliente_id,
        )
        FormAnimal(self, animal)

    def excluir_animal(self):
        valores = self.selecionado(self.tree_animais)

        if not valores:
            messagebox.showinfo("Informação", "Selecione um animal.")
            return

        if messagebox.askyesno(
            "Confirmar",
            "Excluir o animal e suas consultas?"
        ):
            self.db.executar(
                "DELETE FROM animais WHERE id=?",
                (valores[0],)
            )
            self.atualizar_tudo()

    def testar_polimorfismo(self):
        linhas = self.db.consultar(
            "SELECT nome, idade, peso, raca, tipo, cliente_id, id FROM animais"
        )

        if not linhas:
            messagebox.showinfo(
                "Polimorfismo", "Nenhum animal cadastrado."
            )
            return

        sons = []

        for linha in linhas:
            classe = Cachorro if linha[4] == "Cachorro" else Gato
            animal = classe(
                linha[0], linha[1], linha[2],
                linha[3], linha[5], linha[6]
            )
            sons.append(animal.emitir_som())

        messagebox.showinfo(
            "Teste de polimorfismo",
            "\n".join(sons)
        )

    # ---------------------- CONSULTAS ----------------------

    def nova_consulta(self):
        tem_animal = self.db.consultar("SELECT id FROM animais LIMIT 1")
        tem_vet = self.db.consultar("SELECT id FROM veterinarios LIMIT 1")

        if not tem_animal or not tem_vet:
            messagebox.showwarning(
                "Atenção",
                "Cadastre ao menos um animal e um veterinário."
            )
            return

        FormConsulta(self)

    def editar_consulta(self):
        valores = self.selecionado(self.tree_consultas)

        if not valores:
            messagebox.showinfo("Informação", "Selecione uma consulta.")
            return

        consulta = (
            int(valores[0]),
            int(valores[1]),
            int(valores[2]),
            int(valores[3]),
            valores[7],
            valores[8],
            valores[9],
        )
        FormConsulta(self, consulta)

    def alterar_status(self, novo_status):
        valores = self.selecionado(self.tree_consultas)

        if not valores:
            messagebox.showinfo("Informação", "Selecione uma consulta.")
            return

        atual = valores[9]

        if atual == "Cancelada" and novo_status == "Concluída":
            messagebox.showwarning(
                "Atenção", "Consulta cancelada não pode ser concluída."
            )
            return

        if atual == "Concluída" and novo_status == "Cancelada":
            messagebox.showwarning(
                "Atenção", "Consulta concluída não pode ser cancelada."
            )
            return

        self.db.executar(
            "UPDATE consultas SET status=? WHERE id=?",
            (novo_status, valores[0])
        )
        self.atualizar_tudo()

    def concluir_consulta(self):
        self.alterar_status("Concluída")

    def cancelar_consulta(self):
        self.alterar_status("Cancelada")

    def excluir_consulta(self):
        valores = self.selecionado(self.tree_consultas)

        if not valores:
            messagebox.showinfo("Informação", "Selecione uma consulta.")
            return

        if messagebox.askyesno("Confirmar", "Excluir esta consulta?"):
            self.db.executar(
                "DELETE FROM consultas WHERE id=?",
                (valores[0],)
            )
            self.atualizar_tudo()

    # ---------------------- RELATÓRIO ----------------------

    def mostrar_relatorio(self):
        clientes = self.db.consultar(
            "SELECT COUNT(*) FROM clientes"
        )[0][0]
        vets = self.db.consultar(
            "SELECT COUNT(*) FROM veterinarios"
        )[0][0]
        animais = self.db.consultar(
            "SELECT COUNT(*) FROM animais"
        )[0][0]
        status = dict(self.db.consultar(
            "SELECT status, COUNT(*) FROM consultas GROUP BY status"
        ))

        mensagem = (
            f"Clientes: {clientes}\n"
            f"Veterinários: {vets}\n"
            f"Animais: {animais}\n\n"
            f"Consultas agendadas: {status.get('Agendada', 0)}\n"
            f"Consultas concluídas: {status.get('Concluída', 0)}\n"
            f"Consultas canceladas: {status.get('Cancelada', 0)}"
        )

        messagebox.showinfo("Relatório geral", mensagem)

    def encerrar(self):
        self.db.fechar()
        self.destroy()


if __name__ == "__main__":
    app = VetCareApp()
    app.mainloop()