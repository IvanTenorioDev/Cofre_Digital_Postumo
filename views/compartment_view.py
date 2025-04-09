import tkinter as tk
from tkinter import ttk, messagebox
from views.styles import *

class CompartmentView(tk.Frame):
    """Tela de compartimento para o Cofre Digital Póstumo."""
    
    def __init__(self, master, controller):
        """Inicializa a tela de compartimento."""
        super().__init__(master, bg=BG_COLOR)
        self.controller = controller
        self.compartimento_id = None
        self.modo_heranca = False
        
        # Criar interface
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria a interface da tela de compartimento."""
        # Criar menu
        self._criar_menu()
        
        # Frame principal
        main_frame = tk.Frame(self, **FRAME_STYLE)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING_LARGE, pady=PADDING_LARGE)
        
        # Cabeçalho
        header_frame = tk.Frame(main_frame, **FRAME_STYLE)
        header_frame.pack(fill=tk.X, pady=(0, PADDING_LARGE))
        
        # Título do compartimento
        self.label_titulo = tk.Label(
            header_frame,
            text="Compartimento",
            font=FONT_TITLE,
            **LABEL_STYLE
        )
        self.label_titulo.pack(anchor=tk.W)
        
        # Descrição do compartimento
        self.label_descricao = tk.Label(
            header_frame,
            text="",
            font=FONT_NORMAL,
            **LABEL_STYLE
        )
        self.label_descricao.pack(anchor=tk.W)
        
        # Frame para o aviso de modo restrito
        self.modo_restrito_frame = tk.Frame(main_frame, bg=ERROR_COLOR, padx=PADDING_LARGE, pady=PADDING_MEDIUM)
        
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
        
        # Notebook para abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=PADDING_MEDIUM)
        
        # Abas
        self.aba_senhas = tk.Frame(self.notebook, bg=BG_COLOR)
        self.aba_notas = tk.Frame(self.notebook, bg=BG_COLOR)
        self.aba_arquivos = tk.Frame(self.notebook, bg=BG_COLOR)
        self.aba_carteiras = tk.Frame(self.notebook, bg=BG_COLOR)
        
        self.notebook.add(self.aba_senhas, text="Senhas")
        self.notebook.add(self.aba_notas, text="Notas")
        self.notebook.add(self.aba_arquivos, text="Arquivos")
        self.notebook.add(self.aba_carteiras, text="Carteiras BTC")
        
        # Botão para voltar ao dashboard
        voltar_frame = tk.Frame(main_frame, **FRAME_STYLE)
        voltar_frame.pack(anchor=tk.W, pady=PADDING_MEDIUM)
        
        tk.Button(
            voltar_frame,
            text="← Voltar ao Dashboard",
            command=self._voltar_dashboard,
            **BUTTON_STYLE
        ).pack()
    
    def _criar_menu(self):
        """Cria o menu da tela de compartimento."""
        # Criar barra de menu
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)
        
        # Menu Arquivo
        arquivo_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Arquivo", menu=arquivo_menu)
        
        arquivo_menu.add_command(label="Voltar ao Dashboard", command=self._voltar_dashboard)
        arquivo_menu.add_separator()
        arquivo_menu.add_command(label="Exportar Compartimento", command=self._exportar_compartimento)
        arquivo_menu.add_separator()
        arquivo_menu.add_command(label="Sair", command=self._confirmar_saida)
        
        # Menu Ferramentas
        if not self.modo_heranca:
            ferramentas_menu = tk.Menu(menu_bar, tearoff=0)
            menu_bar.add_cascade(label="Ferramentas", menu=ferramentas_menu)
            
            ferramentas_menu.add_command(label="Gerenciar Categorias", command=self._gerenciar_categorias)
            ferramentas_menu.add_command(label="Configurações do Compartimento", command=self._configuracoes_compartimento)
    
    def carregar_compartimento(self, compartimento_id, modo_heranca=False):
        """Carrega os dados do compartimento na interface."""
        self.compartimento_id = compartimento_id
        self.modo_heranca = modo_heranca
        
        # Atualizar título
        self.label_titulo.config(text=f"Compartimento: {compartimento_id}")
        
        # Mostrar/esconder aviso de modo restrito
        if modo_heranca:
            self.modo_restrito_frame.pack(fill=tk.X, pady=PADDING_MEDIUM)
        else:
            self.modo_restrito_frame.pack_forget()
        
        # Recriar menu
        self._criar_menu()
        
        # TODO: Carregar dados do compartimento
        # Implementar carregamento de senhas, notas, arquivos e carteiras
    
    def _voltar_dashboard(self):
        """Volta para o dashboard."""
        # Mostrar dashboard
        if self.controller.view:
            self.controller.view.mostrar_dashboard(self.modo_heranca)
    
    def _exportar_compartimento(self):
        """Exporta os dados do compartimento."""
        # TODO: Implementar exportação
        messagebox.showinfo("Exportar", "Funcionalidade a ser implementada")
    
    def _gerenciar_categorias(self):
        """Abre a tela de gerenciamento de categorias."""
        # TODO: Implementar gerenciamento de categorias
        messagebox.showinfo("Categorias", "Funcionalidade a ser implementada")
    
    def _configuracoes_compartimento(self):
        """Abre a tela de configurações do compartimento."""
        # TODO: Implementar configurações
        messagebox.showinfo("Configurações", "Funcionalidade a ser implementada")
    
    def _confirmar_saida(self):
        """Confirma saída da aplicação."""
        if messagebox.askyesno("Sair", "Tem certeza que deseja sair?"):
            # Chamar logout do controller
            self.controller.logout()
            # Fechar a aplicação
            self.master.destroy() 