import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
from views.styles import *

class DashboardView(tk.Frame):
    """Tela principal do dashboard do Cofre Digital Póstumo."""
    
    def __init__(self, master, controller):
        """Inicializa a tela do dashboard."""
        super().__init__(master, bg=BG_COLOR)
        self.controller = controller
        self.modo_heranca = False
        self.timer_thread = None
        self.timer_ativo = True
        
        # Criar interface
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria a interface do dashboard."""
        # Menu principal
        self._criar_menu()
        
        # Frame principal
        main_frame = tk.Frame(self, **FRAME_STYLE)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING_LARGE, pady=PADDING_LARGE)
        
        # Título e subtítulo
        header_frame = tk.Frame(main_frame, **FRAME_STYLE)
        header_frame.pack(fill=tk.X, pady=(0, PADDING_LARGE))
        
        tk.Label(
            header_frame,
            text="Cofre Digital Póstumo",
            font=FONT_TITLE,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(anchor=tk.W)
        
        tk.Label(
            header_frame,
            text="Gerenciador de dados seguros",
            font=FONT_NORMAL,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(anchor=tk.W)
        
        # Frame para o conteúdo
        content_frame = tk.Frame(main_frame, **FRAME_STYLE)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para o aviso de modo restrito
        self.modo_restrito_frame = tk.Frame(content_frame, bg=ERROR_COLOR, padx=PADDING_LARGE, pady=PADDING_MEDIUM)
        
        tk.Label(
            self.modo_restrito_frame,
            text="MODO DE HERANÇA ATIVO",
            font=FONT_BOLD,
            bg=ERROR_COLOR,
            fg="white"
        ).pack()
        
        tk.Label(
            self.modo_restrito_frame,
            text="Você está no modo de acesso restrito (somente leitura).",
            bg=ERROR_COLOR,
            fg="white"
        ).pack()
        
        # Frame para estatísticas
        estatisticas_frame = tk.LabelFrame(content_frame, text="Resumo", **FRAME_STYLE)
        estatisticas_frame.pack(fill=tk.X, pady=PADDING_MEDIUM)
        
        # Grid para estatísticas
        self.grid_estatisticas = tk.Frame(estatisticas_frame, **FRAME_STYLE)
        self.grid_estatisticas.pack(fill=tk.X, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Estatísticas serão atualizadas pela função atualizar_interface
        
        # Frame para ações
        acoes_frame = tk.LabelFrame(content_frame, text="Ações", **FRAME_STYLE)
        acoes_frame.pack(fill=tk.X, pady=PADDING_MEDIUM)
        
        # Botões de ação
        botoes_frame = tk.Frame(acoes_frame, **FRAME_STYLE)
        botoes_frame.pack(fill=tk.X, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Definir botões de ação
        botoes = [
            ("Senhas", self._abrir_senhas),
            ("Notas", self._abrir_notas),
            ("Arquivos", self._abrir_arquivos),
            ("Carteiras BTC", self._abrir_carteiras),
            ("Categorias", self._abrir_categorias)
        ]
        
        for texto, comando in botoes:
            btn = tk.Button(
                botoes_frame,
                text=texto,
                command=comando,
                width=15,
                **BUTTON_STYLE
            )
            btn.pack(side=tk.LEFT, padx=PADDING_SMALL, pady=PADDING_SMALL)
        
        # Frame para compartimentos
        compartimentos_frame = tk.LabelFrame(content_frame, text="Compartimentos", **FRAME_STYLE)
        compartimentos_frame.pack(fill=tk.X, pady=PADDING_MEDIUM)
        
        # Conteúdo do frame de compartimentos
        comp_content = tk.Frame(compartimentos_frame, **FRAME_STYLE)
        comp_content.pack(fill=tk.X, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Compartimento ativo
        comp_info = tk.Frame(comp_content, **FRAME_STYLE)
        comp_info.pack(fill=tk.X, pady=PADDING_SMALL)
        
        tk.Label(
            comp_info,
            text="Compartimento ativo:",
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(side=tk.LEFT)
        
        self.label_compartimento = tk.Label(
            comp_info,
            text="principal",
            font=FONT_BOLD,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        )
        self.label_compartimento.pack(side=tk.LEFT, padx=PADDING_SMALL)
        
        # Botões de compartimento
        comp_buttons = tk.Frame(comp_content, **FRAME_STYLE)
        comp_buttons.pack(fill=tk.X, pady=PADDING_SMALL)
        
        # Definir botões de compartimento
        comp_acoes = [
            ("Criar Compartimento", self._criar_compartimento),
            ("Alternar Compartimento", self._alternar_compartimento),
            ("Acessar por Frase", self._acessar_por_frase)
        ]
        
        for texto, comando in comp_acoes:
            btn = tk.Button(
                comp_buttons,
                text=texto,
                command=comando,
                **BUTTON_STYLE
            )
            btn.pack(side=tk.LEFT, padx=PADDING_SMALL, pady=PADDING_SMALL)
        
        # Frame do timer
        timer_frame = tk.LabelFrame(content_frame, text="Status", **FRAME_STYLE)
        timer_frame.pack(fill=tk.X, pady=PADDING_MEDIUM)
        
        # Conteúdo do timer
        timer_content = tk.Frame(timer_frame, **FRAME_STYLE)
        timer_content.pack(fill=tk.X, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Label para o texto do timer
        self.label_timer_texto = tk.Label(
            timer_content,
            text="Tempo restante até ativação do modo de herança:",
            fg=TEXT_COLOR,
            bg=BG_COLOR
        )
        self.label_timer_texto.pack()
        
        # Label para o contador
        self.label_timer = tk.Label(
            timer_content,
            text="Carregando...",
            font=FONT_TITLE,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        )
        self.label_timer.pack(pady=PADDING_MEDIUM)
        
        # Botão para renovar período
        self.btn_renovar = tk.Button(
            timer_content,
            text="Renovar Período",
            command=self._renovar_periodo,
            **BUTTON_PRIMARY_STYLE
        )
        self.btn_renovar.pack(pady=PADDING_SMALL)
        
        # Iniciar o timer
        self._iniciar_timer()
    
    def _criar_menu(self):
        """Cria o menu principal."""
        # Criar barra de menu
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)
        
        # Menu Arquivo
        arquivo_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Arquivo", menu=arquivo_menu)
        
        arquivo_menu.add_command(label="Backup", command=self._fazer_backup)
        arquivo_menu.add_command(label="Restaurar", command=self._restaurar)
        arquivo_menu.add_separator()
        arquivo_menu.add_command(label="Sair", command=self._confirmar_saida)
        
        # Menu Configurações
        config_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Configurações", menu=config_menu)
        
        config_menu.add_command(label="Preferências", command=self._abrir_preferencias)
        config_menu.add_command(label="Alterar Senhas", command=self._alterar_senhas)
        
        # Menu Ajuda
        ajuda_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Ajuda", menu=ajuda_menu)
        
        ajuda_menu.add_command(label="Sobre", command=self._mostrar_sobre)
        ajuda_menu.add_command(label="Instruções", command=self._mostrar_instrucoes)
    
    def atualizar_interface(self, modo_heranca=False):
        """Atualiza a interface com base no estado do sistema."""
        self.modo_heranca = modo_heranca
        
        # Atualizar estado do modo de herança
        if modo_heranca:
            self.modo_restrito_frame.pack(fill=tk.X, pady=PADDING_MEDIUM)
            self.label_timer_texto.config(text="Acesso restrito ao compartimento atual")
            self.btn_renovar.pack_forget()  # Esconder botão de renovar período
        else:
            self.modo_restrito_frame.pack_forget()
            self.label_timer_texto.config(text="Tempo restante até ativação do modo de herança:")
            self.btn_renovar.pack(pady=PADDING_SMALL)  # Mostrar botão de renovar período
        
        # Atualizar estatísticas
        self._atualizar_estatisticas()
        
        # Atualizar timer
        self._atualizar_timer()
    
    def _atualizar_estatisticas(self):
        """Atualiza as estatísticas exibidas."""
        # Remover widgets existentes
        for widget in self.grid_estatisticas.winfo_children():
            widget.destroy()
        
        # Obter estatísticas
        estatisticas = self.controller.verificar_status_sistema()["estatisticas"]
        
        # Criar cards de estatísticas
        itens = [
            ("Senhas", estatisticas.get("senhas", 0)),
            ("Notas", estatisticas.get("notas", 0)),
            ("Arquivos", estatisticas.get("arquivos", 0)),
            ("Carteiras BTC", estatisticas.get("carteiras_btc", 0))
        ]
        
        # Criar grid
        for i, (titulo, valor) in enumerate(itens):
            card = tk.Frame(self.grid_estatisticas, **CARD_STYLE)
            card.grid(row=0, column=i, padx=PADDING_MEDIUM, pady=PADDING_SMALL)
            
            tk.Label(
                card,
                text=titulo,
                font=FONT_BOLD,
                fg=TEXT_COLOR,
                bg=FRAME_COLOR
            ).pack(pady=(PADDING_SMALL, 0))
            
            tk.Label(
                card,
                text=str(valor),
                font=FONT_TITLE,
                fg=TEXT_COLOR,
                bg=FRAME_COLOR
            ).pack(pady=PADDING_SMALL)
    
    def _iniciar_timer(self):
        """Inicia o timer para atualização automática."""
        def timer_loop():
            while self.timer_ativo:
                self._atualizar_timer()
                time.sleep(1)  # Atualizar a cada segundo
        
        # Iniciar thread do timer
        self.timer_thread = threading.Thread(target=timer_loop, daemon=True)
        self.timer_thread.start()
    
    def _atualizar_timer(self):
        """Atualiza o timer exibido."""
        if not self.timer_ativo:
            return
        
        if self.modo_heranca:
            # Modo de herança ativo
            self.label_timer.config(
                text="HERANÇA ATIVADA",
                fg=ERROR_COLOR
            )
        else:
            # Verificar dias restantes
            dias_restantes = self.controller.verificar_status_sistema()["dias_restantes"]
            nivel, _ = self.controller.verificar_importancia_renovacao()
            
            if dias_restantes <= 0:
                # Expirado
                self.label_timer.config(
                    text="EXPIRADO!",
                    fg=ERROR_COLOR
                )
            else:
                # Formatar texto
                if dias_restantes == 1:
                    texto = "1 dia"
                else:
                    texto = f"{dias_restantes} dias"
                
                # Definir cor baseada na urgência
                if nivel == "urgente":
                    cor = ERROR_COLOR
                elif nivel == "aviso":
                    cor = WARNING_COLOR
                else:
                    cor = TEXT_COLOR
                
                # Atualizar label
                self.label_timer.config(
                    text=texto,
                    fg=cor
                )
    
    def atualizar_compartimento(self, compartimento_id):
        """Atualiza o compartimento ativo exibido."""
        self.label_compartimento.config(text=compartimento_id)
        self._atualizar_estatisticas()
    
    def destroy(self):
        """Sobrescreve o método destroy para parar o timer."""
        self.timer_ativo = False
        super().destroy()
    
    # === Funções de ação ===
    
    def _renovar_periodo(self):
        """Renova o período de confirmação."""
        # Pedir confirmação
        confirmacao = messagebox.askyesno(
            "Renovar Período",
            "Deseja renovar o período de confirmação agora?"
        )
        
        if confirmacao:
            # Chamar o controller para renovar o período
            sucesso, mensagem = self.controller.renovar_periodo()
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self._atualizar_timer()
            else:
                messagebox.showerror("Erro", mensagem)
    
    def _criar_compartimento(self):
        """Abre o diálogo para criar um novo compartimento."""
        if self.modo_heranca:
            messagebox.showerror(
                "Acesso Negado",
                "Não é possível criar compartimentos no modo de herança."
            )
            return
        
        # Criar diálogo
        dialog = tk.Toplevel(self.master)
        dialog.title("Criar Compartimento")
        dialog.geometry("500x300")
        dialog.transient(self.master)
        dialog.grab_set()
        dialog.configure(bg=BG_COLOR)
        
        # Título
        tk.Label(
            dialog,
            text="Criar Novo Compartimento",
            font=FONT_SUBTITLE,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(pady=PADDING_MEDIUM)
        
        # Frame do formulário
        form_frame = tk.Frame(dialog, **FRAME_STYLE)
        form_frame.pack(padx=PADDING_LARGE, pady=PADDING_MEDIUM)
        
        # Nome
        nome_frame = tk.Frame(form_frame, **FRAME_STYLE)
        nome_frame.pack(fill=tk.X, pady=PADDING_SMALL)
        
        tk.Label(
            nome_frame,
            text="Nome:",
            width=10,
            anchor=tk.W,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(side=tk.LEFT)
        
        entrada_nome = tk.Entry(nome_frame, width=30, **ENTRY_STYLE)
        entrada_nome.pack(side=tk.LEFT, padx=PADDING_SMALL)
        entrada_nome.focus_set()
        
        # Senha
        senha_frame = tk.Frame(form_frame, **FRAME_STYLE)
        senha_frame.pack(fill=tk.X, pady=PADDING_SMALL)
        
        tk.Label(
            senha_frame,
            text="Senha:",
            width=10,
            anchor=tk.W,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(side=tk.LEFT)
        
        entrada_senha = tk.Entry(senha_frame, width=30, show="*", **ENTRY_STYLE)
        entrada_senha.pack(side=tk.LEFT, padx=PADDING_SMALL)
        
        # Confirmar senha
        conf_senha_frame = tk.Frame(form_frame, **FRAME_STYLE)
        conf_senha_frame.pack(fill=tk.X, pady=PADDING_SMALL)
        
        tk.Label(
            conf_senha_frame,
            text="Confirmar:",
            width=10,
            anchor=tk.W,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(side=tk.LEFT)
        
        entrada_conf_senha = tk.Entry(conf_senha_frame, width=30, show="*", **ENTRY_STYLE)
        entrada_conf_senha.pack(side=tk.LEFT, padx=PADDING_SMALL)
        
        # Descrição
        desc_frame = tk.Frame(form_frame, **FRAME_STYLE)
        desc_frame.pack(fill=tk.X, pady=PADDING_SMALL)
        
        tk.Label(
            desc_frame,
            text="Descrição:",
            width=10,
            anchor=tk.W,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(side=tk.LEFT)
        
        entrada_desc = tk.Entry(desc_frame, width=30, **ENTRY_STYLE)
        entrada_desc.pack(side=tk.LEFT, padx=PADDING_SMALL)
        
        # Botões
        botoes_frame = tk.Frame(dialog, **FRAME_STYLE)
        botoes_frame.pack(pady=PADDING_MEDIUM)
        
        # Função para criar compartimento
        def criar():
            nome = entrada_nome.get().strip()
            senha = entrada_senha.get()
            conf_senha = entrada_conf_senha.get()
            descricao = entrada_desc.get().strip()
            
            # Validar campos
            if not nome:
                messagebox.showerror("Erro", "O nome é obrigatório", parent=dialog)
                return
            
            if not senha:
                messagebox.showerror("Erro", "A senha é obrigatória", parent=dialog)
                return
            
            if senha != conf_senha:
                messagebox.showerror("Erro", "As senhas não coincidem", parent=dialog)
                return
            
            # Chamar o controller para criar o compartimento
            sucesso, mensagem, frase = self.controller.criar_compartimento(nome, senha, descricao)
            
            if sucesso:
                dialog.destroy()
                self._atualizar_estatisticas()
            else:
                messagebox.showerror("Erro", mensagem, parent=dialog)
        
        # Botões
        tk.Button(
            botoes_frame,
            text="Criar",
            command=criar,
            **BUTTON_PRIMARY_STYLE
        ).pack(side=tk.LEFT, padx=PADDING_SMALL)
        
        tk.Button(
            botoes_frame,
            text="Cancelar",
            command=dialog.destroy,
            **BUTTON_STYLE
        ).pack(side=tk.LEFT, padx=PADDING_SMALL)
    
    def _alternar_compartimento(self):
        """Abre o diálogo para alternar entre compartimentos."""
        if self.modo_heranca:
            messagebox.showerror(
                "Acesso Negado",
                "Não é possível alternar compartimentos no modo de herança."
            )
            return
        
        # Obter lista de compartimentos
        sucesso, mensagem, compartimentos = self.controller.listar_compartimentos()
        
        if not sucesso:
            messagebox.showerror("Erro", mensagem)
            return
        
        if not compartimentos:
            messagebox.showinfo(
                "Informação",
                "Não há compartimentos disponíveis. Crie um novo compartimento primeiro."
            )
            return
        
        # Criar diálogo
        dialog = tk.Toplevel(self.master)
        dialog.title("Alternar Compartimento")
        dialog.geometry("550x350")
        dialog.transient(self.master)
        dialog.grab_set()
        dialog.configure(bg=BG_COLOR)
        
        # Título
        tk.Label(
            dialog,
            text="Selecione um Compartimento",
            font=FONT_SUBTITLE,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(pady=PADDING_MEDIUM)
        
        # Frame da lista
        lista_frame = tk.Frame(dialog, **FRAME_STYLE)
        lista_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING_LARGE, pady=PADDING_MEDIUM)
        
        # Criar Treeview
        colunas = ("Nome", "ID", "Descrição", "Criação")
        tree = ttk.Treeview(lista_frame, columns=colunas, show="headings", height=8)
        
        # Definir cabeçalhos
        tree.heading("Nome", text="Nome")
        tree.heading("ID", text="ID")
        tree.heading("Descrição", text="Descrição")
        tree.heading("Criação", text="Data de Criação")
        
        # Definir larguras
        tree.column("Nome", width=120)
        tree.column("ID", width=100)
        tree.column("Descrição", width=150)
        tree.column("Criação", width=120)
        
        # Preencher dados
        for comp in compartimentos:
            descricao = comp.get("descricao") or ""
            if len(descricao) > 30:
                descricao = descricao[:27] + "..."
            
            tree.insert("", tk.END, values=(
                comp.get("nome"),
                comp.get("compartimento_id"),
                descricao,
                comp.get("data_criacao", "").split("T")[0]
            ))
        
        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(lista_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame para senha
        senha_frame = tk.Frame(dialog, **FRAME_STYLE)
        senha_frame.pack(fill=tk.X, padx=PADDING_LARGE, pady=PADDING_SMALL)
        
        tk.Label(
            senha_frame,
            text="Senha:",
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(side=tk.LEFT)
        
        entrada_senha = tk.Entry(senha_frame, show="*", width=25, **ENTRY_STYLE)
        entrada_senha.pack(side=tk.LEFT, padx=PADDING_SMALL)
        
        # Botões
        botoes_frame = tk.Frame(dialog, **FRAME_STYLE)
        botoes_frame.pack(pady=PADDING_MEDIUM)
        
        # Função para alternar
        def alternar():
            selecao = tree.selection()
            if not selecao:
                messagebox.showerror("Erro", "Selecione um compartimento", parent=dialog)
                return
            
            # Obter ID do compartimento selecionado
            item = tree.item(selecao[0])
            compartimento_id = item["values"][1]
            
            # Obter senha
            senha = entrada_senha.get()
            if not senha:
                messagebox.showerror("Erro", "Digite a senha", parent=dialog)
                return
            
            # Chamar o controller para alternar
            sucesso, mensagem = self.controller.alternar_compartimento(compartimento_id, senha)
            
            if sucesso:
                dialog.destroy()
                messagebox.showinfo("Sucesso", mensagem)
                self._atualizar_estatisticas()
            else:
                messagebox.showerror("Erro", mensagem, parent=dialog)
        
        # Botões
        tk.Button(
            botoes_frame,
            text="Alternar",
            command=alternar,
            **BUTTON_PRIMARY_STYLE
        ).pack(side=tk.LEFT, padx=PADDING_SMALL)
        
        tk.Button(
            botoes_frame,
            text="Cancelar",
            command=dialog.destroy,
            **BUTTON_STYLE
        ).pack(side=tk.LEFT, padx=PADDING_SMALL)
    
    def _acessar_por_frase(self):
        """Abre o diálogo para acessar um compartimento por frase."""
        messagebox.showinfo(
            "Em desenvolvimento",
            "O acesso a compartimentos por frase será implementado em uma versão futura."
        )
    
    def _abrir_senhas(self):
        """Abre a tela de gerenciamento de senhas."""
        messagebox.showinfo(
            "Em desenvolvimento",
            "O gerenciamento de senhas será implementado em uma versão futura."
        )
    
    def _abrir_notas(self):
        """Abre a tela de gerenciamento de notas."""
        messagebox.showinfo(
            "Em desenvolvimento",
            "O gerenciamento de notas será implementado em uma versão futura."
        )
    
    def _abrir_arquivos(self):
        """Abre a tela de gerenciamento de arquivos."""
        messagebox.showinfo(
            "Em desenvolvimento",
            "O gerenciamento de arquivos será implementado em uma versão futura."
        )
    
    def _abrir_carteiras(self):
        """Abre a tela de gerenciamento de carteiras BTC."""
        messagebox.showinfo(
            "Em desenvolvimento",
            "O gerenciamento de carteiras Bitcoin será implementado em uma versão futura."
        )
    
    def _abrir_categorias(self):
        """Abre a tela de gerenciamento de categorias."""
        messagebox.showinfo(
            "Em desenvolvimento",
            "O gerenciamento de categorias será implementado em uma versão futura."
        )
    
    def _fazer_backup(self):
        """Realiza backup do sistema."""
        messagebox.showinfo(
            "Em desenvolvimento",
            "A funcionalidade de backup será implementada em uma versão futura."
        )
    
    def _restaurar(self):
        """Restaura backup do sistema."""
        messagebox.showinfo(
            "Em desenvolvimento",
            "A funcionalidade de restauração de backup será implementada em uma versão futura."
        )
    
    def _abrir_preferencias(self):
        """Abre a tela de preferências."""
        messagebox.showinfo(
            "Em desenvolvimento",
            "As configurações de preferências serão implementadas em uma versão futura."
        )
    
    def _alterar_senhas(self):
        """Abre a tela para alterar senhas."""
        messagebox.showinfo(
            "Em desenvolvimento",
            "A funcionalidade de alteração de senhas será implementada em uma versão futura."
        )
    
    def _mostrar_sobre(self):
        """Mostra informações sobre o aplicativo."""
        messagebox.showinfo(
            "Sobre",
            "Cofre Digital Póstumo\n\n"
            "Versão 1.0\n\n"
            "Um sistema seguro para armazenar e transmitir informações sensíveis para herdeiros."
        )
    
    def _mostrar_instrucoes(self):
        """Mostra instruções de uso."""
        messagebox.showinfo(
            "Instruções",
            "Este cofre digital permite armazenar e proteger dados sensíveis, "
            "como senhas, notas e frases mnemônicas de carteiras Bitcoin.\n\n"
            "Caso o período de confirmação expire sem renovação, "
            "o modo de herança será automaticamente ativado, "
            "permitindo acesso restrito aos herdeiros designados."
        )
    
    def _confirmar_saida(self):
        """Confirma saída da aplicação."""
        if messagebox.askyesno("Sair", "Tem certeza que deseja sair?"):
            # Parar o timer
            self.timer_ativo = False
            # Chamar logout do controller
            self.controller.logout()
            # Fechar a aplicação
            self.master.destroy() 