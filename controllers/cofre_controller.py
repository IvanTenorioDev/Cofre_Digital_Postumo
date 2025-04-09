import os
import time
import threading
import datetime
import tkinter as tk

from models.cofre_model import CofreDigitalModel
from models.bip39_validator import BIP39Validator


class CofreController:
    """Controlador principal do aplicativo Cofre Digital Póstumo."""
    
    def __init__(self):
        """Inicializa o controlador."""
        self.model = CofreDigitalModel()
        self.view = None  # Será definido quando a view for conectada
        self.bip39 = BIP39Validator()
        
        # Estado da aplicação
        self.compartimento_atual = "principal"
        self.exportando_dados = False
        self.temporizadores = {}
        
        # Iniciar verificação automática de período
        self._iniciar_verificacao_automatica()
    
    def conectar_view(self, view):
        """Conecta a view ao controlador."""
        self.view = view
    
    def verificar_status_sistema(self):
        """Verifica o status do sistema e retorna informações para exibição."""
        # Verificar se existe usuário configurado
        return {
            "usuario_configurado": self._verificar_usuario_existe(),
            "modo_heranca": self.model.modo_heranca_ativo,
            "dias_restantes": self.model.dias_restantes_confirmacao(),
            "estatisticas": self.model.obter_estatisticas()
        }
    
    def iniciar_sistema(self):
        """Inicializa o sistema verificando o estado atual."""
        # Verificar se o usuário já está configurado
        usuario_configurado = self._verificar_usuario_existe()
        
        # Verificar modo de herança
        modo_heranca = self.model.verificar_modo_heranca()
        
        if usuario_configurado:
            # Mostrar tela de login
            if self.view:
                self.view.mostrar_tela_login(modo_heranca)
        else:
            # Mostrar tela de configuração inicial
            if self.view:
                self.view.mostrar_tela_configuracao_inicial()
    
    def _verificar_usuario_existe(self):
        """Verifica se existe um usuário configurado."""
        import sqlite3
        
        try:
            # Conexão com o banco de dados
            conn = sqlite3.connect(self.model.caminho_db)
            cursor = conn.cursor()
            
            # Verificar se existe pelo menos um usuário na tabela
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            count = cursor.fetchone()[0]
            
            conn.close()
            
            return count > 0
            
        except Exception as e:
            self.model.registrar_log("erro", f"Erro ao verificar usuário: {str(e)}")
            return False
    
    def _iniciar_verificacao_automatica(self):
        """Inicia verificação automática do período de confirmação."""
        def verificador():
            while True:
                try:
                    # Verificar se o modo de herança deve ser ativado
                    modo_heranca_anterior = self.model.modo_heranca_ativo
                    modo_heranca_atual = self.model.verificar_modo_heranca()
                    
                    # Se houve mudança no modo de herança e o usuário estiver autenticado
                    if modo_heranca_anterior != modo_heranca_atual and self.model.usuario_autenticado:
                        # Notificar a view sobre a mudança no modo de herança
                        if self.view:
                            if modo_heranca_atual:
                                self.view.atualizar_status_heranca(True, "Modo de herança ativado automaticamente.")
                            else:
                                self.view.atualizar_status_heranca(False, "Modo de herança desativado.")
                    
                    # Verificar dias restantes
                    dias_restantes = self.model.dias_restantes_confirmacao()
                    periodo_notificacao = self.model.config.get("periodo_notificacao", 15)
                    
                    # Notificar se estiver próximo do vencimento
                    if 0 < dias_restantes <= periodo_notificacao and self.model.usuario_autenticado:
                        if self.view:
                            self.view.notificar_periodo(dias_restantes)
                
                except Exception as e:
                    self.model.registrar_log("erro", f"Erro na verificação automática: {str(e)}")
                
                # Verificar a cada 1 hora
                time.sleep(3600)
        
        # Iniciar thread de verificação
        threading.Thread(target=verificador, daemon=True).start()
    
    # === Funções de autenticação e configuração ===
    
    def configurar_usuario(self, nome, senha, senha_heranca, email=None):
        """Configura o usuário principal do sistema."""
        # Validar os dados
        if not nome or len(nome.strip()) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres", None
        
        if not senha or len(senha) < 8:
            return False, "Senha principal deve ter pelo menos 8 caracteres", None
        
        if not senha_heranca or len(senha_heranca) < 8:
            return False, "Senha de herança deve ter pelo menos 8 caracteres", None
        
        if senha == senha_heranca:
            return False, "Senha principal e senha de herança não podem ser iguais", None
        
        # Chamar o modelo para configurar o usuário
        sucesso, mensagem, frase_mnemonica = self.model.configurar_usuario(nome, senha, senha_heranca, email)
        
        # Se for bem-sucedido, redirecionar para a tela de login
        if sucesso and self.view:
            self.view.mostrar_frase_recuperacao(frase_mnemonica)
        
        return sucesso, mensagem, frase_mnemonica
    
    def autenticar(self, senha):
        """Autentica o usuário no sistema."""
        # Chamar o modelo para autenticar
        sucesso, mensagem, modo_heranca = self.model.autenticar(senha)
        
        # Se autenticado com sucesso, redirecionar para o dashboard
        if sucesso and self.view:
            self.view.mostrar_dashboard(modo_heranca)
        
        return sucesso, mensagem, modo_heranca
    
    def autenticar_por_frase(self, frase):
        """Autentica o usuário usando a frase mnemônica."""
        # Chamar o modelo para autenticar
        sucesso, mensagem, modo_heranca = self.model.autenticar_por_frase(frase)
        
        # Se autenticado com sucesso, redirecionar para o dashboard
        if sucesso and self.view:
            self.view.mostrar_dashboard(modo_heranca)
        
        return sucesso, mensagem, modo_heranca
    
    def renovar_periodo(self):
        """Renova o período de confirmação de vida."""
        if not self.model.usuario_autenticado:
            return False, "Usuário não autenticado"
        
        # Chamar o modelo para renovar o período
        sucesso, mensagem = self.model.renovar_periodo()
        
        # Atualizar a view, se necessário
        if sucesso and self.view:
            self.view.atualizar_status_heranca(False, "Período renovado com sucesso.")
        
        return sucesso, mensagem
    
    def logout(self):
        """Encerra a sessão atual."""
        # Limpar dados da sessão
        self.model.usuario_autenticado = False
        self.model.usuario_atual = None
        self.model.modo_heranca_ativo = False
        self.model.chave_compartimento_ativo = None
        self.compartimento_atual = "principal"
        
        # Cancelar todos os temporizadores
        for timer_id in list(self.temporizadores.keys()):
            self.cancelar_temporizador(timer_id)
        
        # Redirecionar para a tela de login
        if self.view:
            self.view.mostrar_tela_login(self.model.verificar_modo_heranca())
        
        return True, "Sessão encerrada com sucesso"
    
    # === Funções de gerenciamento de compartimentos ===
    
    def criar_compartimento(self, nome, senha, descricao=None):
        """Cria um novo compartimento seguro."""
        if not self.model.usuario_autenticado:
            return False, "Usuário não autenticado", None
        
        # Validar os dados
        if not nome or len(nome.strip()) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres", None
        
        if not senha or len(senha) < 6:
            return False, "Senha deve ter pelo menos 6 caracteres", None
        
        # Chamar o modelo para criar o compartimento
        sucesso, mensagem, frase_recuperacao = self.model.criar_compartimento(nome, senha, descricao)
        
        # Atualizar a view, se necessário
        if sucesso and self.view and frase_recuperacao:
            self.view.mostrar_frase_compartimento(nome, frase_recuperacao)
        
        return sucesso, mensagem, frase_recuperacao
    
    def listar_compartimentos(self):
        """Lista os compartimentos disponíveis."""
        if not self.model.usuario_autenticado:
            return False, "Usuário não autenticado", None
        
        # Chamar o modelo para listar os compartimentos
        return self.model.listar_compartimentos()
    
    def alternar_compartimento(self, compartimento_id, senha):
        """Alterna para um compartimento específico."""
        if not self.model.usuario_autenticado:
            return False, "Usuário não autenticado"
        
        # Chamar o modelo para alternar o compartimento
        sucesso, mensagem = self.model.alternar_compartimento(compartimento_id, senha)
        
        # Atualizar status do controlador
        if sucesso:
            self.compartimento_atual = compartimento_id
            
            # Atualizar a view, se necessário
            if self.view:
                self.view.atualizar_compartimento_ativo(compartimento_id)
        
        return sucesso, mensagem
    
    # === Funções de gerenciamento de BIP39 ===
    
    def validar_frase_bip39(self, frase):
        """Valida uma frase mnemônica BIP39."""
        return self.bip39.validar_frase(frase)
    
    def gerar_frase_bip39(self, comprimento=12):
        """Gera uma nova frase mnemônica BIP39."""
        return self.bip39.gerar_frase(comprimento)
    
    # === Funções de utilidade ===
    
    def definir_temporizador(self, funcao, segundos, *args, **kwargs):
        """Define um temporizador para executar uma função após certo tempo."""
        timer_id = os.urandom(8).hex()
        
        def funcao_temporizada():
            try:
                funcao(*args, **kwargs)
            finally:
                # Remover o temporizador da lista quando concluído
                if timer_id in self.temporizadores:
                    del self.temporizadores[timer_id]
        
        # Criar o temporizador
        timer = threading.Timer(segundos, funcao_temporizada)
        timer.daemon = True
        
        # Armazenar o temporizador
        self.temporizadores[timer_id] = timer
        
        # Iniciar o temporizador
        timer.start()
        
        return timer_id
    
    def cancelar_temporizador(self, timer_id):
        """Cancela um temporizador específico."""
        if timer_id in self.temporizadores:
            timer = self.temporizadores[timer_id]
            timer.cancel()
            del self.temporizadores[timer_id]
            return True
        
        return False
    
    # === Funções de gestão de configurações ===
    
    def obter_configuracoes(self):
        """Obtém as configurações atuais do sistema."""
        return self.model.config
    
    def salvar_configuracoes(self, novas_configuracoes):
        """Salva as configurações do sistema."""
        if not self.model.usuario_autenticado:
            return False, "Usuário não autenticado"
        
        if self.model.modo_heranca_ativo:
            return False, "Não é possível alterar configurações no modo de herança"
        
        # Atualizar configurações
        for chave, valor in novas_configuracoes.items():
            self.model.config[chave] = valor
        
        # Salvar configurações
        return self.model.salvar_configuracoes()
    
    def obter_intervalo_confirmacao(self):
        """Obtém o intervalo atual de confirmação de vida."""
        return self.model.config.get("intervalo_confirmacao", 90)
    
    def alterar_intervalo_confirmacao(self, dias):
        """Altera o intervalo de confirmação de vida."""
        if not self.model.usuario_autenticado:
            return False, "Usuário não autenticado"
        
        if self.model.modo_heranca_ativo:
            return False, "Não é possível alterar configurações no modo de herança"
        
        # Validar o valor
        try:
            dias = int(dias)
            if dias < 30:
                return False, "O intervalo mínimo é de 30 dias"
            if dias > 365:
                return False, "O intervalo máximo é de 365 dias"
        except:
            return False, "Valor inválido para o intervalo"
        
        # Atualizar configuração
        self.model.config["intervalo_confirmacao"] = dias
        
        # Salvar configurações
        return self.model.salvar_configuracoes()
    
    def verificar_importancia_renovacao(self):
        """Verifica a importância de renovar o período com base nos dias restantes."""
        dias_restantes = self.model.dias_restantes_confirmacao()
        periodo_notificacao = self.model.config.get("periodo_notificacao", 15)
        
        if dias_restantes <= 0:
            return "critico", "O período expirou. O modo de herança está ativo."
        elif dias_restantes <= 3:
            return "urgente", f"Restam apenas {dias_restantes} dias para renovar o período!"
        elif dias_restantes <= periodo_notificacao:
            return "aviso", f"Restam {dias_restantes} dias para renovar o período."
        else:
            return "normal", f"Período válido. Restam {dias_restantes} dias." 