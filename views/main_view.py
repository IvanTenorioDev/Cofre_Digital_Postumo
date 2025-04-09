import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import datetime
import threading
import time
import os

from views.styles import *
from views.login_view import LoginView
from views.setup_view import SetupView
from views.dashboard_view import DashboardView
from views.recovery_view import RecoveryView
from views.compartment_view import CompartmentView

class CofreDigitalView:
    """View principal para a aplicação Cofre Digital Póstumo."""
    
    def __init__(self, master, controller):
        """Inicializa a view principal."""
        self.master = master
        self.controller = controller
        
        # Configuração da janela principal
        self.master.title("Cofre Digital Póstumo")
        self.master.geometry("900x700")
        self.master.minsize(900, 700)
        self.master.configure(bg=BG_COLOR)
        
        # Telas
        self.current_frame = None
        self.login_view = None
        self.setup_view = None
        self.dashboard_view = None
        self.recovery_view = None
        self.compartment_view = None
        
        # Estado
        self.modo_heranca = False
        
        # Vincular evento de fechamento
        self.master.protocol("WM_DELETE_WINDOW", self.confirmar_saida)
    
    def mostrar_frame(self, frame):
        """Mostra um frame e esconde o atual."""
        if self.current_frame:
            self.current_frame.pack_forget()
        
        frame.pack(fill=tk.BOTH, expand=True)
        self.current_frame = frame
        
        # Forçar atualização da interface
        self.master.update_idletasks()
    
    def mostrar_tela_login(self, modo_heranca=False):
        """Mostra a tela de login."""
        self.modo_heranca = modo_heranca
        
        # Criar tela de login se não existir
        if not self.login_view:
            self.login_view = LoginView(self.master, self.controller)
        
        # Atualizar status de herança
        self.login_view.atualizar_modo_heranca(modo_heranca)
        
        # Mostrar tela
        self.mostrar_frame(self.login_view)
    
    def mostrar_tela_configuracao_inicial(self):
        """Mostra a tela de configuração inicial do usuário."""
        # Criar tela de configuração se não existir
        if not self.setup_view:
            self.setup_view = SetupView(self.master, self.controller)
        
        # Mostrar tela
        self.mostrar_frame(self.setup_view)
    
    def mostrar_dashboard(self, modo_heranca=False):
        """Mostra o dashboard principal."""
        self.modo_heranca = modo_heranca
        
        # Criar tela de dashboard se não existir
        if not self.dashboard_view:
            self.dashboard_view = DashboardView(self.master, self.controller)
        
        # Atualizar dados do dashboard
        self.dashboard_view.atualizar_interface(modo_heranca)
        
        # Mostrar tela
        self.mostrar_frame(self.dashboard_view)
    
    def mostrar_frase_recuperacao(self, frase):
        """Mostra a frase de recuperação após configuração inicial."""
        if not self.recovery_view:
            self.recovery_view = RecoveryView(self.master, self.controller)
        
        # Atualizar frase
        self.recovery_view.mostrar_frase(frase)
        
        # Mostrar tela
        self.mostrar_frame(self.recovery_view)
    
    def mostrar_tela_compartimento(self, compartimento_id, modo_heranca=False):
        """Mostra a tela de um compartimento específico."""
        # Criar tela de compartimento se não existir
        if not self.compartment_view:
            self.compartment_view = CompartmentView(self.master, self.controller)
        
        # Atualizar dados do compartimento
        self.compartment_view.carregar_compartimento(compartimento_id, modo_heranca)
        
        # Mostrar tela
        self.mostrar_frame(self.compartment_view)
    
    def mostrar_frase_compartimento(self, nome, frase):
        """Mostra a frase de recuperação de um compartimento."""
        # Criar diálogo para mostrar a frase
        dialog = tk.Toplevel(self.master)
        dialog.title(f"Frase de Recuperação - {nome}")
        dialog.geometry("600x400")
        dialog.transient(self.master)
        dialog.grab_set()
        dialog.configure(bg=BG_COLOR)
        
        # Frame principal
        frame = tk.Frame(dialog, **FRAME_STYLE)
        frame.pack(fill=tk.BOTH, expand=True, padx=PADDING_LARGE, pady=PADDING_LARGE)
        
        # Título
        tk.Label(
            frame,
            text="IMPORTANTE: GUARDE ESTA FRASE DE RECUPERAÇÃO",
            font=FONT_TITLE,
            **LABEL_STYLE
        ).pack(pady=PADDING_MEDIUM)
        
        # Descrição
        tk.Label(
            frame,
            text=f"Esta é a frase de recuperação para o compartimento '{nome}'.\n"
                 "Guarde-a em um local seguro. Ela permitirá recuperar o acesso ao compartimento.",
            font=FONT_NORMAL,
            justify=tk.CENTER,
            wraplength=550,
            **LABEL_STYLE
        ).pack(pady=PADDING_MEDIUM)
        
        # Frame para a frase
        frase_frame = tk.Frame(frame, bg=FRAME_COLOR, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        frase_frame.pack(fill=tk.X, pady=PADDING_MEDIUM)
        
        # Mostrar a frase
        frase_text = tk.Text(
            frase_frame,
            height=4,
            width=50,
            font=FONT_BOLD,
            bg="white",
            wrap=tk.WORD
        )
        frase_text.insert(tk.END, frase)
        frase_text.configure(state="disabled")
        frase_text.pack(padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Botão para copiar
        def copiar_frase():
            self.master.clipboard_clear()
            self.master.clipboard_append(frase)
            messagebox.showinfo("Copiado", "Frase copiada para a área de transferência.")
        
        tk.Button(
            frame,
            text="Copiar Frase",
            command=copiar_frase,
            **BUTTON_PRIMARY_STYLE
        ).pack(pady=PADDING_MEDIUM)
        
        # Aviso
        tk.Label(
            frame,
            text="ATENÇÃO: Esta frase não será mostrada novamente.",
            font=FONT_BOLD,
            fg=ERROR_COLOR,
            bg=BG_COLOR
        ).pack(pady=PADDING_MEDIUM)
        
        # Botão para concluir
        tk.Button(
            frame,
            text="Entendi e Guardei a Frase",
            command=dialog.destroy,
            **BUTTON_STYLE
        ).pack(pady=PADDING_MEDIUM)
    
    def atualizar_status_heranca(self, modo_heranca, mensagem=None):
        """Atualiza o status de herança em todas as telas."""
        self.modo_heranca = modo_heranca
        
        # Atualizar em cada tela, se existir
        if self.dashboard_view:
            self.dashboard_view.atualizar_interface(modo_heranca)
        
        if self.login_view:
            self.login_view.atualizar_modo_heranca(modo_heranca)
        
        # Mostrar mensagem, se fornecida
        if mensagem:
            messagebox.showinfo("Status de Herança", mensagem)
    
    def notificar_periodo(self, dias_restantes):
        """Notifica o usuário sobre o período de renovação."""
        if dias_restantes <= 3:
            messagebox.showwarning(
                "Período Próximo do Fim",
                f"ATENÇÃO: Restam apenas {dias_restantes} dias para renovar o período.\n"
                "Após esse prazo, o modo de herança será ativado."
            )
        else:
            messagebox.showinfo(
                "Renovação Recomendada",
                f"Restam {dias_restantes} dias para renovar o período.\n"
                "Recomendamos renovar em breve para evitar a ativação do modo de herança."
            )
    
    def confirmar_saida(self):
        """Confirma se o usuário deseja sair da aplicação."""
        resposta = messagebox.askyesno("Sair", "Tem certeza que deseja sair?")
        if resposta:
            self.master.destroy()
    
    def mostrar_erro(self, titulo, mensagem):
        """Mostra uma mensagem de erro."""
        messagebox.showerror(titulo, mensagem)
    
    def mostrar_sucesso(self, titulo, mensagem):
        """Mostra uma mensagem de sucesso."""
        messagebox.showinfo(titulo, mensagem)
    
    def mostrar_aviso(self, titulo, mensagem):
        """Mostra uma mensagem de aviso."""
        messagebox.showwarning(titulo, mensagem)
    
    def confirmar(self, titulo, mensagem):
        """Solicita confirmação do usuário."""
        return messagebox.askyesno(titulo, mensagem)
    
    def pedir_entrada(self, titulo, mensagem):
        """Solicita entrada de texto do usuário."""
        return simpledialog.askstring(titulo, mensagem)
    
    def atualizar_compartimento_ativo(self, compartimento_id):
        """Atualiza o compartimento ativo em todas as telas."""
        # Atualizar dashboard, se existir
        if self.dashboard_view:
            self.dashboard_view.atualizar_compartimento(compartimento_id) 