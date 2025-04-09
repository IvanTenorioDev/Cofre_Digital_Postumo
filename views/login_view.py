import tkinter as tk
from tkinter import ttk, messagebox
from views.styles import *

class LoginView(tk.Frame):
    """Tela de login para o Cofre Digital Póstumo."""
    
    def __init__(self, master, controller):
        """Inicializa a tela de login."""
        super().__init__(master, bg=BG_COLOR)
        self.controller = controller
        self.tentativas = 0
        
        # Criar interface
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria a interface da tela de login."""
        # Frame principal
        main_frame = tk.Frame(self, **FRAME_STYLE)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de login (centralizado)
        login_frame = tk.Frame(main_frame, **FRAME_STYLE)
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Título
        tk.Label(
            login_frame,
            text="Cofre Digital Póstumo",
            font=FONT_TITLE,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(pady=PADDING_LARGE)
        
        # Descrição
        self.label_modo = tk.Label(
            login_frame,
            text="Modo normal de acesso",
            font=FONT_NORMAL,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        )
        self.label_modo.pack(pady=PADDING_MEDIUM)
        
        # Frame para o formulário
        form_frame = tk.Frame(login_frame, **FRAME_STYLE)
        form_frame.pack(pady=PADDING_LARGE)
        
        # Frame para senha
        senha_frame = tk.Frame(form_frame, **FRAME_STYLE)
        senha_frame.pack(fill=tk.X, pady=PADDING_MEDIUM)
        
        # Label de senha
        tk.Label(
            senha_frame,
            text="Senha:",
            font=FONT_NORMAL,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(side=tk.LEFT, padx=(0, PADDING_SMALL))
        
        # Entrada de senha
        self.entrada_senha = tk.Entry(senha_frame, show="*", width=25, **ENTRY_STYLE)
        self.entrada_senha.pack(side=tk.LEFT, padx=PADDING_SMALL)
        self.entrada_senha.bind("<Return>", lambda e: self._autenticar())
        
        # Botão de mostrar/esconder senha
        self.mostrar_senha = tk.BooleanVar(value=False)
        
        def alternar_exibicao_senha():
            if self.mostrar_senha.get():
                self.entrada_senha.configure(show="")
            else:
                self.entrada_senha.configure(show="*")
        
        tk.Checkbutton(
            senha_frame,
            text="Mostrar",
            variable=self.mostrar_senha,
            command=alternar_exibicao_senha,
            bg=BG_COLOR
        ).pack(side=tk.LEFT, padx=PADDING_SMALL)
        
        # Botão de login
        tk.Button(
            form_frame,
            text="Entrar",
            command=self._autenticar,
            width=15,
            **BUTTON_PRIMARY_STYLE
        ).pack(pady=PADDING_MEDIUM)
        
        # Link para acessar por frase
        link_frame = tk.Frame(form_frame, **FRAME_STYLE)
        link_frame.pack(pady=PADDING_MEDIUM)
        
        tk.Label(
            link_frame,
            text="Não tem a senha? ",
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(side=tk.LEFT)
        
        link = tk.Label(
            link_frame,
            text="Acessar com frase de recuperação",
            fg=HIGHLIGHT_COLOR,
            cursor="hand2",
            bg=BG_COLOR
        )
        link.pack(side=tk.LEFT)
        link.bind("<Button-1>", lambda e: self._mostrar_dialog_frase())
        
        # Posicionar o cursor na entrada de senha
        self.entrada_senha.focus_set()
    
    def atualizar_modo_heranca(self, modo_heranca):
        """Atualiza o modo de herança na tela."""
        if modo_heranca:
            self.label_modo.config(
                text="MODO DE HERANÇA ATIVO",
                fg=ERROR_COLOR,
                font=FONT_BOLD
            )
        else:
            self.label_modo.config(
                text="Modo normal de acesso",
                fg=TEXT_COLOR,
                font=FONT_NORMAL
            )
    
    def _autenticar(self):
        """Autentica o usuário."""
        senha = self.entrada_senha.get()
        
        if not senha:
            messagebox.showerror("Erro", "Digite sua senha")
            return
        
        # Chamar o controller para autenticar
        sucesso, mensagem, modo_heranca = self.controller.autenticar(senha)
        
        if not sucesso:
            messagebox.showerror("Erro de autenticação", mensagem)
            self.tentativas += 1
            
            # Verificar limite de tentativas
            max_tentativas = self.controller.obter_configuracoes().get("max_tentativas_senha", 5)
            if self.tentativas >= max_tentativas:
                messagebox.showerror(
                    "Acesso Bloqueado",
                    f"Número máximo de tentativas ({max_tentativas}) atingido.\nO aplicativo será fechado."
                )
                self.master.destroy()
        else:
            # Limpar entrada de senha
            self.entrada_senha.delete(0, tk.END)
            self.tentativas = 0
    
    def _mostrar_dialog_frase(self):
        """Mostra o diálogo para autenticação por frase."""
        dialog = tk.Toplevel(self.master)
        dialog.title("Recuperar Acesso")
        dialog.geometry("600x300")
        dialog.transient(self.master)
        dialog.grab_set()
        dialog.configure(bg=BG_COLOR)
        
        # Frame principal
        main_frame = tk.Frame(dialog, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(
            main_frame,
            text="Recuperação de Acesso",
            font=FONT_TITLE,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(pady=PADDING_MEDIUM)
        
        # Descrição
        tk.Label(
            main_frame,
            text="Digite sua frase mnemônica de recuperação (12 palavras):",
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(pady=PADDING_SMALL)
        
        # Frame para entrada da frase
        frase_frame = tk.Frame(main_frame, bg=BG_COLOR)
        frase_frame.pack(fill=tk.X, padx=PADDING_LARGE, pady=PADDING_MEDIUM)
        
        # Entrada da frase
        frase_text = tk.Text(
            frase_frame,
            height=3,
            width=50,
            wrap=tk.WORD,
            font=FONT_NORMAL
        )
        frase_text.pack(fill=tk.X)
        frase_text.focus_set()
        
        # Frame para botões
        botoes_frame = tk.Frame(main_frame, bg=BG_COLOR)
        botoes_frame.pack(pady=PADDING_MEDIUM)
        
        # Função para autenticar com a frase
        def autenticar_com_frase():
            frase = frase_text.get("1.0", tk.END).strip()
            
            if not frase:
                messagebox.showerror("Erro", "Digite a frase de recuperação", parent=dialog)
                return
            
            # Chamar o controller para autenticar
            sucesso, mensagem, modo_heranca = self.controller.autenticar_por_frase(frase)
            
            if not sucesso:
                messagebox.showerror("Erro de autenticação", mensagem, parent=dialog)
            else:
                dialog.destroy()
        
        # Botões
        tk.Button(
            botoes_frame,
            text="Recuperar Acesso",
            command=autenticar_com_frase,
            bg=HIGHLIGHT_COLOR,
            fg="white",
            font=FONT_BOLD,
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=PADDING_SMALL)
        
        tk.Button(
            botoes_frame,
            text="Cancelar",
            command=dialog.destroy,
            bg=BUTTON_COLOR,
            fg=TEXT_COLOR,
            font=FONT_NORMAL,
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=PADDING_SMALL) 