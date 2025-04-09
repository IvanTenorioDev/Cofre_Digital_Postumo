import tkinter as tk
from tkinter import ttk, messagebox
from views.styles import *

class SetupView(tk.Frame):
    """Tela de configuração inicial do Cofre Digital Póstumo."""
    
    def __init__(self, master, controller):
        """Inicializa a tela de configuração inicial."""
        super().__init__(master, bg=BG_COLOR)
        self.controller = controller
        
        # Criar interface
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria a interface da tela de configuração inicial."""
        # Frame principal
        main_frame = tk.Frame(self, **FRAME_STYLE)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de configuração (centralizado)
        setup_frame = tk.Frame(main_frame, **FRAME_STYLE)
        setup_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Título
        tk.Label(
            setup_frame,
            text="Configuração Inicial",
            font=FONT_TITLE,
            **LABEL_STYLE
        ).pack(pady=PADDING_LARGE)
        
        # Descrição
        tk.Label(
            setup_frame,
            text="Bem-vindo ao Cofre Digital Póstumo. Configure o usuário principal.",
            font=FONT_NORMAL,
            **LABEL_STYLE
        ).pack(pady=PADDING_MEDIUM)
        
        # Frame para o formulário
        form_frame = tk.Frame(setup_frame, **FRAME_STYLE)
        form_frame.pack(pady=PADDING_MEDIUM)
        
        # Nome
        nome_frame = tk.Frame(form_frame, **FRAME_STYLE)
        nome_frame.pack(fill=tk.X, pady=PADDING_SMALL)
        
        tk.Label(
            nome_frame,
            text="Nome:",
            width=15,
            anchor=tk.W,
            **LABEL_STYLE
        ).pack(side=tk.LEFT)
        
        entrada_nome = tk.Entry(nome_frame, width=30, **ENTRY_STYLE)
        entrada_nome.pack(side=tk.LEFT)
        entrada_nome.focus_set()
        
        # Email
        email_frame = tk.Frame(form_frame, **FRAME_STYLE)
        email_frame.pack(fill=tk.X, pady=PADDING_SMALL)
        
        tk.Label(
            email_frame,
            text="Email (opcional):",
            width=15,
            anchor=tk.W,
            **LABEL_STYLE
        ).pack(side=tk.LEFT)
        
        entrada_email = tk.Entry(email_frame, width=30, **ENTRY_STYLE)
        entrada_email.pack(side=tk.LEFT)
        
        # Senha principal
        senha_frame = tk.Frame(form_frame, **FRAME_STYLE)
        senha_frame.pack(fill=tk.X, pady=PADDING_SMALL)
        
        tk.Label(
            senha_frame,
            text="Senha principal:",
            width=15,
            anchor=tk.W,
            **LABEL_STYLE
        ).pack(side=tk.LEFT)
        
        entrada_senha = tk.Entry(senha_frame, width=30, show="*", **ENTRY_STYLE)
        entrada_senha.pack(side=tk.LEFT)
        
        # Confirmar senha principal
        conf_senha_frame = tk.Frame(form_frame, **FRAME_STYLE)
        conf_senha_frame.pack(fill=tk.X, pady=PADDING_SMALL)
        
        tk.Label(
            conf_senha_frame,
            text="Confirmar senha:",
            width=15,
            anchor=tk.W,
            **LABEL_STYLE
        ).pack(side=tk.LEFT)
        
        entrada_conf_senha = tk.Entry(conf_senha_frame, width=30, show="*", **ENTRY_STYLE)
        entrada_conf_senha.pack(side=tk.LEFT)
        
        # Separador
        ttk.Separator(form_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=PADDING_MEDIUM)
        
        # Informação sobre senha de herança
        tk.Label(
            form_frame,
            text="Senha de herança (diferente da senha principal):",
            **LABEL_STYLE
        ).pack(anchor=tk.W, pady=(PADDING_SMALL, 0))
        
        tk.Label(
            form_frame,
            text="Esta senha será usada pelos herdeiros para acessar o sistema.",
            font=FONT_SMALL,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(anchor=tk.W)
        
        # Senha de herança
        senha_heranca_frame = tk.Frame(form_frame, **FRAME_STYLE)
        senha_heranca_frame.pack(fill=tk.X, pady=PADDING_SMALL)
        
        tk.Label(
            senha_heranca_frame,
            text="Senha de herança:",
            width=15,
            anchor=tk.W,
            **LABEL_STYLE
        ).pack(side=tk.LEFT)
        
        entrada_senha_heranca = tk.Entry(senha_heranca_frame, width=30, show="*", **ENTRY_STYLE)
        entrada_senha_heranca.pack(side=tk.LEFT)
        
        # Confirmar senha de herança
        conf_senha_h_frame = tk.Frame(form_frame, **FRAME_STYLE)
        conf_senha_h_frame.pack(fill=tk.X, pady=PADDING_SMALL)
        
        tk.Label(
            conf_senha_h_frame,
            text="Confirmar herança:",
            width=15,
            anchor=tk.W,
            **LABEL_STYLE
        ).pack(side=tk.LEFT)
        
        entrada_conf_senha_h = tk.Entry(conf_senha_h_frame, width=30, show="*", **ENTRY_STYLE)
        entrada_conf_senha_h.pack(side=tk.LEFT)
        
        # Botões
        botoes_frame = tk.Frame(setup_frame, **FRAME_STYLE)
        botoes_frame.pack(pady=PADDING_LARGE)
        
        # Função para configurar usuário
        def configurar():
            nome = entrada_nome.get().strip()
            email = entrada_email.get().strip()
            senha = entrada_senha.get()
            conf_senha = entrada_conf_senha.get()
            senha_heranca = entrada_senha_heranca.get()
            conf_senha_h = entrada_conf_senha_h.get()
            
            # Validar campos
            if not nome:
                messagebox.showerror("Erro", "O nome é obrigatório")
                return
            
            if not senha:
                messagebox.showerror("Erro", "A senha principal é obrigatória")
                return
            
            if senha != conf_senha:
                messagebox.showerror("Erro", "As senhas principais não coincidem")
                return
            
            if len(senha) < 8:
                messagebox.showerror("Erro", "A senha principal deve ter pelo menos 8 caracteres")
                return
            
            if not senha_heranca:
                messagebox.showerror("Erro", "A senha de herança é obrigatória")
                return
            
            if senha_heranca != conf_senha_h:
                messagebox.showerror("Erro", "As senhas de herança não coincidem")
                return
            
            if len(senha_heranca) < 8:
                messagebox.showerror("Erro", "A senha de herança deve ter pelo menos 8 caracteres")
                return
            
            if senha == senha_heranca:
                messagebox.showerror("Erro", "A senha principal e a senha de herança não podem ser iguais")
                return
            
            # Chamar o controller para configurar o usuário
            sucesso, mensagem, _ = self.controller.configurar_usuario(nome, senha, senha_heranca, email)
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
            else:
                messagebox.showerror("Erro", mensagem)
        
        # Botões
        tk.Button(
            botoes_frame,
            text="Configurar",
            command=configurar,
            width=15,
            **BUTTON_PRIMARY_STYLE
        ).pack(pady=PADDING_MEDIUM) 