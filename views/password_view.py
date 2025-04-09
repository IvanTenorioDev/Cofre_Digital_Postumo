import tkinter as tk
from tkinter import ttk, messagebox
from views.styles import *

class PasswordView(tk.Frame):
    """View para gerenciamento de senhas."""
    
    def __init__(self, master, controller):
        """Inicializa a view de senhas."""
        super().__init__(master, bg=BG_COLOR)
        self.controller = controller
        self.master = master
        
        # Criar a interface
        self._criar_interface()
        
        # Carregar dados iniciais
        self._carregar_senhas()
    
    def _criar_interface(self):
        """Cria a interface da view de senhas."""
        # Frame principal
        main_frame = tk.Frame(self, **FRAME_STYLE)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING_LARGE, pady=PADDING_LARGE)
        
        # Título e botões de ação
        header_frame = tk.Frame(main_frame, **FRAME_STYLE)
        header_frame.pack(fill=tk.X, pady=(0, PADDING_LARGE))
        
        # Título
        tk.Label(
            header_frame,
            text="Gerenciamento de Senhas",
            font=FONT_TITLE,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(side=tk.LEFT)
        
        # Botões
        buttons_frame = tk.Frame(header_frame, **FRAME_STYLE)
        buttons_frame.pack(side=tk.RIGHT)
        
        # Botão de adicionar
        self.btn_adicionar = tk.Button(
            buttons_frame,
            text="Adicionar Senha",
            command=self._adicionar_senha,
            **BUTTON_PRIMARY_STYLE
        )
        self.btn_adicionar.pack(side=tk.LEFT, padx=PADDING_SMALL)
        
        # Botão de voltar
        self.btn_voltar = tk.Button(
            buttons_frame,
            text="Voltar ao Dashboard",
            command=self._voltar_dashboard,
            **BUTTON_STYLE
        )
        self.btn_voltar.pack(side=tk.LEFT, padx=PADDING_SMALL)
        
        # Frame para a lista de senhas
        list_frame = tk.Frame(main_frame, **FRAME_STYLE)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Criar a tabela
        columns = ("id", "titulo", "usuario", "url", "categoria", "data_criacao")
        self.tabela = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Configurar cabeçalhos
        self.tabela.heading("id", text="ID")
        self.tabela.heading("titulo", text="Título")
        self.tabela.heading("usuario", text="Usuário")
        self.tabela.heading("url", text="URL")
        self.tabela.heading("categoria", text="Categoria")
        self.tabela.heading("data_criacao", text="Data de Criação")
        
        # Configurar colunas
        self.tabela.column("id", width=50)
        self.tabela.column("titulo", width=200)
        self.tabela.column("usuario", width=150)
        self.tabela.column("url", width=200)
        self.tabela.column("categoria", width=100)
        self.tabela.column("data_criacao", width=150)
        
        # Adicionar barra de rolagem
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tabela.yview)
        self.tabela.configure(yscroll=scrollbar.set)
        
        # Posicionar tabela e scrollbar
        self.tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar evento de duplo clique na tabela
        self.tabela.bind("<Double-1>", self._visualizar_senha)
        
        # Frame para detalhes e ações específicas
        self.detalhes_frame = tk.LabelFrame(main_frame, text="Detalhes da Senha", **FRAME_STYLE)
        self.detalhes_frame.pack(fill=tk.X, pady=PADDING_MEDIUM)
        
        # Inicialmente vazio
        tk.Label(
            self.detalhes_frame,
            text="Selecione uma senha para ver detalhes",
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(pady=PADDING_MEDIUM)
    
    def _carregar_senhas(self):
        """Carrega as senhas do compartimento atual."""
        # Limpar tabela
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        
        # Tentar carregar senhas
        try:
            senhas = self.controller.listar_senhas()
            
            # Se não há senhas, mostrar mensagem
            if not senhas:
                messagebox.showinfo("Informação", "Não há senhas cadastradas.")
                return
            
            # Adicionar senhas à tabela
            for senha in senhas:
                # Extrair valores das colunas existentes
                valores = []
                for coluna in ["id", "titulo", "usuario", "url", "categoria", "data_criacao"]:
                    if coluna == "id":
                        valores.append(senha.get(coluna, ""))
                    elif coluna not in senha or senha[coluna] is None:
                        valores.append("-")
                    else:
                        valores.append(senha[coluna])
                        
                # Formatando para exibição
                self.tabela.insert("", tk.END, values=valores)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar senhas: {str(e)}")
    
    def _adicionar_senha(self):
        """Abre diálogo para adicionar uma nova senha."""
        dialog = tk.Toplevel(self.master)
        dialog.title("Adicionar Nova Senha")
        dialog.geometry("500x400")
        dialog.transient(self.master)
        dialog.grab_set()
        dialog.configure(bg=BG_COLOR)
        
        # Frame principal
        main_frame = tk.Frame(dialog, **FRAME_STYLE)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING_LARGE, pady=PADDING_LARGE)
        
        # Título
        tk.Label(
            main_frame,
            text="Adicionar Nova Senha",
            font=FONT_SUBTITLE,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(pady=PADDING_MEDIUM)
        
        # Formulário
        form_frame = tk.Frame(main_frame, **FRAME_STYLE)
        form_frame.pack(fill=tk.X)
        
        # Campos do formulário
        campos = [
            ("Título:", "titulo"),
            ("Usuário:", "usuario"),
            ("Senha:", "senha"),
            ("URL:", "url"),
            ("Categoria:", "categoria"),
            ("Notas:", "notas")
        ]
        
        # Dicionário para armazenar as entradas
        entradas = {}
        
        # Criar campos
        for i, (label_text, campo) in enumerate(campos):
            frame = tk.Frame(form_frame, **FRAME_STYLE)
            frame.pack(fill=tk.X, pady=PADDING_SMALL)
            
            tk.Label(
                frame,
                text=label_text,
                width=10,
                anchor=tk.W,
                fg=TEXT_COLOR,
                bg=BG_COLOR
            ).pack(side=tk.LEFT)
            
            # Se for campo de senha, usar entrada com máscara
            if campo == "senha":
                entrada = tk.Entry(frame, show="*", width=30, **ENTRY_STYLE)
                entrada.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Variável para controlar exibição da senha
                mostrar_senha = tk.BooleanVar(value=False)
                
                def alternar_exibicao_senha():
                    entrada.configure(show="" if mostrar_senha.get() else "*")
                
                # Checkbox para mostrar/esconder senha
                tk.Checkbutton(
                    frame,
                    text="Mostrar",
                    variable=mostrar_senha,
                    command=alternar_exibicao_senha,
                    bg=BG_COLOR
                ).pack(side=tk.LEFT, padx=PADDING_SMALL)
                
            # Se for campo de notas, usar Text
            elif campo == "notas":
                entrada = tk.Text(frame, height=4, width=30, **ENTRY_STYLE)
                entrada.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
            # Demais campos são Entry padrão
            else:
                entrada = tk.Entry(frame, width=30, **ENTRY_STYLE)
                entrada.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Armazenar referência à entrada
            entradas[campo] = entrada
        
        # Botões
        botoes_frame = tk.Frame(main_frame, **FRAME_STYLE)
        botoes_frame.pack(pady=PADDING_LARGE)
        
        def salvar_senha():
            # Coletar dados do formulário
            dados = {}
            for campo, entrada in entradas.items():
                if campo == "notas":
                    dados[campo] = entrada.get("1.0", tk.END).strip()
                else:
                    dados[campo] = entrada.get().strip()
            
            # Validar campos obrigatórios
            if not dados["titulo"] or not dados["senha"]:
                messagebox.showerror("Erro", "Título e senha são campos obrigatórios.", parent=dialog)
                return
            
            # Chamar o controller para salvar
            try:
                sucesso, mensagem = self.controller.adicionar_senha(
                    titulo=dados["titulo"],
                    usuario=dados["usuario"],
                    senha=dados["senha"],
                    url=dados["url"],
                    categoria=dados["categoria"],
                    notas=dados["notas"]
                )
                
                if sucesso:
                    messagebox.showinfo("Sucesso", mensagem, parent=dialog)
                    dialog.destroy()
                    # Recarregar senhas
                    self._carregar_senhas()
                else:
                    messagebox.showerror("Erro", mensagem, parent=dialog)
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar senha: {str(e)}", parent=dialog)
        
        # Botão de salvar
        tk.Button(
            botoes_frame,
            text="Salvar",
            command=salvar_senha,
            **BUTTON_PRIMARY_STYLE
        ).pack(side=tk.LEFT, padx=PADDING_SMALL)
        
        # Botão de cancelar
        tk.Button(
            botoes_frame,
            text="Cancelar",
            command=dialog.destroy,
            **BUTTON_STYLE
        ).pack(side=tk.LEFT, padx=PADDING_SMALL)
    
    def _visualizar_senha(self, event):
        """Exibe os detalhes da senha selecionada."""
        # Obter item selecionado
        selection = self.tabela.selection()
        if not selection:
            return
        
        # Obter valores
        item = self.tabela.item(selection[0])
        valores = item["values"]
        
        # ID da senha
        senha_id = valores[0]
        
        # Buscar detalhes completos
        try:
            senha = self.controller.obter_senha(senha_id)
            
            # Limpar frame de detalhes
            for widget in self.detalhes_frame.winfo_children():
                widget.destroy()
            
            # Criar grid para detalhes
            detalhes_grid = tk.Frame(self.detalhes_frame, **FRAME_STYLE)
            detalhes_grid.pack(fill=tk.X, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
            
            # Mostrar detalhes
            campos_para_mostrar = []
            for campo, rotulo in [
                ("titulo", "Título:"),
                ("usuario", "Usuário:"),
                ("url", "URL:"),
                ("categoria", "Categoria:"),
                ("notas", "Notas:"),
                ("data_criacao", "Data de Criação:"),
                ("data_modificacao", "Data de Modificação:")
            ]:
                if campo in senha and senha[campo]:
                    campos_para_mostrar.append((rotulo, senha[campo]))
            
            for i, (rotulo, valor) in enumerate(campos_para_mostrar):
                tk.Label(
                    detalhes_grid,
                    text=rotulo,
                    font=FONT_BOLD,
                    fg=TEXT_COLOR,
                    bg=BG_COLOR
                ).grid(row=i, column=0, sticky=tk.W, padx=PADDING_SMALL, pady=2)
                
                tk.Label(
                    detalhes_grid,
                    text=valor,
                    fg=TEXT_COLOR,
                    bg=BG_COLOR
                ).grid(row=i, column=1, sticky=tk.W, padx=PADDING_SMALL, pady=2)
            
            # Frame para botões de ação
            acoes_frame = tk.Frame(self.detalhes_frame, **FRAME_STYLE)
            acoes_frame.pack(pady=PADDING_MEDIUM)
            
            # Botão para mostrar senha
            def mostrar_senha():
                if 'senha' in senha:
                    messagebox.showinfo("Senha", f"Senha: {senha['senha']}", parent=self.master)
                else:
                    messagebox.showinfo("Senha", "Senha não disponível ou criptografada", parent=self.master)
            
            tk.Button(
                acoes_frame,
                text="Mostrar Senha",
                command=mostrar_senha,
                **BUTTON_STYLE
            ).pack(side=tk.LEFT, padx=PADDING_SMALL)
            
            # Botão para editar
            def editar_senha():
                # Implementar edição
                messagebox.showinfo("Em breve", "Edição de senhas será implementada em breve.", parent=self.master)
            
            tk.Button(
                acoes_frame,
                text="Editar",
                command=editar_senha,
                **BUTTON_STYLE
            ).pack(side=tk.LEFT, padx=PADDING_SMALL)
            
            # Botão para excluir
            def excluir_senha():
                titulo_senha = senha.get('titulo', 'selecionada')
                if messagebox.askyesno("Confirmar Exclusão", 
                                       f"Tem certeza que deseja excluir a senha '{titulo_senha}'?", 
                                       parent=self.master):
                    try:
                        sucesso, mensagem = self.controller.excluir_senha(senha_id)
                        
                        if sucesso:
                            messagebox.showinfo("Sucesso", mensagem, parent=self.master)
                            # Limpar detalhes
                            for widget in self.detalhes_frame.winfo_children():
                                widget.destroy()
                            # Recarregar senhas
                            self._carregar_senhas()
                        else:
                            messagebox.showerror("Erro", mensagem, parent=self.master)
                            
                    except Exception as e:
                        messagebox.showerror("Erro", f"Erro ao excluir senha: {str(e)}", parent=self.master)
            
            tk.Button(
                acoes_frame,
                text="Excluir",
                command=excluir_senha,
                **BUTTON_DANGER_STYLE
            ).pack(side=tk.LEFT, padx=PADDING_SMALL)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar detalhes da senha: {str(e)}")
    
    def _voltar_dashboard(self):
        """Volta para o dashboard."""
        # Chamar controller para voltar ao dashboard
        self.controller.voltar_para_dashboard() 