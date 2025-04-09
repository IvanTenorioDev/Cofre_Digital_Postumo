import tkinter as tk
from tkinter import ttk
import time
from styles import *

class CustomDialog:
    """Base para diálogos personalizados"""
    def __init__(self, parent, title, message, icon_type=None):
        self.parent = parent
        self.result = None
        
        # Criar janela de diálogo
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("")
        self.dialog.configure(bg=DARK_BG)
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Remover decorações de janela padrão (opcional)
        self.dialog.overrideredirect(True)
        
        # Configurar frame principal
        self.frame = tk.Frame(self.dialog, bg=DARK_BG, padx=20, pady=20)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho
        header_frame = tk.Frame(self.frame, bg=DARK_BG)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Ícone baseado no tipo
        icon_color = BLUE_PRIMARY
        icon_text = "ℹ"
        
        if icon_type == "error":
            icon_color = DANGER_COLOR
            icon_text = "✕"
        elif icon_type == "warning":
            icon_color = "#FFC107"  # Amarelo
            icon_text = "⚠"
        elif icon_type == "success":
            icon_color = SUCCESS_COLOR
            icon_text = "✓"
        
        # Ícone do diálogo
        icon_label = tk.Label(
            header_frame,
            text=icon_text,
            font=("Helvetica", 24),
            fg=icon_color,
            bg=DARK_BG
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Título
        tk.Label(
            header_frame,
            text=title,
            font=FONT_SUBTITLE,
            fg=TEXT_PRIMARY,
            bg=DARK_BG,
            anchor="w"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Botão de fechar
        close_btn = tk.Label(
            header_frame,
            text="✕",
            fg=TEXT_SECONDARY,
            bg=DARK_BG,
            font=FONT_REGULAR,
            cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Button-1>", self.on_close)
        
        # Mensagem
        message_frame = tk.Frame(self.frame, bg=DARK_BG)
        message_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        message_label = tk.Label(
            message_frame,
            text=message,
            font=FONT_REGULAR,
            fg=TEXT_SECONDARY,
            bg=DARK_BG,
            justify="left",
            wraplength=400
        )
        message_label.pack(fill=tk.BOTH, expand=True)
        
        # Frame de botões
        self.button_frame = tk.Frame(self.frame, bg=DARK_BG)
        self.button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Centralizar a janela após adicionar todo o conteúdo
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Adicionar efeito de fade in
        self.dialog.attributes('-alpha', 0.0)
        self.fade_in()
        
        # Permitir fechar com Escape
        self.dialog.bind("<Escape>", self.on_close)
        
        # Adicionar efeito de arrastar
        self.dialog.bind("<ButtonPress-1>", self.start_move)
        self.dialog.bind("<ButtonRelease-1>", self.stop_move)
        self.dialog.bind("<B1-Motion>", self.do_move)
        
        self.x = 0
        self.y = 0
    
    def fade_in(self):
        """Animação de fade in"""
        alpha = self.dialog.attributes('-alpha')
        if alpha < 1.0:
            alpha += 0.1
            self.dialog.attributes('-alpha', alpha)
            self.dialog.after(20, self.fade_in)
    
    def fade_out(self, callback=None):
        """Animação de fade out"""
        alpha = self.dialog.attributes('-alpha')
        if alpha > 0:
            alpha -= 0.1
            self.dialog.attributes('-alpha', alpha)
            self.dialog.after(20, lambda: self.fade_out(callback))
        else:
            if callback:
                callback()
    
    def start_move(self, event):
        """Inicia o movimento da janela"""
        self.x = event.x
        self.y = event.y
    
    def stop_move(self, event):
        """Para o movimento da janela"""
        self.x = None
        self.y = None
    
    def do_move(self, event):
        """Realiza o movimento da janela"""
        if self.y is not None:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.dialog.winfo_x() + deltax
            y = self.dialog.winfo_y() + deltay
            self.dialog.geometry(f"+{x}+{y}")
    
    def on_close(self, event=None):
        """Fecha o diálogo"""
        self.fade_out(self.dialog.destroy)
    
    def add_button(self, text, command, is_primary=False):
        """Adiciona um botão ao diálogo"""
        if is_primary:
            button = tk.Button(
                self.button_frame, 
                text=text,
                command=command,
                bg=BLUE_PRIMARY,
                fg=TEXT_PRIMARY,
                activebackground=BLUE_SECONDARY,
                activeforeground=TEXT_PRIMARY,
                relief="flat",
                bd=0,
                cursor="hand2",
                font=FONT_REGULAR,
                padx=15,
                pady=8
            )
        else:
            button = tk.Button(
                self.button_frame, 
                text=text,
                command=command,
                bg=DARK_BG,
                fg=TEXT_PRIMARY,
                activebackground=DARKER_BG,
                activeforeground=TEXT_PRIMARY,
                relief="flat",
                bd=1,
                highlightbackground=TEXT_SECONDARY,
                highlightthickness=1,
                cursor="hand2",
                font=FONT_REGULAR,
                padx=15,
                pady=8
            )
        
        return button

class MessageDialog(CustomDialog):
    """Diálogo de mensagem"""
    def __init__(self, parent, title, message, icon_type=None):
        super().__init__(parent, title, message, icon_type)
        
        # Adicionar botão de OK
        ok_btn = self.add_button("OK", self.on_ok, True)
        ok_btn.pack(side=tk.RIGHT)
        
        # Focar no botão OK
        ok_btn.focus_set()
    
    def on_ok(self):
        self.result = True
        self.fade_out(self.dialog.destroy)

class ConfirmDialog(CustomDialog):
    """Diálogo de confirmação com botões Sim/Não"""
    def __init__(self, parent, title, message, icon_type="warning"):
        super().__init__(parent, title, message, icon_type)
        
        # Adicionar botões
        cancel_btn = self.add_button("Não", self.on_cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        ok_btn = self.add_button("Sim", self.on_ok, True)
        ok_btn.pack(side=tk.RIGHT)
        
        # Focar no botão OK
        ok_btn.focus_set()
    
    def on_ok(self):
        self.result = True
        self.fade_out(self.dialog.destroy)
    
    def on_cancel(self):
        self.result = False
        self.fade_out(self.dialog.destroy)

class InputDialog(CustomDialog):
    """Diálogo com campo de entrada"""
    def __init__(self, parent, title, message, default="", show=None, icon_type=None):
        super().__init__(parent, title, message, icon_type)
        
        # Campo de entrada
        entry_frame = tk.Frame(self.frame, bg=DARK_BG)
        entry_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.entry = tk.Entry(
            entry_frame,
            font=FONT_REGULAR,
            bg=DARKER_BG,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=TEXT_SECONDARY,
            highlightcolor=BLUE_PRIMARY,
            width=40
        )
        if show:
            self.entry.configure(show=show)
        self.entry.pack(fill=tk.X, ipady=8)
        self.entry.insert(0, default)
        self.entry.select_range(0, tk.END)
        self.entry.focus_set()
        
        # Adicionar botões
        cancel_btn = self.add_button("Cancelar", self.on_cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        ok_btn = self.add_button("OK", self.on_ok, True)
        ok_btn.pack(side=tk.RIGHT)
        
        # Vincular a tecla Enter
        self.entry.bind("<Return>", lambda event: self.on_ok())
    
    def on_ok(self):
        self.result = self.entry.get()
        self.fade_out(self.dialog.destroy)
    
    def on_cancel(self):
        self.result = None
        self.fade_out(self.dialog.destroy)

# Funções utilitárias para substituir messagebox padrão
def show_info(parent, title, message):
    """Mostra um diálogo de informação"""
    dialog = MessageDialog(parent, title, message, "info")
    parent.wait_window(dialog.dialog)
    return dialog.result

def show_error(parent, title, message):
    """Mostra um diálogo de erro"""
    dialog = MessageDialog(parent, title, message, "error")
    parent.wait_window(dialog.dialog)
    return dialog.result

def show_warning(parent, title, message):
    """Mostra um diálogo de alerta"""
    dialog = MessageDialog(parent, title, message, "warning")
    parent.wait_window(dialog.dialog)
    return dialog.result

def show_success(parent, title, message):
    """Mostra um diálogo de sucesso"""
    dialog = MessageDialog(parent, title, message, "success")
    parent.wait_window(dialog.dialog)
    return dialog.result

def ask_yes_no(parent, title, message):
    """Mostra um diálogo de confirmação Sim/Não"""
    dialog = ConfirmDialog(parent, title, message)
    parent.wait_window(dialog.dialog)
    return dialog.result

def ask_input(parent, title, message, default="", show=None):
    """Mostra um diálogo de entrada de texto"""
    dialog = InputDialog(parent, title, message, default, show)
    parent.wait_window(dialog.dialog)
    return dialog.result 