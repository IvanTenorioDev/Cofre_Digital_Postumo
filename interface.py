import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
import threading
import time
import json
import os
import datetime
import sqlite3
import traceback
from styles import *
from custom_dialogs import show_info, show_error, show_warning, show_success, ask_yes_no, ask_input

def aplicar_estilo_padrao(func):
    """Decorador para aplicar estilo padrão em janelas"""
    def wrapper(self, *args, **kwargs):
        janela = func(self, *args, **kwargs)
        if isinstance(janela, tk.Toplevel):
            janela.configure(bg=DARK_BG)
            # Configurar estilos modernos
            janela.option_add("*TButton*Background", BLUE_PRIMARY)
            janela.option_add("*TButton*Foreground", TEXT_PRIMARY)
            
            # Adicionar sombra com frame externo
            for widget in janela.winfo_children()[:]:
                if isinstance(widget, tk.Frame):
                    widget.configure(bg=DARK_BG)
                    
                    # Aplicar estilo a todos os botões no frame
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Button):
                            child.configure(
                                bg=BLUE_PRIMARY,
                                fg=TEXT_PRIMARY,
                                activebackground=BLUE_SECONDARY,
                                activeforeground=TEXT_PRIMARY,
                                **BTN_STYLE
                            )
                            
                            # Adicionar efeitos hover
                            def on_enter(e, button=child):
                                button['background'] = BLUE_SECONDARY
                            
                            def on_leave(e, button=child):
                                button['background'] = BLUE_PRIMARY
                            
                            child.bind("<Enter>", on_enter)
                            child.bind("<Leave>", on_leave)
                            
                        elif isinstance(child, tk.Entry):
                            child.configure(**ENTRY_STYLE)
                        
                        elif isinstance(child, tk.Label):
                            child.configure(bg=DARK_BG, fg=TEXT_PRIMARY, font=FONT_REGULAR)
                        
                        elif isinstance(child, tk.Text):
                            child.configure(
                                bg=SURFACE_1,
                                fg=TEXT_PRIMARY,
                                insertbackground=TEXT_PRIMARY,
                                relief="flat",
                                bd=0,
                                highlightthickness=1,
                                highlightbackground=BORDER_COLOR,
                                highlightcolor=BLUE_PRIMARY,
                                font=FONT_REGULAR
                            )
            
            # Centralizar a janela
            janela.update_idletasks()
            width = janela.winfo_width()
            height = janela.winfo_height()
            x = (janela.winfo_screenwidth() // 2) - (width // 2)
            y = (janela.winfo_screenheight() // 2) - (height // 2)
            janela.geometry(f'+{x}+{y}')
            
            # Adicionar borda arredondada (simulada)
            janela.configure(highlightbackground=BORDER_COLOR, highlightthickness=1)
        
        return janela
    return wrapper

class InterfaceGrafica:
    def __init__(self, cofre):
        self.cofre = cofre
        self.janela = None
        self.frame_login = None
        self.frame_principal = None
        self.usuario_configurado = False
        self.tentativas = 0
    
    def iniciar(self):
        """Inicia a interface gráfica"""
        self.janela = tk.Tk()
        self.janela.title("Bloco de Notas Portátil")
        self.janela.geometry("800x600")
        
        # Verificar se o usuário já está configurado
        self.verificar_usuario_configurado()
        
        if self.usuario_configurado:
            self.mostrar_tela_login()
        else:
            self.mostrar_tela_configuracao()
        
        self.janela.mainloop()
    
    def verificar_usuario_configurado(self):
        """Verifica se já existe um usuário configurado"""
        try:
            self.usuario_configurado = self.cofre.banco_dados.verificar_usuario_existente()
        except Exception:
            self.usuario_configurado = False
    
    def mostrar_tela_configuracao(self):
        """Mostra a tela de configuração inicial"""
        if self.frame_login:
            self.frame_login.destroy()
        
        if self.frame_principal:
            self.frame_principal.destroy()
        
        frame = tk.Frame(self.janela)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="Configuração Inicial", font=("Arial", 16)).pack(pady=10)
        
        tk.Label(frame, text="Nome:").pack(anchor=tk.W, pady=(10, 0))
        entrada_nome = tk.Entry(frame, width=40)
        entrada_nome.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame, text="Senha Principal:").pack(anchor=tk.W, pady=(10, 0))
        entrada_senha = tk.Entry(frame, width=40, show="*")
        entrada_senha.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame, text="Confirmar Senha Principal:").pack(anchor=tk.W, pady=(10, 0))
        entrada_confirmar_senha = tk.Entry(frame, width=40, show="*")
        entrada_confirmar_senha.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame, text="Senha de Recuperação:").pack(anchor=tk.W, pady=(10, 0))
        entrada_senha_heranca = tk.Entry(frame, width=40, show="*")
        entrada_senha_heranca.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame, text="Confirmar Senha de Recuperação:").pack(anchor=tk.W, pady=(10, 0))
        entrada_confirmar_senha_heranca = tk.Entry(frame, width=40, show="*")
        entrada_confirmar_senha_heranca.pack(fill=tk.X, pady=(0, 10))
        
        def configurar():
            """Configura o usuário inicial"""
            nome = self.entrada_nome.get()
            senha = self.entrada_senha.get()
            confirmar_senha = self.entrada_confirmar_senha.get()
            senha_heranca = self.entrada_senha_heranca.get()
            confirmar_senha_heranca = self.entrada_confirmar_senha_heranca.get()
            
            # Validar campos
            if not nome or not senha or not confirmar_senha or not senha_heranca or not confirmar_senha_heranca:
                messagebox.showerror("Erro", "Todos os campos são obrigatórios")
                return
            
            if senha != confirmar_senha:
                messagebox.showerror("Erro", "As senhas principais não coincidem")
                return
            
            if senha_heranca != confirmar_senha_heranca:
                messagebox.showerror("Erro", "As senhas de recuperação não coincidem")
                return
            
            # Configurar usuário
            sucesso, mensagem = self.cofre.configurar_usuario(nome, senha, senha_heranca)
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                # Limpar o frame de configuração
                self.frame_configuracao.destroy()
                # Mostrar a tela de login
                self.mostrar_tela_login()
            else:
                messagebox.showerror("Erro", mensagem)
        
        tk.Button(frame, text="Configurar", command=configurar).pack(pady=20)
    
    def mostrar_tela_login(self):
        """Mostra a tela de login modernizada"""
        # Limpar TODA a janela primeiro
        for widget in self.janela.winfo_children():
            widget.destroy()
        
        # Configurar janela principal
        self.janela.configure(bg=DARK_BG)
        self.janela.geometry("450x580")
        self.janela.resizable(False, False)
        
        # Centralizar a janela
        self.janela.update_idletasks()
        width = self.janela.winfo_width()
        height = self.janela.winfo_height()
        x = (self.janela.winfo_screenwidth() // 2) - (width // 2)
        y = (self.janela.winfo_screenheight() // 2) - (height // 2)
        self.janela.geometry(f'+{x}+{y}')
        
        # Container principal com padding
        container = tk.Frame(self.janela, bg=DARK_BG, padx=40, pady=40)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Ícone ou logo (simula um ícone de cadeado)
        logo_frame = tk.Frame(container, bg=DARK_BG, width=80, height=80)
        logo_frame.pack(pady=(30, 20))
        logo_frame.pack_propagate(False)
        
        # Usar um label como logotipo
        logo = tk.Label(
            logo_frame, 
            text="🔒", 
            font=("Arial", 48), 
            fg=BLUE_PRIMARY,
            bg=DARK_BG
        )
        logo.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título da aplicação com um subtítulo
        tk.Label(
            container,
            text="Bloco de Notas Portátil",
            font=FONT_TITLE,
            bg=DARK_BG,
            fg=TEXT_PRIMARY
        ).pack(pady=(0, 5))
        
        tk.Label(
            container,
            text="Entre para acessar suas anotações",
            font=FONT_SMALL,
            bg=DARK_BG,
            fg=TEXT_SECONDARY
        ).pack(pady=(0, 40))
        
        # Frame do formulário com efeito de card
        frame_form = tk.Frame(
            container,
            bg=CARD_BG,
            padx=30,
            pady=30,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        frame_form.pack(fill=tk.X)
        
        # Label para a senha
        tk.Label(
            frame_form,
            text="Senha",
            font=FONT_REGULAR,
            bg=CARD_BG,
            fg=TEXT_SECONDARY,
            anchor="w"
        ).pack(fill=tk.X)
        
        # Frame para o campo de senha com ícone
        senha_frame = tk.Frame(frame_form, bg=CARD_BG)
        senha_frame.pack(fill=tk.X, pady=(8, 25))
        
        # Ícone de cadeado
        tk.Label(
            senha_frame,
            text="🔑",
            font=FONT_REGULAR,
            bg=SURFACE_1,
            fg=TEXT_SECONDARY,
            padx=10
        ).pack(side=tk.LEFT)
        
        # Campo de senha com estilo moderno
        entrada_senha = tk.Entry(
            senha_frame,
            show="•",
            **ENTRY_STYLE,
            width=25
        )
        entrada_senha.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=8)
        entrada_senha.focus_set()
        
        # Botão de mostrar/ocultar senha
        self.mostrar_senha_var = tk.BooleanVar(value=False)
        
        def toggle_mostrar_senha():
            if self.mostrar_senha_var.get():
                entrada_senha.config(show="")
            else:
                entrada_senha.config(show="•")
        
        mostrar_senha_check = tk.Checkbutton(
            frame_form,
            text="Mostrar senha",
            variable=self.mostrar_senha_var,
            command=toggle_mostrar_senha,
            bg=CARD_BG,
            fg=TEXT_SECONDARY,
            selectcolor=DARK_BG,
            activebackground=CARD_BG,
            activeforeground=TEXT_PRIMARY
        )
        mostrar_senha_check.pack(anchor="w", pady=(0, 15))
        
        # Botão de login com efeito de elevação
        btn_frame = tk.Frame(frame_form, bg=CARD_BG)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Criar uma cópia do estilo para modificar a fonte
        login_btn_style = dict(BTN_PRIMARY_STYLE)
        login_btn_style["font"] = ("Inter", 14)
        
        login_btn = tk.Button(
            btn_frame,
            text="Entrar",
            command=lambda: self.verificar_senha(entrada_senha.get()),
            **login_btn_style,
            width=20,
            height=2
        )
        login_btn.pack(pady=(0, 5))
        
        # Adicionar efeitos de hover e click
        def on_enter(e):
            login_btn['background'] = BLUE_SECONDARY
        
        def on_leave(e):
            login_btn['background'] = BLUE_PRIMARY
        
        def on_click(e):
            login_btn.configure(relief="sunken")
        
        def on_release(e):
            login_btn.configure(relief="flat")
            self.verificar_senha(entrada_senha.get())
        
        login_btn.bind("<Enter>", on_enter)
        login_btn.bind("<Leave>", on_leave)
        login_btn.bind("<ButtonPress-1>", on_click)
        login_btn.bind("<ButtonRelease-1>", on_release)
        
        # Separador
        separator_frame = tk.Frame(frame_form, bg=CARD_BG, height=40)
        separator_frame.pack(fill=tk.X, pady=15)
        
        separator_line1 = tk.Frame(separator_frame, bg=BORDER_COLOR, height=1)
        separator_line1.place(relx=0, rely=0.5, relwidth=0.42, anchor="w")
        
        tk.Label(
            separator_frame,
            text="ou",
            bg=CARD_BG,
            fg=TEXT_SECONDARY,
            font=FONT_SMALL
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        separator_line2 = tk.Frame(separator_frame, bg=BORDER_COLOR, height=1)
        separator_line2.place(relx=1, rely=0.5, relwidth=0.42, anchor="e")
        
        # Botão de frase mnemônica
        btn_frase = tk.Button(
            frame_form,
            text="Acessar com Frase Mnemônica",
            command=self.mostrar_login_frase,
            **BTN_SECONDARY_STYLE,
            width=25
        )
        btn_frase.pack(pady=5)
        
        # Vincular tecla Enter
        entrada_senha.bind("<Return>", lambda event: self.verificar_senha(entrada_senha.get()))
        
        # Versão ou informação adicional
        tk.Label(
            container,
            text="Cofre Digital Póstumo v1.0",
            font=("Inter", 10),
            bg=DARK_BG,
            fg=TEXT_SECONDARY
        ).pack(side=tk.BOTTOM, pady=10)
    
    def verificar_senha(self, senha):
        """Verifica a senha do usuário"""
        if not senha:
            show_error(self.janela, "Erro", "Digite sua senha")
            return
        
        sucesso, mensagem, modo_heranca = self.cofre.autenticar(senha)
        
        if sucesso:
            # Não atualizar a data da última confirmação automaticamente
            # Isso será feito apenas quando o usuário solicitar explicitamente
            self.mostrar_tela_principal(modo_restrito=False)
        else:
            show_error(self.janela, "Erro", mensagem)
            
            # Incrementar contador de tentativas
            self.tentativas += 1
            
            # Verificar se atingiu o limite de tentativas
            if self.tentativas >= self.cofre.max_tentativas:
                show_error(self.janela, "Acesso Bloqueado", "Número máximo de tentativas atingido. O aplicativo será fechado.")
                self.janela.quit()
    
    def mostrar_tela_principal(self, modo_restrito=False):
        """Mostra a tela principal modernizada"""
        # Limpar janela
        for widget in self.janela.winfo_children():
            widget.destroy()
        
        # Configurar janela principal
        self.janela.configure(bg=DARK_BG)
        self.janela.geometry("1024x768")
        self.janela.minsize(1024, 768)
        
        # Criar menu
        self._criar_menu()
        
        # Frame principal que contém todo o conteúdo
        self.frame_principal = tk.Frame(self.janela, bg=DARK_BG)
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Header com título e subtítulo
        header_frame = tk.Frame(self.frame_principal, bg=DARK_BG)
        header_frame.pack(fill=tk.X, pady=(40, 30))
        
        # Título principal
        tk.Label(
            header_frame,
            text="Bloco de Notas Portátil",
            font=FONT_TITLE,
            bg=DARK_BG,
            fg=TEXT_PRIMARY
        ).pack(anchor="w")
        
        # Subtítulo ou descrição
        tk.Label(
            header_frame,
            text="Gerenciador de dados seguros",
            font=FONT_REGULAR,
            bg=DARK_BG,
            fg=TEXT_SECONDARY
        ).pack(anchor="w", pady=(5, 0))
        
        # Indicador de modo restrito
        if modo_restrito:
            modo_frame = tk.Frame(self.frame_principal, bg=DANGER_COLOR, padx=20, pady=15)
            modo_frame.pack(fill=tk.X, pady=(0, 30))
            
            tk.Label(
                modo_frame,
                text="MODO DE ACESSO RESTRITO",
                font=("Inter", 12, "bold"),
                bg=DANGER_COLOR,
                fg=TEXT_PRIMARY
            ).pack()
            
            tk.Label(
                modo_frame,
                text="Você tem acesso somente para leitura neste compartimento",
                font=FONT_SMALL,
                bg=DANGER_COLOR,
                fg=TEXT_PRIMARY
            ).pack()
        
        # Frame para os cards de estatísticas
        stats_section = tk.Frame(self.frame_principal, bg=DARK_BG)
        stats_section.pack(fill=tk.X, pady=(0, 50))
        
        # Título da seção de estatísticas
        tk.Label(
            stats_section,
            text="Resumo",
            font=FONT_SUBTITLE,
            bg=DARK_BG,
            fg=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 20))
        
        # Frame para os cards
        stats_frame = tk.Frame(stats_section, bg=DARK_BG)
        stats_frame.pack(fill=tk.X)
        
        # Configurar grid para centralizar os cards
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(4, weight=1)
        
        # Cards de estatísticas centralizados
        self._criar_card_estatistica(stats_frame, "Senhas", "1", 1)
        self._criar_card_estatistica(stats_frame, "Notas", "1", 2)
        self._criar_card_estatistica(stats_frame, "Arquivos", "0", 3)
        
        # Seção de ações
        actions_section = tk.Frame(self.frame_principal, bg=DARK_BG)
        actions_section.pack(fill=tk.X, pady=(0, 40))
        
        # Título da seção de ações
        tk.Label(
            actions_section,
            text="Ações",
            font=FONT_SUBTITLE,
            bg=DARK_BG,
            fg=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 20))
        
        # Frame para os botões principais
        frame_botoes = tk.Frame(actions_section, bg=DARK_BG)
        frame_botoes.pack(fill=tk.X)
        
        # Botões principais
        self._criar_botao_principal(frame_botoes, "Senhas", self.gerenciar_senhas)
        self._criar_botao_principal(frame_botoes, "Notas", self.gerenciar_notas)
        self._criar_botao_principal(frame_botoes, "Arquivos", self.gerenciar_arquivos)
        self._criar_botao_principal(frame_botoes, "Categorias", self.gerenciar_categorias)
        
        # Seção de compartimentos
        compartment_section = tk.Frame(self.frame_principal, bg=DARK_BG)
        compartment_section.pack(fill=tk.X, pady=(0, 40))
        
        # Título da seção de compartimentos
        tk.Label(
            compartment_section,
            text="Compartimentos",
            font=FONT_SUBTITLE,
            bg=DARK_BG,
            fg=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 15))
        
        # Frame do compartimento
        frame_compartimento = tk.Frame(
            compartment_section,
            bg=CARD_BG,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            bd=0,
            padx=25,
            pady=20
        )
        frame_compartimento.pack(fill=tk.X)
        
        # Ícone e nome do compartimento ativo
        comp_header = tk.Frame(frame_compartimento, bg=CARD_BG)
        comp_header.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            comp_header,
            text="📁",
            font=("Arial", 18),
            bg=CARD_BG,
            fg=BLUE_PRIMARY
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            comp_header,
            text=f"Compartimento ativo: {self.cofre.compartimento_ativo}",
            bg=CARD_BG,
            fg=TEXT_PRIMARY,
            font=("Inter", 14, "bold")
        ).pack(side=tk.LEFT)
        
        # Botões do compartimento apenas se não estiver em modo restrito
        if not modo_restrito:
            frame_botoes = tk.Frame(frame_compartimento, bg=CARD_BG)
            frame_botoes.pack(fill=tk.X)
            
            # Botões com tamanho fixo
            botoes = [
                ("Criar Compartimento", "➕", self.criar_compartimento),
                ("Alternar Compartimento", "🔄", self.alternar_compartimento),
                ("Acessar por Frase", "🔑", self.acessar_por_frase)
            ]
            
            for texto, icone, comando in botoes:
                btn_frame = tk.Frame(frame_botoes, bg=CARD_BG)
                btn_frame.pack(side=tk.LEFT, padx=(0, 15))
                
                btn = tk.Button(
                    btn_frame,
                    text=f"{icone} {texto}",
                    command=comando,
                    bg=SURFACE_1,
                    fg=TEXT_PRIMARY,
                    activebackground=SURFACE_2,
                    activeforeground=TEXT_PRIMARY,
                    font=FONT_REGULAR,
                    relief="flat",
                    bd=0,
                    padx=15,
                    pady=10,
                    cursor="hand2"
                )
                btn.pack()
                
                # Efeitos hover
                def on_enter(e, button=btn):
                    button['background'] = SURFACE_2
                
                def on_leave(e, button=btn):
                    button['background'] = SURFACE_1
                
                btn.bind("<Enter>", on_enter)
                btn.bind("<Leave>", on_leave)
        
        # Seção do timer
        timer_section = tk.Frame(self.frame_principal, bg=DARK_BG)
        timer_section.pack(fill=tk.X, pady=(0, 20))
        
        # Frame do timer com card moderno
        frame_timer = tk.Frame(
            timer_section,
            bg=DARK_BG,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1 if not modo_restrito else 0,
            bd=0
        )
        frame_timer.pack(fill=tk.X, pady=(0, 20))
        
        # Frame para o conteúdo do timer
        timer_content = tk.Frame(frame_timer, bg=DARK_BG, padx=30, pady=20)
        timer_content.pack(fill=tk.X)
        
        if modo_restrito:
            texto_timer = "Acesso restrito ao compartimento atual"
        else:
            texto_timer = "Tempo restante até ativação do modo de recuperação:"
        
        # Ícone do timer
        tk.Label(
            timer_content,
            text="⏱️",
            font=("Arial", 24),
            bg=DARK_BG,
            fg=BLUE_PRIMARY
        ).pack(pady=(0, 10))
        
        # Texto explicativo
        tk.Label(
            timer_content,
            text=texto_timer,
            bg=DARK_BG,
            fg=TEXT_SECONDARY,
            font=FONT_REGULAR
        ).pack()
        
        # Label do timer com tamanho fixo
        timer_frame = tk.Frame(timer_content, bg=DARK_BG, height=80)
        timer_frame.pack(fill=tk.X, pady=(10, 20))
        timer_frame.pack_propagate(False)
        
        # Label do timer
        self.label_timer = tk.Label(
            timer_frame,
            text="Carregando...",
            bg=DARK_BG,
            fg=BLUE_PRIMARY,
            font=("Inter", 36, "bold")
        )
        self.label_timer.place(relx=0.5, rely=0.5, anchor="center")
        
        # Botão de renovar período apenas se não estiver em modo restrito
        if not modo_restrito:
            btn_frame = tk.Frame(timer_content, bg=DARK_BG)
            btn_frame.pack()
            
            btn_renovar = tk.Button(
                btn_frame,
                text="Renovar Período",
                command=self.renovar_periodo,
                **BTN_PRIMARY_STYLE,
                padx=20,
                pady=10
            )
            btn_renovar.pack()
            
            # Efeitos hover
            def on_enter(e):
                btn_renovar['background'] = BLUE_SECONDARY
            
            def on_leave(e):
                btn_renovar['background'] = BLUE_PRIMARY
            
            btn_renovar.bind("<Enter>", on_enter)
            btn_renovar.bind("<Leave>", on_leave)
        
        # Armazenar o modo de acesso restrito como atributo da classe
        self.modo_acesso_restrito = modo_restrito
        
        # Iniciar atualização do timer imediatamente
        self.atualizar_timer()
    
    def _criar_card_estatistica(self, parent, titulo, valor, coluna):
        """Cria um card de estatística com visual moderno e 3D"""
        # Frame externo para sombra
        frame_externo = tk.Frame(parent, bg=DARK_BG, padx=3, pady=3)
        frame_externo.grid(row=0, column=coluna, padx=20)
        
        # Frame do card com efeito de elevação e borda
        card = tk.Frame(
            frame_externo,
            bg=CARD_BG,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            bd=0,
            padx=25,
            pady=20
        )
        card.pack()
        
        # Ícones baseados no tipo
        icones = {
            "Senhas": "🔑",
            "Notas": "📝",
            "Arquivos": "📁"
        }
        
        icone = icones.get(titulo, "📊")
        
        # Ícone superior
        tk.Label(
            card,
            text=icone,
            font=("Arial", 20),
            bg=CARD_BG,
            fg=BLUE_PRIMARY
        ).pack(pady=(0, 5))
        
        # Container para o valor com gradiente simulado
        valor_frame = tk.Frame(card, bg=CARD_BG, width=100, height=70)
        valor_frame.pack(pady=5)
        valor_frame.pack_propagate(False)
        
        # Valor em destaque
        tk.Label(
            valor_frame,
            text=valor,
            font=("Inter", 32, "bold"),
            bg=CARD_BG,
            fg=BLUE_PRIMARY
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Título abaixo do valor
        tk.Label(
            card,
            text=titulo,
            font=FONT_REGULAR,
            bg=CARD_BG,
            fg=TEXT_SECONDARY
        ).pack(pady=(5, 0))
        
        # Adicionar efeito hover
        def on_enter(e):
            card.configure(bg=SURFACE_2)
            for widget in card.winfo_children():
                widget.configure(bg=SURFACE_2)
        
        def on_leave(e):
            card.configure(bg=CARD_BG)
            for widget in card.winfo_children():
                widget.configure(bg=CARD_BG)
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
    
    def _criar_botao_principal(self, parent, texto, comando):
        """Cria um botão principal com visual 3D moderno"""
        frame = tk.Frame(parent, bg=DARK_BG)
        frame.pack(side=tk.LEFT, padx=15)
        
        # Ícones para cada tipo de botão
        icones = {
            "Senhas": "🔑",
            "Notas": "📝",
            "Arquivos": "📁",
            "Categorias": "🏷️"
        }
        
        # Frame para efeito de sombra e elevação
        frame_sombra = tk.Frame(
            frame,
            bg=DARKER_BG,
            padx=2,
            pady=2,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        frame_sombra.pack()
        
        # Frame para o conteúdo do botão
        btn_content = tk.Frame(
            frame_sombra,
            bg=SURFACE_1,
            padx=20,
            pady=15
        )
        btn_content.pack()
        
        # Adicionar ícone
        tk.Label(
            btn_content,
            text=icones.get(texto, "🔘"),
            font=("Arial", 20),
            bg=SURFACE_1,
            fg=BLUE_PRIMARY
        ).pack(pady=(0, 10))
        
        # Adicionar texto
        tk.Label(
            btn_content,
            text=texto,
            font=("Inter", 14, "bold"),
            bg=SURFACE_1,
            fg=TEXT_PRIMARY
        ).pack()
        
        # Tornar o botão clicável
        for widget in (btn_content, btn_content.winfo_children()[0], btn_content.winfo_children()[1]):
            widget.bind("<Button-1>", lambda e, cmd=comando: cmd())
            widget.configure(cursor="hand2")
        
        # Efeitos hover e click
        def on_enter(e):
            frame_sombra.configure(bg=BLUE_SECONDARY)
            btn_content.configure(bg=BLUE_PRIMARY)
            for child in btn_content.winfo_children():
                child.configure(bg=BLUE_PRIMARY, fg=TEXT_PRIMARY)
        
        def on_leave(e):
            frame_sombra.configure(bg=DARKER_BG)
            btn_content.configure(bg=SURFACE_1)
            btn_content.winfo_children()[0].configure(bg=SURFACE_1, fg=BLUE_PRIMARY)  # Ícone
            btn_content.winfo_children()[1].configure(bg=SURFACE_1, fg=TEXT_PRIMARY)  # Texto
        
        def on_click(e):
            frame_sombra.configure(bg=DARKER_BG)
            btn_content.configure(bg=BLUE_SECONDARY)
            for child in btn_content.winfo_children():
                child.configure(bg=BLUE_SECONDARY)
            comando()
        
        # Vincular eventos
        for widget in (btn_content, btn_content.winfo_children()[0], btn_content.winfo_children()[1]):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)
    
    def _criar_frame_compartimento(self):
        """Cria o frame do compartimento com visual moderno"""
        frame = tk.Frame(
            self.frame_principal,
            bg=CARD_BG,
            highlightbackground=BLUE_PRIMARY,
            highlightthickness=1,
            bd=0
        )
        frame.pack(fill=tk.X, pady=20, padx=20)
        
        # Label do compartimento ativo
        self.label_compartimento_ativo = tk.Label(
            frame,
            text=f"Compartimento ativo: {self.cofre.compartimento_ativo}",
            bg=CARD_BG,
            fg=TEXT_PRIMARY,
            font=FONT_REGULAR
        )
        self.label_compartimento_ativo.pack(pady=15)
        
        # Frame para os botões
        frame_botoes = tk.Frame(frame, bg=CARD_BG)
        frame_botoes.pack(pady=(0, 15))
        
        # Botões com tamanho fixo
        botoes = [
            ("Criar Compartimento", self.criar_compartimento),
            ("Alternar Compartimento", self.alternar_compartimento),
            ("Acessar por Frase", self.acessar_por_frase)
        ]
        
        for texto, comando in botoes:
            btn = tk.Button(
                frame_botoes,
                text=texto,
                command=comando,
                bg=BLUE_PRIMARY,
                fg=TEXT_PRIMARY,
                activebackground=BLUE_SECONDARY,
                activeforeground=TEXT_PRIMARY,
                font=("Helvetica", 12),
                width=20,  # Largura fixa para todos os botões
                relief="flat",
                bd=0,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=10)
            
            # Efeitos hover
            def on_enter(e, button=btn):
                button['background'] = BLUE_SECONDARY
            
            def on_leave(e, button=btn):
                button['background'] = BLUE_PRIMARY
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
    
    def _criar_botao_secundario(self, parent, texto, comando):
        """Cria um botão secundário estilizado"""
        btn = tk.Button(
            parent,
            text=texto,
            command=comando,
            bg=CARD_BG,
            fg=TEXT_PRIMARY,
            activebackground=DARKER_BG,
            activeforeground=TEXT_PRIMARY,
            **BTN_STYLE
        )
        btn.pack(side=tk.LEFT, padx=5)
        
    def _criar_timer(self):
        """Cria o timer de recuperação"""
        frame = tk.Frame(self.frame_principal, bg=DARK_BG)
        frame.pack(pady=(30, 40))  # Aumentar padding
        
        tk.Label(
            frame,
            text="Tempo restante até ativação do modo de recuperação:",
            bg=DARK_BG,
            fg=TEXT_SECONDARY,
            font=FONT_REGULAR
        ).pack()
        
        self.label_timer = tk.Label(
            frame,
            text="00:00:00",
            bg=DARK_BG,
            fg=BLUE_PRIMARY,
            font=("Helvetica", 36, "bold")
        )
        self.label_timer.pack(pady=(15, 25))  # Aumentar padding
        
        # Botão de renovar período
        btn = tk.Button(
            frame,
            text="Renovar Período",
            command=self.renovar_periodo,
            bg=BLUE_PRIMARY,
            fg=TEXT_PRIMARY,
            activebackground=BLUE_SECONDARY,
            activeforeground=TEXT_PRIMARY,
            font=("Helvetica", 12),
            width=20,  # Largura fixa
            relief="flat",
            bd=0,
            cursor="hand2"
        )
        btn.pack()
        
        # Efeitos hover
        def on_enter(e):
            btn['background'] = BLUE_SECONDARY
        def on_leave(e):
            btn['background'] = BLUE_PRIMARY
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
    
    def sair(self):
        """Sai da aplicação"""
        if ask_yes_no(self.janela, "Sair", "Tem certeza que deseja sair?"):
            self.janela.quit()
    
    def adicionar_senha(self, janela_pai=None, callback_atualizacao=None):
        """Adiciona uma nova senha com visual moderno"""
        janela = tk.Toplevel(janela_pai if janela_pai else self.janela)
        self._aplicar_estilo_janela(janela, "Adicionar Nova Senha")
        janela.geometry("500x400")
        janela.grab_set()
        
        # Frame principal
        frame_principal = tk.Frame(janela, **FRAME_STYLE)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Campos de entrada com estilo moderno
        entrada_titulo = self._criar_entrada_texto(frame_principal, "Título")
        entrada_senha = self._criar_entrada_texto(frame_principal, "Senha", show="*")
        
        # ... resto do código ...
    
    @aplicar_estilo_padrao
    def gerenciar_senhas(self):
        """Gerencia as senhas armazenadas"""
        janela = tk.Toplevel(self.janela)
        janela.title("Gerenciar Senhas")
        janela.geometry("700x500")
        janela.grab_set()  # Torna a janela modal
        
        tk.Label(janela, text="Senhas Armazenadas", font=("Arial", 14)).pack(pady=10)
        
        # Frame para pesquisa e filtros
        frame_pesquisa = tk.Frame(janela)
        frame_pesquisa.pack(fill=tk.X, padx=20, pady=5)
        
        # ... (código existente para pesquisa e filtros)
        
        # Lista de senhas
        frame_lista = tk.Frame(janela)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(frame_lista, width=70, height=15, yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=listbox.yview)
        
        # Armazenar IDs das senhas
        ids_senhas = []
        
        # Função para atualizar a lista de senhas
        def atualizar_lista():
            listbox.delete(0, tk.END)
            ids_senhas.clear()
            
            # Obter todas as senhas
            sucesso, mensagem, senhas = self.cofre.obter_senhas()
            
            if sucesso and senhas:
                for senha in senhas:
                    listbox.insert(tk.END, f"{senha['titulo']} - {senha['descricao']}")
                    ids_senhas.append(senha['id'])
        
        # Inicialmente, mostrar todas as senhas
        atualizar_lista()
        
        # Funções para gerenciar senhas
        def visualizar():
            selecao = listbox.curselection()
            if not selecao:
                show_info(janela, "Aviso", "Selecione uma senha para visualizar")
                return
            
            indice = selecao[0]
            id_senha = ids_senhas[indice]
            
            self.visualizar_senha(id_senha, janela)
        
        def excluir():
            selecao = listbox.curselection()
            if not selecao:
                show_info(janela, "Aviso", "Selecione uma senha para excluir")
                return
            
            indice = selecao[0]
            id_senha = ids_senhas[indice]
            titulo = listbox.get(indice).split(" - ")[0]
            
            # Confirmar exclusão
            confirmacao = ask_yes_no(
                janela, 
                "Confirmar Exclusão", 
                f"Tem certeza que deseja excluir a senha '{titulo}'?"
            )
            
            if confirmacao:
                sucesso, mensagem = self.cofre.excluir_senha(id_senha)
                
                if sucesso:
                    show_success(janela, "Sucesso", mensagem)
                    atualizar_lista()
                    
                    # Atualizar contador na tela principal
                    self.atualizar_contadores()
                else:
                    show_error(janela, "Erro", mensagem)
        
        # Frame para botões
        frame_botoes = tk.Frame(janela)
        frame_botoes.pack(pady=10)
        
        tk.Button(frame_botoes, text="Visualizar", command=visualizar).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="Adicionar", command=lambda: self.adicionar_senha(janela, atualizar_lista)).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="Excluir", command=excluir).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="Fechar", command=janela.destroy).pack(side=tk.LEFT, padx=10)
    
    def adicionar_nota(self, janela_pai=None, callback_atualizacao=None):
        """Adiciona uma nova nota"""
        janela = tk.Toplevel(janela_pai if janela_pai else self.janela)
        janela.title("Adicionar Nota")
        janela.geometry("500x400")
        janela.grab_set()  # Torna a janela modal
        
        tk.Label(janela, text="Adicionar Nova Nota", font=("Arial", 14)).pack(pady=10)
        
        tk.Label(janela, text="Título:").pack(anchor=tk.W, padx=20, pady=(10, 0))
        entrada_titulo = tk.Entry(janela, width=40)
        entrada_titulo.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        tk.Label(janela, text="Conteúdo:").pack(anchor=tk.W, padx=20, pady=(10, 0))
        entrada_conteudo = tk.Text(janela, width=40, height=10)
        entrada_conteudo.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        def salvar():
            titulo = entrada_titulo.get()
            conteudo = entrada_conteudo.get("1.0", tk.END).strip()
            
            if not titulo or not conteudo:
                show_error(janela, "Erro", "Título e conteúdo são obrigatórios")
                return
            
            sucesso, mensagem = self.cofre.adicionar_nota(titulo, conteudo)
            
            if sucesso:
                show_success(janela, "Sucesso", mensagem)
                janela.destroy()
                
                # Atualizar lista de notas se fornecido um callback
                if callback_atualizacao:
                    callback_atualizacao()
                
                # Atualizar contador na tela principal
                self.atualizar_contadores()
            else:
                show_error(janela, "Erro", mensagem)
        
        frame_botoes = tk.Frame(janela)
        frame_botoes.pack(pady=10)
        
        tk.Button(frame_botoes, text="Salvar", command=salvar).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="Cancelar", command=janela.destroy).pack(side=tk.LEFT, padx=10)
    
    @aplicar_estilo_padrao
    def gerenciar_notas(self):
        """Abre a janela para gerenciar notas"""
        janela_notas = tk.Toplevel(self.janela)
        janela_notas.title("Gerenciar Notas")
        janela_notas.geometry("600x500")
        
        tk.Label(janela_notas, text="Notas Armazenadas", font=("Arial", 14)).pack(pady=10)
        
        # Lista de notas
        frame_lista = tk.Frame(janela_notas)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.lista_notas = tk.Listbox(frame_lista, width=50, height=15)
        self.lista_notas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Adicionar barra de rolagem
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Conectar a barra de rolagem à lista
        self.lista_notas.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.lista_notas.yview)
        
        # Inicializar lista de IDs
        self.notas_ids = []
        
        # Carregar notas
        self.atualizar_lista_notas()
        
        # Botões
        frame_botoes = tk.Frame(janela_notas)
        frame_botoes.pack(pady=15)
        
        # Conectar o botão Visualizar à função visualizar_nota
        tk.Button(frame_botoes, text="Visualizar", command=self.visualizar_nota).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="Adicionar", command=lambda: self.adicionar_nota(janela_notas)).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="Excluir", command=lambda: self.excluir_nota(janela_notas)).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="Fechar", command=janela_notas.destroy).pack(side=tk.LEFT, padx=10)
    
    def adicionar_arquivo(self, janela_pai=None, callback_atualizacao=None):
        """Adiciona um novo arquivo"""
        caminho_arquivo = filedialog.askopenfilename(
            title="Selecionar Arquivo",
            filetypes=[("Todos os arquivos", "*.*")]
        )
        
        if not caminho_arquivo:
            return
        
        print("\n=== Debug Adicionar Arquivo ===")
        print(f"Arquivo selecionado: {caminho_arquivo}")
        
        janela = tk.Toplevel(janela_pai if janela_pai else self.janela)
        janela.title("Adicionar Novo Arquivo")
        janela.geometry("500x200")
        janela.grab_set()  # Torna a janela modal
        
        tk.Label(janela, text="Adicionar Novo Arquivo", font=("Arial", 14)).pack(pady=10)
        
        tk.Label(janela, text=f"Arquivo: {os.path.basename(caminho_arquivo)}").pack(anchor=tk.W, padx=20, pady=(10, 0))
        
        tk.Label(janela, text="Descrição:").pack(anchor=tk.W, padx=20, pady=(10, 0))
        entrada_descricao = tk.Entry(janela, width=40)
        entrada_descricao.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        def salvar():
            descricao = entrada_descricao.get()
            
            print(f"Tentando adicionar arquivo com descrição: {descricao}")
            sucesso, mensagem = self.cofre.adicionar_arquivo(caminho_arquivo, descricao)
            print(f"Resultado: sucesso={sucesso}, mensagem={mensagem}")
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem, parent=janela)
                janela.destroy()
                
                # Atualizar lista de arquivos se fornecido um callback
                if callback_atualizacao:
                    callback_atualizacao()
                
                # Forçar atualização dos contadores
                self.atualizar_contadores()
                
                # Atualizar a interface principal
                self.atualizar_interface()
            else:
                messagebox.showerror("Erro", mensagem, parent=janela)
        
        frame_botoes = tk.Frame(janela)
        frame_botoes.pack(pady=10)
        
        tk.Button(frame_botoes, text="Salvar", command=salvar).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="Cancelar", command=janela.destroy).pack(side=tk.LEFT, padx=10)
    
    def gerenciar_arquivos(self):
        """Gerencia os arquivos armazenados"""
        janela = tk.Toplevel(self.janela)
        janela.title("Gerenciar Arquivos")
        janela.geometry("700x500")
        janela.grab_set()  # Torna a janela modal
        
        tk.Label(janela, text="Arquivos Armazenados", font=("Arial", 14)).pack(pady=10)
        
        # Lista de arquivos
        frame_lista = tk.Frame(janela)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(frame_lista, width=70, height=15, yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=listbox.yview)
        
        # Armazenar IDs dos arquivos
        ids_arquivos = []
        
        # Função para atualizar a lista de arquivos
        def atualizar_lista():
            listbox.delete(0, tk.END)
            ids_arquivos.clear()
            
            # Obter todos os arquivos
            sucesso, mensagem, arquivos = self.cofre.obter_arquivos()
            
            if sucesso and arquivos:
                for arquivo in arquivos:
                    descricao = arquivo.get('descricao', '')
                    listbox.insert(tk.END, f"{arquivo['nome_original']} - {descricao if descricao else ''}")
                    ids_arquivos.append(arquivo['id'])
            else:
                print(f"Erro ao obter arquivos: {mensagem}")
                print(f"Sucesso: {sucesso}, Arquivos: {arquivos}")
        
        # Inicialmente, mostrar todos os arquivos
        atualizar_lista()
        
        # Funções para gerenciar arquivos
        def baixar():
            selecao = listbox.curselection()
            if not selecao:
                show_info(janela, "Aviso", "Selecione um arquivo para baixar")
                return
            
            indice = selecao[0]
            id_arquivo = ids_arquivos[indice]
            
            # Solicitar local para salvar o arquivo
            destino = filedialog.asksaveasfilename(
                parent=janela,
                title="Salvar Arquivo Como",
                initialfile=listbox.get(indice).split(" - ")[0]
            )
            
            if destino:
                sucesso, mensagem = self.cofre.baixar_arquivo(id_arquivo, destino)
                
                if sucesso:
                    show_success(janela, "Sucesso", mensagem)
                else:
                    show_error(janela, "Erro", mensagem)
        
        def excluir():
            selecao = listbox.curselection()
            if not selecao:
                show_info(janela, "Aviso", "Selecione um arquivo para excluir")
                return
            
            indice = selecao[0]
            id_arquivo = ids_arquivos[indice]
            nome = listbox.get(indice)
            
            # Confirmar exclusão
            confirmacao = ask_yes_no(
                janela, 
                "Confirmar Exclusão", 
                f"Tem certeza que deseja excluir o arquivo '{nome}'?"
            )
            
            if confirmacao:
                sucesso, mensagem = self.cofre.excluir_arquivo(id_arquivo)
                
                if sucesso:
                    show_success(janela, "Sucesso", mensagem)
                    atualizar_lista()
                    
                    # Atualizar contador na tela principal
                    self.atualizar_contadores()
                else:
                    show_error(janela, "Erro", mensagem)
        
        # Frame para botões
        frame_botoes = tk.Frame(janela)
        frame_botoes.pack(pady=10)
        
        tk.Button(frame_botoes, text="Baixar", command=baixar).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="Adicionar", command=lambda: self.adicionar_arquivo(janela, atualizar_lista)).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="Excluir", command=excluir).pack(side=tk.LEFT, padx=10)
        
        # Adicionar callback quando a janela for fechada
        def ao_fechar():
            self.atualizar_contadores()
            janela.destroy()
        
        # Modificar o botão Fechar para usar o novo callback
        tk.Button(frame_botoes, text="Fechar", command=ao_fechar).pack(side=tk.LEFT, padx=10)
    
    def alterar_configuracoes(self):
        """Altera as configurações gerais do sistema"""
        # Carregar configurações atuais
        try:
            with open(self.cofre.caminho_config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar configurações: {str(e)}")
            return
        
        janela = tk.Toplevel(self.janela)
        janela.title("Configurações Gerais")
        janela.geometry("500x300")
        janela.grab_set()  # Torna a janela modal
        
        tk.Label(janela, text="Configurações do Sistema", font=("Arial", 14)).pack(pady=10)
        
        # Intervalo de confirmação
        frame_intervalo = tk.Frame(janela)
        frame_intervalo.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(frame_intervalo, text="Intervalo de confirmação (dias):").pack(side=tk.LEFT)
        entrada_intervalo = tk.Entry(frame_intervalo, width=10)
        entrada_intervalo.pack(side=tk.LEFT, padx=10)
        entrada_intervalo.insert(0, str(config.get("intervalo_confirmacao", 30)))
        
        # Máximo de tentativas
        frame_tentativas = tk.Frame(janela)
        frame_tentativas.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(frame_tentativas, text="Máximo de tentativas de senha:").pack(side=tk.LEFT)
        entrada_tentativas = tk.Entry(frame_tentativas, width=10)
        entrada_tentativas.pack(side=tk.LEFT, padx=10)
        entrada_tentativas.insert(0, str(config.get("max_tentativas_senha", 5)))
        
        # Autodestruição
        frame_autodestruicao = tk.Frame(janela)
        frame_autodestruicao.pack(fill=tk.X, padx=20, pady=5)
        
        autodestruicao = tk.BooleanVar()
        autodestruicao.set(config.get("autodestruicao_ativada", True))
        
        tk.Label(frame_autodestruicao, text="Autodestruição ativada:").pack(side=tk.LEFT)
        tk.Checkbutton(frame_autodestruicao, variable=autodestruicao).pack(side=tk.LEFT, padx=10)
        
        # Nome de exibição
        frame_nome = tk.Frame(janela)
        frame_nome.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(frame_nome, text="Nome de exibição:").pack(side=tk.LEFT)
        entrada_nome = tk.Entry(frame_nome, width=30)
        entrada_nome.pack(side=tk.LEFT, padx=10)
        entrada_nome.insert(0, config.get("nome_exibicao", "Bloco de Notas Portátil"))
        
        def salvar():
            try:
                intervalo = int(entrada_intervalo.get())
                tentativas = int(entrada_tentativas.get())
                
                if intervalo <= 0 or tentativas <= 0:
                    messagebox.showerror("Erro", "Os valores devem ser maiores que zero")
                    return
                
                # Atualizar configurações
                config["intervalo_confirmacao"] = intervalo
                config["max_tentativas_senha"] = tentativas
                config["autodestruicao_ativada"] = autodestruicao.get()
                config["nome_exibicao"] = entrada_nome.get()
                
                # Salvar configurações
                with open(self.cofre.caminho_config, 'w') as f:
                    json.dump(config, f, indent=4)
                
                # Atualizar título da janela
                self.janela.title(config["nome_exibicao"])
                
                # Atualizar max_tentativas no objeto cofre
                self.cofre.max_tentativas = tentativas
                
                messagebox.showinfo("Sucesso", "Configurações salvas com sucesso")
                janela.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Os valores devem ser números inteiros")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar configurações: {str(e)}")
        
        frame_botoes = tk.Frame(janela)
        frame_botoes.pack(pady=20)
        
        tk.Button(frame_botoes, text="Salvar", command=salvar).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="Cancelar", command=janela.destroy).pack(side=tk.LEFT, padx=10)
    
    def reconfigurar_senhas(self):
        """Permite ao usuário reconfigurar suas senhas"""
        janela = tk.Toplevel(self.janela)
        janela.title("Reconfigurar Senhas")
        janela.geometry("500x400")
        janela.grab_set()  # Torna a janela modal
        
        tk.Label(janela, text="Reconfigurar Senhas", font=("Arial", 14)).pack(pady=10)
        
        # Campos de entrada
        frame_campos = tk.Frame(janela)
        frame_campos.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(frame_campos, text="Senha Atual:").pack(anchor=tk.W, pady=(10, 0))
        entrada_senha_atual = tk.Entry(frame_campos, width=40, show="*")
        entrada_senha_atual.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame_campos, text="Nova Senha Principal:").pack(anchor=tk.W, pady=(10, 0))
        entrada_nova_senha = tk.Entry(frame_campos, width=40, show="*")
        entrada_nova_senha.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame_campos, text="Confirmar Nova Senha Principal:").pack(anchor=tk.W, pady=(10, 0))
        entrada_confirmar_nova_senha = tk.Entry(frame_campos, width=40, show="*")
        entrada_confirmar_nova_senha.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame_campos, text="Nova Senha de Recuperação:").pack(anchor=tk.W, pady=(10, 0))
        entrada_nova_senha_heranca = tk.Entry(frame_campos, width=40, show="*")
        entrada_nova_senha_heranca.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame_campos, text="Confirmar Nova Senha de Recuperação:").pack(anchor=tk.W, pady=(10, 0))
        entrada_confirmar_nova_senha_heranca = tk.Entry(frame_campos, width=40, show="*")
        entrada_confirmar_nova_senha_heranca.pack(fill=tk.X, pady=(0, 10))
        
        def salvar():
            senha_atual = entrada_senha_atual.get()
            nova_senha = entrada_nova_senha.get()
            confirmar_nova_senha = entrada_confirmar_nova_senha.get()
            nova_senha_heranca = entrada_nova_senha_heranca.get()
            confirmar_nova_senha_heranca = entrada_confirmar_nova_senha_heranca.get()
            
            if not senha_atual or not nova_senha or not nova_senha_heranca:
                show_error(janela, "Erro", "Todos os campos são obrigatórios")
                return
            
            if nova_senha != confirmar_nova_senha:
                show_error(janela, "Erro", "As novas senhas principais não coincidem")
                return
            
            if nova_senha_heranca != confirmar_nova_senha_heranca:
                show_error(janela, "Erro", "As novas senhas de recuperação não coincidem")
                return
            
            if nova_senha == nova_senha_heranca:
                show_error(janela, "Erro", "A senha principal e a senha de recuperação não podem ser iguais")
                return
            
            sucesso, mensagem = self.cofre.reconfigurar_senhas(senha_atual, nova_senha, nova_senha_heranca)
            
            if sucesso:
                show_success(janela, "Sucesso", mensagem)
                janela.destroy()
            else:
                show_error(janela, "Erro", mensagem)
        
        # Vincular a tecla Enter a cada campo para avançar para o próximo ou salvar
        entrada_senha_atual.bind("<Return>", lambda event: entrada_nova_senha.focus_set())
        entrada_nova_senha.bind("<Return>", lambda event: entrada_confirmar_nova_senha.focus_set())
        entrada_confirmar_nova_senha.bind("<Return>", lambda event: entrada_nova_senha_heranca.focus_set())
        entrada_nova_senha_heranca.bind("<Return>", lambda event: entrada_confirmar_nova_senha_heranca.focus_set())
        entrada_confirmar_nova_senha_heranca.bind("<Return>", lambda event: salvar())
        
        frame_botoes = tk.Frame(janela)
        frame_botoes.pack(pady=20)
        
        tk.Button(frame_botoes, text="Salvar", command=salvar).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="Cancelar", command=janela.destroy).pack(side=tk.LEFT, padx=10)
    
    def gerenciar_categorias(self):
        """Gerencia as categorias armazenadas"""
        janela = tk.Toplevel(self.janela)
        janela.title("Gerenciar Categorias")
        janela.geometry("600x400")
        janela.grab_set()  # Torna a janela modal
        
        tk.Label(janela, text="Categorias Armazenadas", font=("Arial", 14)).pack(pady=10)
        
        # Lista de categorias
        frame_lista = tk.Frame(janela)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(frame_lista, width=70, height=15, yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=listbox.yview)
        
        # Obter categorias
        sucesso, mensagem, categorias = self.cofre.obter_categorias()
        
        ids_categorias = []
        
        if sucesso:
            for categoria in categorias:
                listbox.insert(tk.END, categoria['nome'])
                ids_categorias.append(categoria['id'])
        
        def atualizar_lista():
            listbox.delete(0, tk.END)
            for categoria in categorias:
                listbox.insert(tk.END, categoria['nome'])
        
        def editar_categoria():
            selecao = listbox.curselection()
            if not selecao:
                show_info(janela, "Aviso", "Selecione uma categoria para editar")
                return
            
            indice = selecao[0]
            id_categoria = ids_categorias[indice]
            nome_atual = listbox.get(indice)
            
            # Solicitar novo nome
            novo_nome = simpledialog.askstring("Editar Categoria", "Novo nome:", initialvalue=nome_atual, parent=janela)
            
            if novo_nome and novo_nome.strip():
                sucesso, mensagem = self.cofre.editar_categoria(id_categoria, novo_nome.strip())
                
                if sucesso:
                    show_success(janela, "Sucesso", mensagem)
                    atualizar_lista()
                else:
                    show_error(janela, "Erro", mensagem)
        
        def excluir_categoria():
            selecao = listbox.curselection()
            if not selecao:
                show_info(janela, "Aviso", "Selecione uma categoria para excluir")
                return
            
            indice = selecao[0]
            id_categoria = ids_categorias[indice]
            nome = listbox.get(indice)
            
            # Confirmar exclusão
            confirmacao = ask_yes_no(
                janela, 
                "Confirmar Exclusão", 
                f"Tem certeza que deseja excluir a categoria '{nome}'? Isso não excluirá os itens associados."
            )
            
            if confirmacao:
                sucesso, mensagem = self.cofre.excluir_categoria(id_categoria)
                
                if sucesso:
                    show_success(janela, "Sucesso", mensagem)
                    atualizar_lista()
                else:
                    show_error(janela, "Erro", mensagem)
        
        # Frame para adicionar categoria
        frame_adicionar = tk.Frame(janela)
        frame_adicionar.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(frame_adicionar, text="Nova Categoria:").pack(side=tk.LEFT)
        entrada_categoria = tk.Entry(frame_adicionar, width=30)
        entrada_categoria.pack(side=tk.LEFT, padx=10)
        
        def adicionar_categoria():
            nome = entrada_categoria.get().strip()
            if not nome:
                show_info(janela, "Aviso", "Digite um nome para a categoria")
                return
            
            sucesso, mensagem = self.cofre.criar_categoria(nome)
            
            if sucesso:
                show_success(janela, "Sucesso", mensagem)
                entrada_categoria.delete(0, tk.END)
                atualizar_lista()
            else:
                show_error(janela, "Erro", mensagem)
        
        tk.Button(frame_adicionar, text="Adicionar", command=adicionar_categoria).pack(side=tk.LEFT)
        
        # Frame para botões
        frame_botoes = tk.Frame(janela)
        frame_botoes.pack(pady=10)
        
        tk.Button(frame_botoes, text="Editar", command=editar_categoria).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="Excluir", command=excluir_categoria).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="Fechar", command=janela.destroy).pack(side=tk.LEFT, padx=10)
    
    def backup_restauracao(self):
        """Gerencia backup e restauração do sistema"""
        janela = tk.Toplevel(self.janela)
        janela.title("Backup e Restauração")
        janela.geometry("500x300")
        janela.grab_set()  # Torna a janela modal
        
        tk.Label(janela, text="Backup e Restauração", font=("Arial", 14)).pack(pady=10)
        
        # Frame para backup
        frame_backup = tk.LabelFrame(janela, text="Fazer Backup")
        frame_backup.pack(fill=tk.X, padx=20, pady=10)
        
        def selecionar_destino_backup():
            diretorio = filedialog.askdirectory(title="Selecionar Diretório para Backup")
            if diretorio:
                entrada_destino_backup.delete(0, tk.END)
                entrada_destino_backup.insert(0, diretorio)
        
        frame_destino = tk.Frame(frame_backup)
        frame_destino.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(frame_destino, text="Destino:").pack(side=tk.LEFT)
        entrada_destino_backup = tk.Entry(frame_destino, width=40)
        entrada_destino_backup.pack(side=tk.LEFT, padx=5)
        tk.Button(frame_destino, text="...", command=selecionar_destino_backup).pack(side=tk.LEFT)
        
        def fazer_backup():
            destino = entrada_destino_backup.get()
            if not destino:
                messagebox.showinfo("Aviso", "Selecione um diretório de destino")
                return
            
            sucesso, mensagem = self.cofre.fazer_backup(destino)
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem, parent=janela)
            else:
                messagebox.showerror("Erro", mensagem, parent=janela)
        
        tk.Button(frame_backup, text="Fazer Backup", command=fazer_backup).pack(pady=5)
        
        # Frame para restauração
        frame_restauracao = tk.LabelFrame(janela, text="Restaurar Backup")
        frame_restauracao.pack(fill=tk.X, padx=20, pady=10)
        
        def selecionar_arquivo_backup():
            arquivo = filedialog.askopenfilename(
                title="Selecionar Arquivo de Backup",
                filetypes=[("Arquivos de Backup Criptografados", "*.enc")]
            )
            if arquivo:
                entrada_arquivo_backup.delete(0, tk.END)
                entrada_arquivo_backup.insert(0, arquivo)
        
        frame_arquivo = tk.Frame(frame_restauracao)
        frame_arquivo.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(frame_arquivo, text="Arquivo:").pack(side=tk.LEFT)
        entrada_arquivo_backup = tk.Entry(frame_arquivo, width=40)
        entrada_arquivo_backup.pack(side=tk.LEFT, padx=5)
        tk.Button(frame_arquivo, text="...", command=selecionar_arquivo_backup).pack(side=tk.LEFT)
        
        def restaurar_backup():
            arquivo_backup = entrada_arquivo_backup.get()
            
            if not arquivo_backup:
                messagebox.showinfo("Aviso", "Selecione um arquivo de backup")
                return
            
            # Confirmar restauração
            confirmacao = ask_yes_no(
                janela, 
                "Confirmar Restauração", 
                "A restauração substituirá todos os dados atuais. Tem certeza que deseja continuar?"
            )
            
            if confirmacao:
                sucesso, mensagem = self.cofre.restaurar_backup(arquivo_backup)
                
                if sucesso:
                    show_success(janela, "Sucesso", mensagem)
                    janela.destroy()
                    
                    # Reiniciar a aplicação
                    self.janela.after(2000, self.reiniciar)
                else:
                    show_error(janela, "Erro", mensagem)
        
        tk.Button(frame_restauracao, text="Restaurar Backup", command=restaurar_backup).pack(pady=5)
        
        # Botão para fechar
        tk.Button(janela, text="Fechar", command=janela.destroy).pack(pady=10)
    
    def atualizar_contadores(self):
        """Atualiza os contadores de itens na tela principal"""
        if not hasattr(self, 'label_contador_senhas'):
            return  # Se os labels não existirem, não faz nada
        
        # Obter contagens
        sucesso_senhas, mensagem_senhas, senhas = self.cofre.listar_senhas()
        sucesso_notas, mensagem_notas, notas = self.cofre.listar_notas()
        sucesso_arquivos, mensagem_arquivos, arquivos = self.cofre.listar_arquivos()
        
        print("\n=== Debug Contadores ===")
        print(f"Arquivos - Sucesso: {sucesso_arquivos}")
        print(f"Mensagem: {mensagem_arquivos}")
        print(f"Arquivos: {arquivos}")
        print(f"Tipo de arquivos: {type(arquivos)}")
        if arquivos:
            print(f"Número de arquivos: {len(arquivos)}")
        print("=====================\n")
        
        # Atualizar labels com verificação de None
        self.label_contador_senhas.config(text=f"Senhas: {len(senhas) if sucesso_senhas and senhas else 0}")
        self.label_contador_notas.config(text=f"Notas: {len(notas) if sucesso_notas and notas else 0}")
        self.label_contador_arquivos.config(text=f"Arquivos: {len(arquivos) if sucesso_arquivos and arquivos else 0}")
    
    def visualizar_senha(self, id_senha, janela_pai):
        """Visualiza os detalhes de uma senha"""
        sucesso, mensagem, senha = self.cofre.obter_senha(id_senha)
        
        if not sucesso:
            show_error(janela_pai or self.janela, "Erro", mensagem)
            return
        
        janela_senha = tk.Toplevel(janela_pai)
        janela_senha.title(senha['titulo'])
        janela_senha.geometry("400x300")
        janela_senha.grab_set()  # Torna a janela modal
        
        # Senha
        frame_senha = tk.Frame(janela_senha)
        frame_senha.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(frame_senha, text="Senha:").pack(side=tk.LEFT)
        
        var_senha = tk.StringVar()
        var_senha.set(senha['senha'])
        
        entrada_senha = tk.Entry(frame_senha, textvariable=var_senha, width=30, show="*")
        entrada_senha.pack(side=tk.LEFT, padx=10)
        
        def mostrar_senha():
            if entrada_senha.cget('show') == '*':
                entrada_senha.config(show='')
                check_mostrar.select()
            else:
                entrada_senha.config(show='*')
        
        var_mostrar = tk.BooleanVar()
        check_mostrar = tk.Checkbutton(frame_senha, text="Mostrar", variable=var_mostrar, command=mostrar_senha)
        check_mostrar.pack(side=tk.LEFT)
        
        # Descrição
        tk.Label(janela_senha, text="Descrição:").pack(anchor=tk.W, padx=20, pady=(10, 0))
        
        texto_descricao = tk.Text(janela_senha, width=40, height=10)
        texto_descricao.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        if senha['descricao']:
            texto_descricao.insert(tk.END, senha['descricao'])
        
        # Botões
        frame_botoes = tk.Frame(janela_senha)
        frame_botoes.pack(pady=10)
        
        def copiar_senha():
            self.janela.clipboard_clear()
            self.janela.clipboard_append(senha['senha'])
            self.janela.update()
            
            show_success(janela_senha, "Sucesso", "Senha copiada para a área de transferência")
        
        tk.Button(frame_botoes, text="Copiar", command=copiar_senha).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="Fechar", command=janela_senha.destroy).pack(side=tk.LEFT, padx=10)
    
    def visualizar_nota(self):
        """Visualiza o conteúdo de uma nota selecionada"""
        print("Função visualizar_nota chamada")
        selecao = self.lista_notas.curselection()
        if not selecao:
            show_error(self.janela, "Erro", "Selecione uma nota para visualizar")
            return
        
        titulo_nota = self.lista_notas.get(selecao[0])
        id_nota = self.notas_ids[selecao[0]]
        
        print(f"Nota selecionada: ID={id_nota}, Título={titulo_nota}")
        
        # Obter conteúdo da nota
        sucesso, mensagem, conteudo = self.cofre.obter_nota(id_nota)
        
        print(f"Resultado: sucesso={sucesso}, mensagem={mensagem}")
        
        if not sucesso:
            messagebox.showerror("Erro", mensagem)
            return
        
        # Criar janela para visualizar a nota
        janela_nota = tk.Toplevel(self.janela)
        janela_nota.title(titulo_nota)
        janela_nota.geometry("600x400")
        
        # Área de texto para exibir o conteúdo
        texto_nota = tk.Text(janela_nota, wrap=tk.WORD, font=("Courier", 12))
        texto_nota.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Inserir conteúdo
        texto_nota.insert(tk.END, conteudo)
        texto_nota.config(state=tk.DISABLED)  # Tornar somente leitura
        
        # Botão para fechar
        tk.Button(janela_nota, text="Fechar", command=janela_nota.destroy).pack(pady=10)
    
    def excluir_nota(self, janela_pai):
        """Exclui uma nota"""
        selecao = self.lista_notas.curselection()
        if not selecao:
            show_info(janela_pai, "Aviso", "Selecione uma nota para excluir")
            return
        
        indice = selecao[0]
        id_nota = self.notas_ids[indice]
        titulo = self.lista_notas.get(indice)
        
        # Confirmar exclusão
        confirmacao = ask_yes_no(
            janela_pai, 
            "Confirmar Exclusão", 
            f"Tem certeza que deseja excluir a nota '{titulo}'?"
        )
        
        if confirmacao:
            sucesso, mensagem = self.cofre.excluir_nota(id_nota)
            
            if sucesso:
                show_success(janela_pai, "Sucesso", mensagem)
                self.atualizar_lista_notas()
                
                # Atualizar contador na tela principal
                self.atualizar_contadores()
            else:
                show_error(janela_pai, "Erro", mensagem)
    
    def depurar_arquivos(self):
        """Função de depuração para verificar o estado dos arquivos no banco de dados"""
        try:
            # Conectar diretamente ao banco de dados
            conn = sqlite3.connect(self.cofre.caminho_db)
            cursor = conn.cursor()
            
            # Obter todos os registros da tabela de arquivos
            cursor.execute("SELECT * FROM arquivos")
            resultados = cursor.fetchall()
            
            # Obter nomes das colunas
            cursor.execute("PRAGMA table_info(arquivos)")
            colunas = [info[1] for info in cursor.fetchall()]
            
            conn.close()
            
            # Exibir resultados
            print("=== Depuração da tabela de arquivos ===")
            print(f"Colunas: {colunas}")
            print(f"Número de registros: {len(resultados)}")
            for registro in resultados:
                print(registro)
            print("=====================================")
            
            # Verificar arquivos físicos
            diretorio_arquivos = os.path.join(self.cofre.caminho_base, "arquivos")
            arquivos_fisicos = os.listdir(diretorio_arquivos)
            print(f"Arquivos físicos no diretório: {len(arquivos_fisicos)}")
            for arquivo in arquivos_fisicos:
                print(arquivo)
            
            return True
        except Exception as e:
            print(f"Erro na depuração: {str(e)}")
            return False

    def criar_compartimento(self):
        """Abre a janela para criar um novo compartimento"""
        # Verificar se está em modo restrito
        if hasattr(self, 'modo_acesso_restrito') and self.modo_acesso_restrito:
            show_error(self.janela, "Acesso Negado", "Você está em modo de acesso restrito.\nNão é possível criar novos compartimentos.")
            return
        
        janela_criar = tk.Toplevel(self.janela)
        janela_criar.title("Criar Novo Compartimento")
        janela_criar.geometry("500x300")
        janela_criar.grab_set()  # Torna a janela modal
        
        tk.Label(janela_criar, text="Criar Novo Compartimento", font=("Arial", 14)).pack(pady=10)
        
        # Nome do compartimento
        frame_nome = tk.Frame(janela_criar)
        frame_nome.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(frame_nome, text="Nome:").pack(side=tk.LEFT)
        entrada_nome = tk.Entry(frame_nome, width=30)
        entrada_nome.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Descrição
        tk.Label(janela_criar, text="Descrição:").pack(anchor=tk.W, padx=20, pady=(10, 0))
        
        texto_descricao = tk.Text(janela_criar, width=50, height=5)
        texto_descricao.pack(fill=tk.X, padx=20, pady=5)
        
        # Aviso
        tk.Label(janela_criar, text="IMPORTANTE: Guarde a frase mnemônica em um local seguro.\nEla será necessária para recuperar este compartimento.", fg="red").pack(pady=10)
        
        def confirmar_criar():
            nome = entrada_nome.get().strip()
            descricao = texto_descricao.get("1.0", tk.END).strip()
            
            if not nome:
                show_error(janela_criar, "Erro", "O nome do compartimento é obrigatório")
                return
            
            # Adicionar depuração
            print(f"Tentando criar compartimento: {nome}")
            print(f"Descrição: {descricao}")
            
            try:
                # Criar compartimento
                sucesso, mensagem, frase = self.cofre.criar_compartimento(nome, descricao)
                print(f"Resultado: sucesso={sucesso}, mensagem={mensagem}")
            except Exception as e:
                print(f"ERRO: {str(e)}")
                traceback.print_exc()
                messagebox.showerror("Erro", f"Erro ao criar compartimento: {str(e)}", parent=janela_criar)
                return
            
            # Resto do código...
            
            if sucesso:
                # Mostrar a frase mnemônica
                janela_frase = tk.Toplevel(janela_criar)
                janela_frase.title("Frase Mnemônica")
                janela_frase.geometry("600x300")
                janela_frase.grab_set()
                
                tk.Label(janela_frase, text="Frase Mnemônica do Compartimento", font=("Arial", 14)).pack(pady=10)
                
                tk.Label(janela_frase, text="GUARDE ESTA FRASE EM UM LOCAL SEGURO!", fg="red", font=("Arial", 12, "bold")).pack(pady=5)
                
                frame_frase = tk.Frame(janela_frase)
                frame_frase.pack(fill=tk.X, padx=20, pady=10)
                
                texto_frase = tk.Text(frame_frase, width=50, height=3, font=("Courier", 12))
                texto_frase.pack(fill=tk.X, expand=True)
                texto_frase.insert(tk.END, frase)
                texto_frase.config(state="disabled")  # Somente leitura
                
                def copiar_frase():
                    self.janela.clipboard_clear()
                    self.janela.clipboard_append(frase)
                    self.janela.update()
                    
                    show_success(janela_frase, "Sucesso", "Frase copiada para a área de transferência")
                
                tk.Button(janela_frase, text="Copiar Frase", command=copiar_frase).pack(pady=5)
                
                tk.Label(janela_frase, text="Esta frase permite acesso direto a este compartimento.\nNão a compartilhe com ninguém que não deva ter acesso a estes dados.", fg="blue").pack(pady=10)
                
                tk.Button(janela_frase, text="Entendi, guardei a frase", command=janela_frase.destroy).pack(pady=10)
                
                # Ativar o novo compartimento
                self.cofre.ativar_compartimento_por_nome(nome)
                self.atualizar_interface()
                
                # Fechar janela de criação
                janela_criar.destroy()
            else:
                messagebox.showerror("Erro", mensagem, parent=janela_criar)
        
        # Botões
        frame_botoes = tk.Frame(janela_criar)
        frame_botoes.pack(pady=15)
        
        tk.Button(frame_botoes, text="Criar", command=confirmar_criar).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="Cancelar", command=janela_criar.destroy).pack(side=tk.LEFT, padx=10)

    def alternar_compartimento(self):
        """Abre a janela para alternar entre compartimentos existentes"""
        # Verificar se está em modo restrito
        if hasattr(self, 'modo_acesso_restrito') and self.modo_acesso_restrito:
            show_error(self.janela, "Acesso Negado", "Você está em modo de acesso restrito.\nNão é possível alternar entre compartimentos.")
            return
        
        # Obter lista de compartimentos
        sucesso, mensagem, compartimentos = self.cofre.listar_compartimentos()
        
        if not sucesso:
            show_error(self.janela, "Erro", mensagem)
            return
        
        if not compartimentos:
            show_info(self.janela, "Informação", "Não há compartimentos disponíveis. Crie um novo compartimento primeiro.")
            return
        
        janela_alternar = tk.Toplevel(self.janela)
        janela_alternar.title("Alternar Compartimento")
        janela_alternar.geometry("500x400")
        janela_alternar.grab_set()  # Torna a janela modal
        
        tk.Label(janela_alternar, text="Selecione um Compartimento", font=("Arial", 14)).pack(pady=10)
        
        # Lista de compartimentos
        frame_lista = tk.Frame(janela_alternar)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Criar Treeview
        colunas = ("nome", "descricao", "data_criacao")
        tree = ttk.Treeview(frame_lista, columns=colunas, show="headings")
        
        # Definir cabeçalhos
        tree.heading("nome", text="Nome")
        tree.heading("descricao", text="Descrição")
        tree.heading("data_criacao", text="Data de Criação")
        
        # Definir larguras
        tree.column("nome", width=100)
        tree.column("descricao", width=200)
        tree.column("data_criacao", width=150)
        
        # Adicionar dados
        for comp in compartimentos:
            data_criacao = comp["data_criacao"]
            try:
                # Tentar formatar a data
                data_obj = datetime.datetime.fromisoformat(data_criacao)
                data_formatada = data_obj.strftime("%d/%m/%Y %H:%M")
            except:
                data_formatada = data_criacao
            
            tree.insert("", tk.END, values=(comp["nome"], comp["descricao"] or "", data_formatada))
        
        # Adicionar barra de rolagem
        scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        def confirmar_alternar():
            selecao = tree.selection()
            if not selecao:
                show_error(janela_alternar, "Erro", "Selecione um compartimento")
                return
            
            item = tree.item(selecao[0])
            nome_compartimento = item["values"][0]
            
            # Ativar compartimento
            sucesso, mensagem = self.cofre.ativar_compartimento_por_nome(nome_compartimento)
            
            if sucesso:
                show_success(janela_alternar, "Sucesso", mensagem)
                self.atualizar_interface()
                janela_alternar.destroy()
            else:
                show_error(janela_alternar, "Erro", mensagem)
        
        # Botões
        frame_botoes = tk.Frame(janela_alternar)
        frame_botoes.pack(pady=15)
        
        tk.Button(frame_botoes, text="Ativar", command=confirmar_alternar).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="Cancelar", command=janela_alternar.destroy).pack(side=tk.LEFT, padx=10)

    def acessar_por_frase(self):
        """Abre a janela para acessar um compartimento usando uma frase mnemônica"""
        # Verificar se está em modo restrito
        if hasattr(self, 'modo_acesso_restrito') and self.modo_acesso_restrito:
            show_error(self.janela, "Acesso Negado", "Você está em modo de acesso restrito.\nNão é possível acessar outros compartimentos.")
            return
        
        janela_frase = tk.Toplevel(self.janela)
        janela_frase.title("Acessar por Frase Mnemônica")
        janela_frase.geometry("600x300")
        janela_frase.grab_set()  # Torna a janela modal
        
        tk.Label(janela_frase, text="Acessar Compartimento por Frase Mnemônica", font=("Arial", 14)).pack(pady=10)
        
        tk.Label(janela_frase, text="Digite a frase mnemônica (12 palavras separadas por espaço):").pack(anchor=tk.W, padx=20, pady=(10, 0))
        
        texto_frase = tk.Text(janela_frase, width=50, height=3, font=("Courier", 12))
        texto_frase.pack(fill=tk.X, padx=20, pady=5)
        
        def confirmar_acesso():
            frase = texto_frase.get("1.0", tk.END).strip()
            
            if not frase:
                show_error(janela_frase, "Erro", "A frase mnemônica é obrigatória")
                return
            
            # Ativar compartimento
            sucesso, mensagem = self.cofre.ativar_compartimento_por_frase(frase)
            
            if sucesso:
                show_success(janela_frase, "Sucesso", mensagem)
                self.atualizar_interface()
                janela_frase.destroy()
            else:
                show_error(janela_frase, "Erro", mensagem)
        
        # Botões
        frame_botoes = tk.Frame(janela_frase)
        frame_botoes.pack(pady=15)
        
        tk.Button(frame_botoes, text="Acessar", command=confirmar_acesso).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botoes, text="Cancelar", command=janela_frase.destroy).pack(side=tk.LEFT, padx=10)

    def atualizar_interface(self):
        """Atualiza elementos da interface após mudanças"""
        # Atualizar label do compartimento ativo
        if hasattr(self, 'label_compartimento_ativo'):
            self.label_compartimento_ativo.config(text=self.cofre.compartimento_ativo)
        
        # Atualizar contadores
        self.atualizar_contadores()
        
        # Atualizar listas
        if hasattr(self, 'atualizar_lista_senhas'):
            self.atualizar_lista_senhas()
        if hasattr(self, 'atualizar_lista_notas'):
            self.atualizar_lista_notas()
        if hasattr(self, 'atualizar_lista_arquivos'):
            self.atualizar_lista_arquivos()

    def verificar_senha(self, senha):
        """Verifica a senha do usuário"""
        if not senha:
            show_error(self.janela, "Erro", "Digite sua senha")
            return
        
        sucesso, mensagem, modo_heranca = self.cofre.autenticar(senha)
        
        if sucesso:
            # Não atualizar a data da última confirmação automaticamente
            # Isso será feito apenas quando o usuário solicitar explicitamente
            self.mostrar_tela_principal(modo_restrito=False)
        else:
            show_error(self.janela, "Erro", mensagem)
            
            # Incrementar contador de tentativas
            self.tentativas += 1
            
            # Verificar se atingiu o limite de tentativas
            if self.tentativas >= self.cofre.max_tentativas:
                show_error(self.janela, "Acesso Bloqueado", "Número máximo de tentativas atingido. O aplicativo será fechado.")
                self.janela.quit()

    def atualizar_lista_notas(self):
        """Atualiza a lista de notas"""
        if not hasattr(self, 'lista_notas'):
            return
        
        # Limpar lista atual
        self.lista_notas.delete(0, tk.END)
        self.notas_ids = []
        
        # Obter notas do compartimento ativo
        sucesso, mensagem, notas = self.cofre.listar_notas()
        
        if not sucesso:
            messagebox.showerror("Erro", mensagem)
            return
        
        # Adicionar notas à lista
        for nota in notas:
            self.lista_notas.insert(tk.END, nota["titulo"])
            self.notas_ids.append(nota["id"])

    def _criar_janela_dialogo(self, titulo, tamanho="400x300"):
        """Cria uma janela de diálogo estilizada"""
        janela = tk.Toplevel(self.janela)
        janela.title(titulo)
        janela.geometry(tamanho)
        janela.configure(bg=DARK_BG)
        janela.grab_set()
        
        # Título
        tk.Label(
            janela,
            text=titulo,
            font=FONT_SUBTITLE,
            bg=DARK_BG,
            fg=TEXT_PRIMARY
        ).pack(pady=20)
        
        return janela

    def _criar_entrada_texto(self, parent, label, show=None):
        """Cria um campo de entrada estilizado"""
        frame = tk.Frame(parent, bg=DARK_BG)
        frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(
            frame,
            text=label,
            bg=DARK_BG,
            fg=TEXT_SECONDARY,
            font=FONT_REGULAR
        ).pack(anchor=tk.W)
        
        entrada = tk.Entry(
            frame,
            show=show,
            bg=CARD_BG,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief="flat",
            font=FONT_REGULAR
        )
        entrada.pack(fill=tk.X, pady=(5, 0))
        
        return entrada

    def renovar_periodo(self):
        """Renova o período de confirmação do usuário"""
        try:
            # Verificar se está em modo restrito
            if hasattr(self, 'modo_acesso_restrito') and self.modo_acesso_restrito:
                show_error(self.janela, "Acesso Negado", "Você está em modo de acesso restrito.\nNão é possível renovar o período.")
                return
                
            # Chamar o método do cofre para renovar o período
            sucesso, mensagem = self.cofre.renovar_periodo()
            
            if sucesso:
                show_success(self.janela, "Sucesso", mensagem)
                # Atualizar o timer na interface
                self.atualizar_timer()
            else:
                show_error(self.janela, "Erro", mensagem)
        except Exception as e:
            show_error(self.janela, "Erro", f"Erro ao renovar período: {str(e)}")

    def atualizar_timer(self):
        """Atualiza o timer na interface"""
        if hasattr(self, 'label_timer'):
            try:
                if hasattr(self, 'modo_acesso_restrito') and self.modo_acesso_restrito:
                    self.label_timer.config(text="ACESSO RESTRITO")
                    return  # Não continuar atualizando em modo restrito
                
                # Obter o tempo restante do cofre
                tempo_restante = self.cofre.obter_tempo_restante()
                
                # Converter para formato HH:MM:SS
                horas = tempo_restante // 3600
                minutos = (tempo_restante % 3600) // 60
                segundos = tempo_restante % 60
                
                # Atualizar o label com o tempo formatado
                tempo_formatado = f"{horas:03d}:{minutos:02d}:{segundos:02d}"
                self.label_timer.config(text=tempo_formatado)
                
                # Agendar próxima atualização em 1 segundo
                self.janela.after(1000, self.atualizar_timer)
                
            except Exception as e:
                print(f"Erro ao atualizar timer: {str(e)}")
                traceback.print_exc()

    def _aplicar_estilo_janela(self, janela, titulo):
        """Aplica o estilo padrão em uma janela"""
        janela.configure(bg=DARK_BG)
        
        # Título
        tk.Label(
            janela,
            text=titulo,
            font=FONT_SUBTITLE,
            bg=DARK_BG,
            fg=TEXT_PRIMARY,
            **LABEL_STYLE
        ).pack(pady=20)
        
        return janela

    def _criar_botao_padrao(self, parent, texto, comando, is_primary=True):
        """Cria um botão com estilo padrão"""
        frame = tk.Frame(parent, bg=DARK_BG)
        frame.pack(side=tk.LEFT, padx=5)
        
        cor_bg = BLUE_PRIMARY if is_primary else CARD_BG
        cor_fg = TEXT_PRIMARY
        cor_hover = BLUE_SECONDARY if is_primary else DARKER_BG
        
        btn = tk.Button(
            frame,
            text=texto,
            command=comando,
            bg=cor_bg,
            fg=cor_fg,
            activebackground=cor_hover,
            activeforeground=cor_fg,
            **BTN_STYLE
        )
        btn.pack()
        
        # Efeitos hover
        def on_enter(e):
            btn['background'] = cor_hover
        def on_leave(e):
            btn['background'] = cor_bg
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn

    def _criar_menu(self):
        """Cria o menu principal da aplicação"""
        menubar = tk.Menu(self.janela)
        self.janela.config(menu=menubar)
        
        # Menu Arquivo
        menu_arquivo = tk.Menu(menubar, tearoff=0, bg=DARK_BG, fg=TEXT_PRIMARY)
        menubar.add_cascade(label="Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Backup e Restauração", command=self.backup_restauracao)
        menu_arquivo.add_separator()
        menu_arquivo.add_command(label="Sair", command=self.sair)
        
        # Menu Configurações
        menu_config = tk.Menu(menubar, tearoff=0, bg=DARK_BG, fg=TEXT_PRIMARY)
        menubar.add_cascade(label="Configurações", menu=menu_config)
        menu_config.add_command(label="Configurações Gerais", command=self.alterar_configuracoes)
        menu_config.add_command(label="Reconfigurar Senhas", command=self.reconfigurar_senhas)

    @aplicar_estilo_padrao
    def mostrar_login_frase(self):
        """Mostra a tela de login com frase mnemônica"""
        janela_frase = tk.Toplevel(self.janela)
        janela_frase.title("Acessar com Frase Mnemônica")
        janela_frase.geometry("600x350")
        janela_frase.grab_set()  # Torna a janela modal
        janela_frase.configure(bg=DARK_BG)
        
        # Container com padding
        container = tk.Frame(janela_frase, bg=DARK_BG, padx=30, pady=30)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Título com ícone
        titulo_frame = tk.Frame(container, bg=DARK_BG)
        titulo_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Ícone
        tk.Label(
            titulo_frame,
            text="🔑",
            font=("Arial", 24),
            fg=BLUE_PRIMARY,
            bg=DARK_BG
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        # Título
        tk.Label(
            titulo_frame,
            text="Acesso com Frase Mnemônica",
            font=FONT_SUBTITLE,
            bg=DARK_BG,
            fg=TEXT_PRIMARY
        ).pack(side=tk.LEFT)
        
        # Instrução
        tk.Label(
            container,
            text="Digite a frase mnemônica (12 palavras separadas por espaço):",
            font=FONT_REGULAR,
            bg=DARK_BG,
            fg=TEXT_SECONDARY,
            anchor="w"
        ).pack(fill=tk.X, pady=(0, 10))
        
        # Campo de texto para a frase
        texto_frase = tk.Text(
            container,
            height=3,
            font=("Consolas", 14),
            bg=SURFACE_1,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            highlightcolor=BLUE_PRIMARY,
            padx=15,
            pady=15
        )
        texto_frase.pack(fill=tk.X, pady=(0, 20))
        texto_frase.focus_set()
        
        # Frame de botões
        btn_frame = tk.Frame(container, bg=DARK_BG)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Função para acessar
        def confirmar_acesso():
            frase = texto_frase.get("1.0", tk.END).strip()
            
            if not frase:
                show_error(janela_frase, "Erro", "A frase mnemônica é obrigatória")
                return
            
            try:
                # Autenticar com a frase
                sucesso, mensagem, modo_restrito = self.cofre.autenticar_por_frase(frase)
                
                if sucesso:
                    show_success(janela_frase, "Sucesso", mensagem)
                    janela_frase.destroy()
                    self.mostrar_tela_principal(modo_restrito=modo_restrito)
                else:
                    show_error(janela_frase, "Erro", mensagem)
            except Exception as e:
                traceback.print_exc()
                show_error(janela_frase, "Erro", f"Erro ao autenticar: {str(e)}")
        
        # Botão cancelar
        btn_cancelar = tk.Button(
            btn_frame, 
            text="Cancelar", 
            command=janela_frase.destroy,
            **BTN_SECONDARY_STYLE
        )
        btn_cancelar.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Botão acessar
        btn_acessar = tk.Button(
            btn_frame, 
            text="Acessar", 
            command=confirmar_acesso,
            **BTN_PRIMARY_STYLE
        )
        btn_acessar.pack(side=tk.RIGHT)
        
        # Vincular a tecla Enter
        texto_frase.bind("<Control-Return>", lambda event: confirmar_acesso())
        
        return janela_frase