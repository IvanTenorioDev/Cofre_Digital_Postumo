import tkinter as tk
from tkinter import ttk, messagebox
from views.styles import *

class RecoveryView(tk.Frame):
    """Tela de exibição da frase de recuperação."""
    
    def __init__(self, master, controller):
        """Inicializa a tela de frase de recuperação."""
        super().__init__(master, bg=BG_COLOR)
        self.controller = controller
        self.frase = None
        
        # Criar interface
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria a interface da tela de frase de recuperação."""
        # Frame principal
        main_frame = tk.Frame(self, **FRAME_STYLE)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame central
        central_frame = tk.Frame(main_frame, **FRAME_STYLE)
        central_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Título
        tk.Label(
            central_frame,
            text="IMPORTANTE: GUARDE SUA FRASE DE RECUPERAÇÃO",
            font=FONT_TITLE,
            fg=HIGHLIGHT_COLOR,
            **LABEL_STYLE
        ).pack(pady=PADDING_LARGE)
        
        # Descrição
        tk.Label(
            central_frame,
            text="Esta é sua frase mnemônica BIP39 de recuperação.\n"
                 "Anote-a em um lugar seguro. Ela será necessária para recuperar\n"
                 "o acesso ao sistema caso você esqueça suas senhas.",
            font=FONT_NORMAL,
            justify=tk.CENTER,
            **LABEL_STYLE
        ).pack(pady=PADDING_MEDIUM)
        
        # Frame para a frase
        frase_frame = tk.Frame(central_frame, bg=FRAME_COLOR, relief=tk.RAISED, bd=1)
        frase_frame.pack(pady=PADDING_LARGE)
        
        # Caixa de texto para a frase
        self.frase_text = tk.Text(
            frase_frame,
            height=3,
            width=60,
            font=FONT_BOLD,
            bg="white",
            relief=tk.SUNKEN,
            bd=1,
            padx=PADDING_MEDIUM,
            pady=PADDING_MEDIUM,
            wrap=tk.WORD
        )
        self.frase_text.pack(padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Botão para copiar
        def copiar_frase():
            if self.frase:
                self.master.clipboard_clear()
                self.master.clipboard_append(self.frase)
                messagebox.showinfo("Copiado", "Frase copiada para a área de transferência")
        
        tk.Button(
            central_frame,
            text="Copiar Frase",
            command=copiar_frase,
            **BUTTON_PRIMARY_STYLE
        ).pack(pady=PADDING_MEDIUM)
        
        # Aviso importante
        aviso_frame = tk.Frame(central_frame, bg="#ffedeb", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        aviso_frame.pack(fill=tk.X, pady=PADDING_MEDIUM)
        
        tk.Label(
            aviso_frame,
            text="⚠️ AVISO IMPORTANTE",
            font=FONT_BOLD,
            fg=ERROR_COLOR,
            bg="#ffedeb"
        ).pack()
        
        tk.Label(
            aviso_frame,
            text="• Esta frase NÃO será mostrada novamente\n"
                 "• Guarde-a em um local físico seguro\n"
                 "• Não compartilhe com ninguém\n"
                 "• Quem possuir esta frase terá acesso ao seu cofre",
            justify=tk.LEFT,
            bg="#ffedeb",
            fg=TEXT_COLOR
        ).pack()
        
        # Botão para continuar
        tk.Button(
            central_frame,
            text="Entendi e Guardei a Frase",
            command=self._continuar,
            **BUTTON_STYLE
        ).pack(pady=PADDING_LARGE)
    
    def mostrar_frase(self, frase):
        """Mostra a frase mnemônica na interface."""
        self.frase = frase
        
        # Limpar e inserir a frase
        self.frase_text.config(state=tk.NORMAL)
        self.frase_text.delete("1.0", tk.END)
        self.frase_text.insert(tk.END, frase)
        self.frase_text.config(state=tk.DISABLED)
    
    def _continuar(self):
        """Continua para a próxima tela após o usuário confirmar."""
        # Confirmar que o usuário guardou a frase
        confirmacao = messagebox.askyesno(
            "Confirmação",
            "Você realmente guardou a frase em um local seguro?\n\n"
            "Esta frase não será mostrada novamente e é essencial para recuperação."
        )
        
        if confirmacao:
            # Mostrar tela de login
            self.controller.iniciar_sistema() 