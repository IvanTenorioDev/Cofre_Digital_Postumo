import os
import sys
import time
import json
import sqlite3
import hashlib
import secrets
import datetime
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import threading
import base64
import hmac
import traceback

# Importar módulos do projeto
from criptografia import Criptografia
from banco_dados import BancoDados
from interface import InterfaceGrafica

# Adicionar suporte para BIP39 (frases mnemônicas)
try:
    from mnemonic import Mnemonic
    BIP39_DISPONIVEL = True
except ImportError:
    BIP39_DISPONIVEL = False
    print("Biblioteca mnemonic não encontrada. Suporte a frases mnemônicas desativado.")
    print("Para instalar: pip install mnemonic")

class CofreDigital:
    def __init__(self):
        """Inicializa o cofre digital"""
        # Definir caminhos
        self.caminho_base = os.path.dirname(os.path.abspath(__file__))
        self.caminho_db = os.path.join(self.caminho_base, "dados", "cofre.db")
        self.caminho_config = os.path.join(self.caminho_base, "dados", "config.json")
        
        # Criar diretórios necessários
        os.makedirs(os.path.join(self.caminho_base, "dados"), exist_ok=True)
        os.makedirs(os.path.join(self.caminho_base, "arquivos"), exist_ok=True)
        os.makedirs(os.path.join(self.caminho_base, "backup"), exist_ok=True)
        
        # Inicializar componentes
        self.criptografia = Criptografia()
        self.banco_dados = BancoDados(self.caminho_db)
        
        # Criar estrutura do banco de dados
        self.banco_dados.criar_estrutura()
        
        # Atualizar estrutura do banco de dados (adicionar novas colunas)
        self.banco_dados.atualizar_estrutura()
        
        # Carregar configurações
        self.carregar_configuracoes()
        
        # Estado da aplicação
        self.usuario_autenticado = False
        self.tentativas_senha = 0
        self.modo_heranca_ativo = self.verificar_modo_heranca()
        
        # Compartimento ativo (padrão: compartimento principal)
        self.compartimento_ativo = "principal"
        self.chave_compartimento_ativo = None
    
    def inicializar_sistema(self):
        """Inicializa o banco de dados e as configurações do sistema"""
        # Verificar se o banco de dados existe, caso contrário, criar
        if not os.path.exists(self.caminho_db):
            self.banco_dados.criar_estrutura()
            
        # Verificar se o arquivo de configuração existe, caso contrário, criar
        if not os.path.exists(self.caminho_config):
            self.criar_configuracao_padrao()
            
        # Verificar se é necessário ativar o modo de herança
        self.verificar_modo_heranca()
    
    def criar_configuracao_padrao(self):
        """Cria o arquivo de configuração padrão"""
        config = {
            "intervalo_confirmacao": 30,  # dias
            "ultima_confirmacao": datetime.datetime.now().isoformat(),
            "max_tentativas_senha": 5,
            "modo_camuflagem": "bloco_notas",
            "autodestruicao_ativada": True,
            "nome_exibicao": "Bloco de Notas Portátil"
        }
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(self.caminho_config), exist_ok=True)
        
        with open(self.caminho_config, 'w') as f:
            json.dump(config, f, indent=4)
        
        self.banco_dados.registrar_log("sistema", "Configuração padrão criada")
        return True
    
    def verificar_modo_heranca(self):
        """Verifica se o modo de herança deve ser ativado"""
        try:
            # Carregar configurações
            with open(self.caminho_config, 'r') as f:
                config = json.load(f)
            
            # Obter data da última confirmação
            ultima_confirmacao_str = config.get("ultima_confirmacao")
            
            if not ultima_confirmacao_str:
                return False
            
            # Converter string para objeto datetime
            ultima_confirmacao = datetime.datetime.fromisoformat(ultima_confirmacao_str)
            
            # Calcular diferença de tempo
            agora = datetime.datetime.now()
            diferenca = agora - ultima_confirmacao
            
            # Verificar se passou o intervalo de confirmação
            intervalo_dias = config.get("intervalo_confirmacao", 30)
            
            if diferenca.days >= intervalo_dias:
                # Ativar modo de herança
                self.modo_heranca_ativo = True
                self.banco_dados.registrar_log("sistema", "Modo de herança ativado")
                return True
            else:
                # Modo normal
                self.modo_heranca_ativo = False
                return False
        except Exception as e:
            print(f"Erro ao verificar modo de herança: {str(e)}")
            return False
    
    def configurar_usuario(self, nome, senha, senha_heranca):
        """Configura o usuário principal do sistema"""
        try:
            # Verificar se já existe um usuário
            if self.banco_dados.verificar_usuario_existente():
                return False, "Já existe um usuário configurado"
            
            # Criar hash da senha principal
            hash_senha, salt = self.criptografia.hash_senha(senha)
            
            # Criar hash da senha de herança
            hash_senha_heranca, salt_heranca = self.criptografia.hash_senha(senha_heranca)
            
            # Gerar frase mnemônica para backup (se BIP39 estiver disponível)
            frase_mnemonica = None
            seed_hex = None
            
            if BIP39_DISPONIVEL:
                try:
                    # Gerar entropia aleatória (128 bits = 16 bytes = frase de 12 palavras)
                    entropia = secrets.token_bytes(16)
                    mnemo = Mnemonic("english")
                    
                    # Gerar frase mnemônica
                    frase_mnemonica = mnemo.to_mnemonic(entropia)
                    
                    # Gerar seed a partir da frase (com senha vazia como passphrase)
                    seed = mnemo.to_seed(frase_mnemonica, "")
                    seed_hex = seed.hex()
                    
                    # Registrar log
                    self.banco_dados.registrar_log("sistema", "Frase mnemônica gerada com sucesso")
                except Exception as e:
                    self.banco_dados.registrar_log("erro", f"Erro ao gerar frase mnemônica: {str(e)}")
            
            # Inserir usuário
            sucesso = self.banco_dados.criar_usuario(nome, hash_senha, salt, hash_senha_heranca, salt_heranca, seed_hex)
            
            if sucesso:
                self.banco_dados.registrar_log("sistema", f"Usuário {nome} configurado com sucesso")
                
                # Retornar a frase mnemônica para exibição ao usuário
                if frase_mnemonica:
                    return True, "Usuário configurado com sucesso", frase_mnemonica
                else:
                    return True, "Usuário configurado com sucesso", None
            else:
                return False, "Erro ao configurar usuário", None
        except Exception as e:
            self.banco_dados.registrar_log("erro", f"Erro ao configurar usuário: {str(e)}")
            return False, f"Erro ao configurar usuário: {str(e)}", None
    
    def autenticar(self, senha):
        """Autentica o usuário no sistema"""
        try:
            # Obter dados do usuário
            usuario = self.banco_dados.obter_usuario()
            
            if not usuario:
                self.tentativas_senha += 1
                self.banco_dados.registrar_log("autenticacao", "Tentativa de autenticação falhou: usuário não encontrado")
                return False, "Usuário não encontrado", False
            
            # Desempacotar com tratamento para o caso de seed_hex estar disponível
            if len(usuario) == 6:
                id_usuario, hash_senha_armazenado, salt, hash_senha_heranca, salt_heranca, seed_hex = usuario
            else:
                id_usuario, hash_senha_armazenado, salt, hash_senha_heranca, salt_heranca = usuario
            
            # Verificar senha principal
            hash_senha_fornecida, _ = self.criptografia.hash_senha(senha, salt)
            
            if hash_senha_fornecida == hash_senha_armazenado:
                # Senha principal correta
                if not self.modo_heranca_ativo:
                    # Modo normal - NÃO atualizar última confirmação automaticamente
                    self.usuario_autenticado = True
                    self.tentativas_senha = 0
                    self.banco_dados.registrar_log("autenticacao", f"Usuário ID {id_usuario} autenticado com sucesso")
                    return True, "Autenticação bem-sucedida", False
                else:
                    # Modo herança ativo, mas tentou usar senha principal
                    self.tentativas_senha += 1
                    self.banco_dados.registrar_log("autenticacao", "Tentativa de usar senha principal no modo recuperação")
                    return False, "Modo de recuperação ativo. Use a senha de recuperação.", False
            
            # Verificar senha de herança
            hash_senha_heranca_fornecida, _ = self.criptografia.hash_senha(senha, salt_heranca)
            
            if hash_senha_heranca_fornecida == hash_senha_heranca:
                # Senha de herança correta
                if self.modo_heranca_ativo:
                    # Modo herança ativo - permitir acesso
                    self.usuario_autenticado = True
                    self.tentativas_senha = 0
                    self.banco_dados.registrar_log("autenticacao", f"Acesso de herança concedido para usuário ID {id_usuario}")
                    return True, "Acesso de herança concedido", True
                else:
                    # Modo herança não ativo - negar acesso
                    self.tentativas_senha += 1
                    self.banco_dados.registrar_log("autenticacao", "Tentativa de usar senha de herança fora do modo herança")
                    return False, "Senha de herança só pode ser usada após o período de inatividade", False
            
            # Ambas as senhas estão incorretas
            self.tentativas_senha += 1
            self.banco_dados.registrar_log("autenticacao", f"Tentativa de autenticação falhou para usuário ID {id_usuario}")
            
            # Verificar se deve autodestruir
            if self.tentativas_senha >= self.max_tentativas:
                with open(self.caminho_config, 'r') as f:
                    config = json.load(f)
                
                if config.get("autodestruicao_ativada", True):
                    self.autodestruir()
                    return False, "Número máximo de tentativas excedido. Dados apagados.", False
            
            return False, f"Senha incorreta. Tentativas restantes: {self.max_tentativas - self.tentativas_senha}", False
        
        except Exception as e:
            self.banco_dados.registrar_log("erro", f"Erro durante autenticação: {str(e)}")
            return False, f"Erro durante autenticação: {str(e)}", False
    
    def autodestruir(self):
        """Apaga todos os dados criptografados do sistema"""
        try:
            self.banco_dados.registrar_log("sistema", "Iniciando autodestruição dos dados")
            
            # Apagar senhas e notas
            self.banco_dados.apagar_dados_sensiveis()
            
            # Obter lista de arquivos criptografados
            arquivos = self.banco_dados.obter_arquivos_para_exclusao()
            
            # Apagar arquivos físicos
            for arquivo in arquivos:
                caminho_arquivo = os.path.join(self.caminho_base, "arquivos", arquivo)
                if os.path.exists(caminho_arquivo):
                    os.remove(caminho_arquivo)
            
            self.banco_dados.registrar_log("sistema", "Autodestruição concluída")
            return True, "Dados apagados com sucesso"
        except Exception as e:
            self.banco_dados.registrar_log("erro", f"Erro durante autodestruição: {str(e)}")
            return False, f"Erro durante autodestruição: {str(e)}"

    def adicionar_senha(self, titulo, senha, descricao=None, categoria_id=None):
        """Adiciona uma nova senha ao cofre no compartimento ativo"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado"
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Usar a chave do compartimento ativo para criptografia
            chave_criptografia = self.chave_compartimento_ativo
            
            # Se não houver chave de compartimento ativa, usar a chave derivada da senha do usuário
            if chave_criptografia is None:
                # Obter dados do usuário
                cursor.execute("SELECT hash_senha FROM usuarios LIMIT 1")
                resultado_usuario = cursor.fetchone()
                
                if not resultado_usuario:
                    conn.close()
                    return False, "Usuário não encontrado"
                
                hash_senha_usuario = resultado_usuario[0]
                
                # Usar o hash da senha do usuário como base para a chave de criptografia
                chave_criptografia = hash_senha_usuario[:32].encode()
            
            # Criptografar a senha
            senha_criptografada, iv = self.criptografia.criptografar(senha, chave_criptografia)
            
            # Salvar no banco de dados
            data_atual = datetime.datetime.now().isoformat()
            
            cursor.execute(
                "INSERT INTO senhas (titulo, descricao, dados_criptografados, iv, data_criacao, data_modificacao, categoria_id, compartimento) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (titulo, descricao, senha_criptografada, iv, data_atual, data_atual, categoria_id, self.compartimento_ativo)
            )
            
            conn.commit()
            conn.close()
            
            try:
                self.banco_dados.registrar_log("dados", f"Nova senha adicionada: {titulo} (compartimento: {self.compartimento_ativo})")
            except:
                pass
            return True, "Senha adicionada com sucesso"
        except Exception as e:
            try:
                self.banco_dados.registrar_log("erro", f"Erro ao adicionar senha: {str(e)}")
            except:
                pass
            return False, f"Erro ao adicionar senha: {str(e)}"

    def obter_senhas(self):
        """Obtém todas as senhas do compartimento ativo"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado", None
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Obter apenas as senhas do compartimento ativo
            cursor.execute(
                "SELECT id, titulo, descricao, data_criacao, data_modificacao, categoria_id FROM senhas WHERE compartimento = ? ORDER BY titulo",
                (self.compartimento_ativo,)
            )
            resultados = cursor.fetchall()
            
            conn.close()
            
            senhas = []
            for id_senha, titulo, descricao, data_criacao, data_modificacao, categoria_id in resultados:
                senhas.append({
                    "id": id_senha,
                    "titulo": titulo,
                    "descricao": descricao,
                    "data_criacao": data_criacao,
                    "data_modificacao": data_modificacao,
                    "categoria_id": categoria_id
                })
            
            return True, f"Encontradas {len(senhas)} senhas no compartimento {self.compartimento_ativo}", senhas
        except Exception as e:
            try:
                self.banco_dados.registrar_log("erro", f"Erro ao obter senhas: {str(e)}")
            except:
                pass
            return False, f"Erro ao obter senhas: {str(e)}", None

    def obter_senha(self, id_senha):
        """Obtém uma senha específica pelo ID do compartimento ativo"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado", None
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Verificar se a senha pertence ao compartimento ativo
            cursor.execute(
                "SELECT id, titulo, dados_criptografados, iv, descricao, data_criacao, data_modificacao, categoria_id FROM senhas WHERE id = ? AND compartimento = ?",
                (id_senha, self.compartimento_ativo)
            )
            resultado = cursor.fetchone()
            
            if not resultado:
                conn.close()
                return False, "Senha não encontrada no compartimento ativo", None
            
            id_senha, titulo, senha_criptografada, iv, descricao, data_criacao, data_modificacao, categoria_id = resultado
            
            # Usar a chave do compartimento ativo para descriptografia
            chave_descriptografia = self.chave_compartimento_ativo
            
            # Se não houver chave de compartimento ativa, usar a chave derivada da senha do usuário
            if chave_descriptografia is None:
                # Obter dados do usuário
                cursor.execute("SELECT hash_senha FROM usuarios LIMIT 1")
                resultado_usuario = cursor.fetchone()
                
                if not resultado_usuario:
                    conn.close()
                    return False, "Usuário não encontrado", None
                
                hash_senha_usuario = resultado_usuario[0]
                
                # Usar o hash da senha do usuário como base para a chave de descriptografia
                chave_descriptografia = hash_senha_usuario[:32].encode()
            
            # Descriptografar a senha
            senha = self.criptografia.descriptografar(senha_criptografada, iv, chave_descriptografia).decode()
            
            conn.close()
            
            return True, "Senha obtida com sucesso", {
                "id": id_senha,
                "titulo": titulo,
                "senha": senha,
                "descricao": descricao,
                "data_criacao": data_criacao,
                "data_modificacao": data_modificacao,
                "categoria_id": categoria_id
            }
        except Exception as e:
            try:
                self.banco_dados.registrar_log("erro", f"Erro ao obter senha: {str(e)}")
            except:
                pass
            return False, f"Erro ao obter senha: {str(e)}", None

    def obter_notas(self):
        """Obtém todas as notas armazenadas"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado", None
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Verificar quais colunas existem na tabela notas
            cursor.execute("PRAGMA table_info(notas)")
            colunas = [info[1] for info in cursor.fetchall()]
            
            # Adaptar a query de acordo com as colunas existentes
            if 'conteudo_criptografado' in colunas:
                cursor.execute(
                    "SELECT id, titulo, data_criacao, data_modificacao FROM notas ORDER BY titulo"
                )
            elif 'dados_criptografados' in colunas:
                cursor.execute(
                    "SELECT id, titulo, data_criacao, data_modificacao FROM notas ORDER BY titulo"
                )
            else:
                conn.close()
                return False, "Estrutura da tabela notas inválida", None
            
            resultados = cursor.fetchall()
            
            conn.close()
            
            notas = []
            for id_nota, titulo, data_criacao, data_modificacao in resultados:
                notas.append({
                    "id": id_nota,
                    "titulo": titulo,
                    "data_criacao": data_criacao,
                    "data_modificacao": data_modificacao
                })
            
            return True, f"Encontradas {len(notas)} notas", notas
        except Exception as e:
            try:
                self.banco_dados.registrar_log("erro", f"Erro ao obter notas: {str(e)}")
            except:
                pass
            return False, f"Erro ao obter notas: {str(e)}", None

    def obter_nota(self, id_nota):
        """Obtém o conteúdo de uma nota específica"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado", None
        
        try:
            # Obter dados da nota
            nota = self.banco_dados.obter_nota_por_id(id_nota)
            
            if not nota:
                return False, "Nota não encontrada", None
            
            # Verificar se a nota pertence ao compartimento ativo
            if nota["compartimento"] != self.compartimento_ativo:
                self.banco_dados.registrar_log("seguranca", f"Tentativa de acessar nota de outro compartimento: {nota['compartimento']}")
                return False, "Esta nota não pertence ao compartimento ativo", None
            
            # Descriptografar o conteúdo
            conteudo_criptografado = nota["conteudo_criptografado"]
            iv = nota["iv"]
            
            # Usar a chave do compartimento ativo
            chave_criptografia = self.chave_compartimento_ativo
            
            # Se não houver chave de compartimento ativa, usar a chave derivada da senha do usuário
            if chave_criptografia is None:
                # Obter dados do usuário
                usuario = self.banco_dados.obter_usuario()
                
                if not usuario:
                    return False, "Usuário não encontrado", None
                
                # Desempacotar com tratamento para o caso de seed_hex estar disponível
                if len(usuario) == 6:
                    id_usuario, hash_senha, salt, hash_senha_heranca, salt_heranca, seed_hex = usuario
                else:
                    id_usuario, hash_senha, salt, hash_senha_heranca, salt_heranca = usuario
                
                # Usar o hash da senha do usuário como base para a chave de criptografia
                chave_criptografia = hash_senha[:32].encode()
            
            try:
                # Descriptografar o conteúdo
                conteudo = self.criptografia.descriptografar(conteudo_criptografado, iv, chave_criptografia)
                return True, "Nota obtida com sucesso", conteudo
            except Exception as e:
                self.banco_dados.registrar_log("erro", f"Erro ao descriptografar nota: {str(e)}")
                return False, f"Erro ao descriptografar nota: {str(e)}", None
        except Exception as e:
            self.banco_dados.registrar_log("erro", f"Erro ao obter nota: {str(e)}")
            return False, f"Erro ao obter nota: {str(e)}", None

    def obter_arquivos(self):
        """Obtém a lista de arquivos armazenados"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado", None
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Obter todos os arquivos
            cursor.execute(
                "SELECT id, nome_original, descricao, data_upload FROM arquivos ORDER BY nome_original"
            )
            resultados = cursor.fetchall()
            
            conn.close()
            
            arquivos = []
            for id_arquivo, nome_original, descricao, data_upload in resultados:
                arquivos.append({
                    "id": id_arquivo,
                    "nome_original": nome_original,
                    "descricao": descricao if descricao else "",
                    "data_upload": data_upload
                })
            
            return True, f"Encontrados {len(arquivos)} arquivos", arquivos
        except Exception as e:
            try:
                self.banco_dados.registrar_log("erro", f"Erro ao obter arquivos: {str(e)}")
            except:
                pass
            return False, f"Erro ao obter arquivos: {str(e)}", None

    def adicionar_nota(self, titulo, conteudo, categoria_id=None):
        """Adiciona uma nova nota ao cofre no compartimento ativo"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado"
        
        try:
            # Usar a chave do compartimento ativo para criptografia
            chave_criptografia = self.chave_compartimento_ativo
            
            # Se não houver chave de compartimento ativa, usar a chave derivada da senha do usuário
            if chave_criptografia is None:
                # Obter dados do usuário
                usuario = self.banco_dados.obter_usuario()
                
                if not usuario:
                    return False, "Usuário não encontrado"
                
                id_usuario, hash_senha, salt, hash_senha_heranca, salt_heranca, seed_hex = usuario
                
                # Usar o hash da senha do usuário como base para a chave de criptografia
                chave_criptografia = hash_senha[:32].encode()
            
            # Criptografar o conteúdo da nota
            conteudo_criptografado, iv = self.criptografia.criptografar(conteudo, chave_criptografia)
            
            # Obter data atual
            data_atual = datetime.datetime.now().isoformat()
            
            # Inserir nota no banco de dados
            sucesso = self.banco_dados.adicionar_nota(
                titulo, 
                conteudo_criptografado, 
                iv, 
                data_atual, 
                data_atual, 
                categoria_id,
                self.compartimento_ativo  # Adicionar o compartimento ativo
            )
            
            if sucesso:
                self.banco_dados.registrar_log("nota", f"Nota '{titulo}' adicionada ao compartimento '{self.compartimento_ativo}'")
                return True, "Nota adicionada com sucesso"
            else:
                return False, "Erro ao adicionar nota"
        except Exception as e:
            self.banco_dados.registrar_log("erro", f"Erro ao adicionar nota: {str(e)}")
            return False, f"Erro ao adicionar nota: {str(e)}"

    def adicionar_arquivo(self, caminho_arquivo, descricao=""):
        """Adiciona um novo arquivo ao cofre"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado"
        
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(caminho_arquivo):
                return False, "Arquivo não encontrado"
            
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Obter ID do usuário diretamente
            cursor.execute("SELECT id FROM usuarios LIMIT 1")
            resultado_usuario = cursor.fetchone()
            
            if not resultado_usuario:
                conn.close()
                return False, "Usuário não encontrado"
            
            id_usuario = resultado_usuario[0]
            
            # Derivar chave de criptografia
            chave, _ = self.criptografia.gerar_chave_derivada(str(id_usuario))
            
            # Ler o arquivo
            with open(caminho_arquivo, 'rb') as f:
                conteudo = f.read()
            
            # Criptografar o conteúdo
            dados_criptografados, iv = self.criptografia.criptografar(conteudo, chave)
            
            # Gerar nome único para o arquivo criptografado
            nome_original = os.path.basename(caminho_arquivo)
            nome_criptografado = f"{secrets.token_hex(8)}_{nome_original}"
            
            # Salvar o arquivo criptografado
            caminho_destino = os.path.join(self.caminho_base, "arquivos", nome_criptografado)
            with open(caminho_destino, 'wb') as f:
                f.write(base64.b64decode(dados_criptografados))
            
            # Salvar no banco de dados
            data_atual = datetime.datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO arquivos (nome_original, nome_criptografado, descricao, iv, data_upload) VALUES (?, ?, ?, ?, ?)",
                (nome_original, nome_criptografado, descricao, iv, data_atual)
            )
            
            conn.commit()
            conn.close()
            
            self.banco_dados.registrar_log("dados", f"Novo arquivo adicionado: {nome_original}")
            return True, "Arquivo adicionado com sucesso"
        except Exception as e:
            self.banco_dados.registrar_log("erro", f"Erro ao adicionar arquivo: {str(e)}")
            return False, f"Erro ao adicionar arquivo: {str(e)}"

    def extrair_arquivo(self, id_arquivo, caminho_destino):
        """Extrai um arquivo específico para o destino especificado (versão simplificada para teste)"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado"
        
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Obter informações do arquivo
            cursor.execute("SELECT nome_original, nome_criptografado FROM arquivos WHERE id = ?", (id_arquivo,))
            resultado = cursor.fetchone()
            
            if not resultado:
                conn.close()
                return False, "Arquivo não encontrado"
            
            nome_original = resultado[0]
            conn.close()
            
            # Para teste, vamos apenas copiar um arquivo de exemplo
            # Em uma implementação real, este seria o conteúdo descriptografado do arquivo original.
            caminho_saida = os.path.join(caminho_destino, nome_original)
            
            with open(caminho_saida, 'w') as f:
                f.write("Este é um arquivo de teste extraído do cofre digital.\n")
                f.write("Em uma implementação real, este seria o conteúdo descriptografado do arquivo original.")
            
            try:
                self.banco_dados.registrar_log("acesso", f"Arquivo extraído: {nome_original}")
            except:
                pass
            
            return True, f"Arquivo extraído para {caminho_saida}"
        except Exception as e:
            try:
                self.banco_dados.registrar_log("erro", f"Erro ao extrair arquivo: {str(e)}")
            except:
                pass
            return False, f"Erro ao extrair arquivo: {str(e)}"

    def reconfigurar_senhas(self, senha_atual, nova_senha, nova_senha_heranca):
        """Reconfigura as senhas do usuário e recriptografa todos os dados"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado"
        
        try:
            # Obter dados do usuário
            usuario = self.banco_dados.obter_usuario()
            
            if not usuario:
                return False, "Usuário não encontrado"
            
            id_usuario, hash_senha_armazenado, salt, _, _ = usuario
            
            # Verificar senha atual
            hash_senha_fornecida, _ = self.criptografia.hash_senha(senha_atual, salt)
            
            if hash_senha_fornecida != hash_senha_armazenado:
                return False, "Senha atual incorreta"
            
            # Obter a chave antiga para descriptografar os dados existentes
            chave_antiga = hash_senha_armazenado[:32].encode()
            
            # Criar hash da nova senha principal
            hash_nova_senha, novo_salt = self.criptografia.hash_senha(nova_senha)
            
            # Criar hash da nova senha de herança
            hash_nova_senha_heranca, novo_salt_heranca = self.criptografia.hash_senha(nova_senha_heranca)
            
            # Obter a nova chave para recriptografar os dados
            chave_nova = hash_nova_senha[:32].encode()
            
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Recriptografar senhas
            cursor.execute("SELECT id, titulo, descricao, dados_criptografados, iv FROM senhas")
            senhas = cursor.fetchall()
            
            for id_senha, titulo, descricao, dados_criptografados, iv in senhas:
                try:
                    # Descriptografar com a chave antiga
                    senha_bytes = self.criptografia.descriptografar(dados_criptografados, iv, chave_antiga)
                    senha = senha_bytes.decode('utf-8')
                    
                    # Recriptografar com a nova chave
                    novos_dados_criptografados, novo_iv = self.criptografia.criptografar(senha, chave_nova)
                    
                    # Atualizar no banco de dados
                    cursor.execute(
                        "UPDATE senhas SET dados_criptografados = ?, iv = ? WHERE id = ?",
                        (novos_dados_criptografados, novo_iv, id_senha)
                    )
                except Exception as e:
                    print(f"Erro ao recriptografar senha {id_senha}: {str(e)}")
                    # Continuar com as outras senhas mesmo se houver erro
            
            # Recriptografar notas
            cursor.execute("SELECT id, titulo, dados_criptografados, iv FROM notas")
            notas = cursor.fetchall()
            
            for id_nota, titulo, dados_criptografados, iv in notas:
                try:
                    # Descriptografar com a chave antiga
                    conteudo_bytes = self.criptografia.descriptografar(dados_criptografados, iv, chave_antiga)
                    conteudo = conteudo_bytes.decode('utf-8')
                    
                    # Recriptografar com a nova chave
                    novos_dados_criptografados, novo_iv = self.criptografia.criptografar(conteudo, chave_nova)
                    
                    # Atualizar no banco de dados
                    cursor.execute(
                        "UPDATE notas SET dados_criptografados = ?, iv = ? WHERE id = ?",
                        (novos_dados_criptografados, novo_iv, id_nota)
                    )
                except Exception as e:
                    print(f"Erro ao recriptografar nota {id_nota}: {str(e)}")
                    # Continuar com as outras notas mesmo se houver erro
            
            # Atualizar senhas do usuário
            cursor.execute(
                "UPDATE usuarios SET hash_senha = ?, salt = ?, hash_senha_heranca = ?, salt_heranca = ? WHERE id = ?",
                (hash_nova_senha, novo_salt, hash_nova_senha_heranca, novo_salt_heranca, id_usuario)
            )
            
            conn.commit()
            conn.close()
            
            try:
                self.banco_dados.registrar_log("sistema", "Senhas reconfiguradas e dados recriptografados com sucesso")
            except:
                pass
            
            return True, "Senhas reconfiguradas e dados recriptografados com sucesso"
        except Exception as e:
            try:
                self.banco_dados.registrar_log("erro", f"Erro ao reconfigurar senhas: {str(e)}")
            except:
                pass
            return False, f"Erro ao reconfigurar senhas: {str(e)}"

    def editar_senha(self, id_senha, titulo, senha, descricao=""):
        """Edita uma senha existente"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado"
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Verificar se a senha existe
            cursor.execute("SELECT titulo FROM senhas WHERE id = ?", (id_senha,))
            resultado = cursor.fetchone()
            
            if not resultado:
                conn.close()
                return False, "Senha não encontrada"
            
            titulo_antigo = resultado[0]
            
            # Obter dados do usuário
            cursor.execute("SELECT hash_senha FROM usuarios LIMIT 1")
            resultado_usuario = cursor.fetchone()
            
            if not resultado_usuario:
                conn.close()
                return False, "Usuário não encontrado"
            
            hash_senha_usuario = resultado_usuario[0]
            
            # Usar o hash da senha do usuário como base para a chave de criptografia
            chave_base = hash_senha_usuario[:32].encode()
            
            # Criptografar a senha
            dados_criptografados, iv = self.criptografia.criptografar(senha, chave_base)
            
            # Atualizar no banco de dados
            data_atual = datetime.datetime.now().isoformat()
            cursor.execute(
                "UPDATE senhas SET titulo = ?, descricao = ?, dados_criptografados = ?, iv = ?, data_modificacao = ? WHERE id = ?",
                (titulo, descricao, dados_criptografados, iv, data_atual, id_senha)
            )
            
            conn.commit()
            conn.close()
            
            try:
                self.banco_dados.registrar_log("dados", f"Senha editada: {titulo_antigo} -> {titulo}")
            except:
                pass
            return True, "Senha atualizada com sucesso"
        except Exception as e:
            try:
                self.banco_dados.registrar_log("erro", f"Erro ao editar senha: {str(e)}")
            except:
                pass
            return False, f"Erro ao editar senha: {str(e)}"

    def editar_nota(self, id_nota, titulo, conteudo):
        """Edita uma nota existente"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado"
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Verificar se a nota existe
            cursor.execute("SELECT titulo FROM notas WHERE id = ?", (id_nota,))
            resultado = cursor.fetchone()
            
            if not resultado:
                conn.close()
                return False, "Nota não encontrada"
            
            titulo_antigo = resultado[0]
            
            # Obter dados do usuário
            cursor.execute("SELECT hash_senha FROM usuarios LIMIT 1")
            resultado_usuario = cursor.fetchone()
            
            if not resultado_usuario:
                conn.close()
                return False, "Usuário não encontrado"
            
            hash_senha_usuario = resultado_usuario[0]
            
            # Usar o hash da senha do usuário como base para a chave de criptografia
            chave_base = hash_senha_usuario[:32].encode()
            
            # Criptografar o conteúdo
            dados_criptografados, iv = self.criptografia.criptografar(conteudo, chave_base)
            
            # Atualizar no banco de dados
            data_atual = datetime.datetime.now().isoformat()
            cursor.execute(
                "UPDATE notas SET titulo = ?, dados_criptografados = ?, iv = ?, data_modificacao = ? WHERE id = ?",
                (titulo, dados_criptografados, iv, data_atual, id_nota)
            )
            
            conn.commit()
            conn.close()
            
            try:
                self.banco_dados.registrar_log("dados", f"Nota editada: {titulo_antigo} -> {titulo}")
            except:
                pass
            return True, "Nota atualizada com sucesso"
        except Exception as e:
            try:
                self.banco_dados.registrar_log("erro", f"Erro ao editar nota: {str(e)}")
            except:
                pass
            return False, f"Erro ao editar nota: {str(e)}"

    def criar_categoria(self, nome, descricao=""):
        """Cria uma nova categoria"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado"
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Verificar se a tabela de categorias existe
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                descricao TEXT,
                data_criacao TEXT NOT NULL
            )
            """)
            
            # Verificar se já existe uma categoria com o mesmo nome
            cursor.execute("SELECT id FROM categorias WHERE nome = ?", (nome,))
            if cursor.fetchone():
                conn.close()
                return False, "Já existe uma categoria com este nome"
            
            # Inserir nova categoria
            data_atual = datetime.datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO categorias (nome, descricao, data_criacao) VALUES (?, ?, ?)",
                (nome, descricao, data_atual)
            )
            
            # Adicionar colunas de categoria às tabelas existentes, se necessário
            try:
                cursor.execute("ALTER TABLE senhas ADD COLUMN categoria_id INTEGER")
            except:
                pass  # Coluna já existe
            
            try:
                cursor.execute("ALTER TABLE notas ADD COLUMN categoria_id INTEGER")
            except:
                pass  # Coluna já existe
            
            conn.commit()
            conn.close()
            
            try:
                self.banco_dados.registrar_log("dados", f"Nova categoria criada: {nome}")
            except:
                pass
            return True, "Categoria criada com sucesso"
        except Exception as e:
            try:
                self.banco_dados.registrar_log("erro", f"Erro ao criar categoria: {str(e)}")
            except:
                pass
            return False, f"Erro ao criar categoria: {str(e)}"

    def obter_categorias(self):
        """Obtém a lista de categorias"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado", None
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Obter todas as categorias
            cursor.execute("SELECT id, nome FROM categorias ORDER BY nome")
            resultados = cursor.fetchall()
            
            conn.close()
            
            categorias = []
            for id_categoria, nome in resultados:
                categorias.append({
                    "id": id_categoria,
                    "nome": nome
                })
            
            return True, f"Encontradas {len(categorias)} categorias", categorias
        except Exception as e:
            try:
                self.banco_dados.registrar_log("erro", f"Erro ao obter categorias: {str(e)}")
            except:
                pass
            return False, f"Erro ao obter categorias: {str(e)}", None

    def atribuir_categoria(self, tipo, id_item, id_categoria):
        """Atribui uma categoria a um item (senha ou nota)"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado"
        
        if tipo not in ["senha", "nota"]:
            return False, "Tipo inválido. Use 'senha' ou 'nota'."
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Verificar se o item existe
            tabela = "senhas" if tipo == "senha" else "notas"
            cursor.execute(f"SELECT id FROM {tabela} WHERE id = ?", (id_item,))
            if not cursor.fetchone():
                conn.close()
                return False, f"{tipo.capitalize()} não encontrada"
            
            # Verificar se a categoria existe (se não for NULL)
            if id_categoria is not None:
                cursor.execute("SELECT id FROM categorias WHERE id = ?", (id_categoria,))
                if not cursor.fetchone():
                    conn.close()
                    return False, "Categoria não encontrada"
            
            # Atualizar a categoria do item
            cursor.execute(
                f"UPDATE {tabela} SET categoria_id = ? WHERE id = ?",
                (id_categoria, id_item)
            )
            
            conn.commit()
            conn.close()
            
            try:
                self.banco_dados.registrar_log("dados", f"Categoria atribuída a {tipo}: {id_item}")
            except:
                pass
            return True, f"Categoria atribuída com sucesso à {tipo}"
        except Exception as e:
            try:
                self.banco_dados.registrar_log("erro", f"Erro ao atribuir categoria: {str(e)}")
            except:
                pass
            return False, f"Erro ao atribuir categoria: {str(e)}"

    def fazer_backup(self, caminho_destino):
        """Faz um backup criptografado do banco de dados e configurações"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado"
        
        try:
            # Verificar se o diretório de destino existe
            if not os.path.exists(caminho_destino):
                return False, "Diretório de destino não encontrado"
            
            # Gerar nome de arquivo com data e hora
            data_hora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"backup_{data_hora}.enc"
            caminho_backup = os.path.join(caminho_destino, nome_arquivo)
            
            # Obter hash da senha do usuário para usar como chave de criptografia
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            cursor.execute("SELECT hash_senha FROM usuarios LIMIT 1")
            resultado = cursor.fetchone()
            conn.close()
            
            if not resultado:
                return False, "Usuário não encontrado"
            
            hash_senha_usuario = resultado[0]
            chave_base = hash_senha_usuario[:32].encode()  # Usar os primeiros 32 caracteres do hash
            
            # Criar arquivo temporário para o backup
            import tempfile
            temp_dir = tempfile.mkdtemp()
            temp_db = os.path.join(temp_dir, "temp_db.db")
            temp_config = os.path.join(temp_dir, "temp_config.json")
            
            # Copiar arquivos para o diretório temporário
            import shutil
            shutil.copy2(self.caminho_db, temp_db)
            shutil.copy2(self.caminho_config, temp_config)
            
            # Criar arquivo ZIP com os arquivos temporários
            import zipfile
            temp_zip = os.path.join(temp_dir, "backup.zip")
            with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(temp_db, "sistema.db")
                zipf.write(temp_config, "config.json")
            
            # Ler o arquivo ZIP
            with open(temp_zip, 'rb') as f:
                dados = f.read()
            
            # Criptografar o arquivo ZIP
            dados_criptografados, iv = self.criptografia.criptografar(dados, chave_base)
            
            # Criar arquivo de backup com metadados e dados criptografados
            metadados = {
                "versao": "1.0",
                "data_backup": data_hora,
                "iv": iv
            }
            
            with open(caminho_backup, 'w') as f:
                # Escrever metadados como JSON
                json.dump(metadados, f)
                # Adicionar uma linha em branco para separar metadados dos dados
                f.write("\n")
                # Escrever dados criptografados
                f.write(dados_criptografados)
            
            # Limpar arquivos temporários
            shutil.rmtree(temp_dir)
            
            try:
                self.banco_dados.registrar_log("sistema", f"Backup criptografado realizado: {caminho_backup}")
            except:
                pass
            return True, f"Backup criptografado realizado com sucesso em {caminho_backup}"
        except Exception as e:
            try:
                self.banco_dados.registrar_log("erro", f"Erro ao fazer backup: {str(e)}")
            except:
                pass
            return False, f"Erro ao fazer backup: {str(e)}"

    def restaurar_backup(self, caminho_backup):
        """Restaura um backup criptografado do banco de dados"""
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(caminho_backup):
                return False, "Arquivo de backup não encontrado"
            
            # Ler o arquivo de backup
            with open(caminho_backup, 'r') as f:
                # Ler a primeira linha como JSON (metadados)
                linha_metadados = f.readline()
                metadados = json.loads(linha_metadados)
                
                # Verificar versão do backup
                if metadados.get("versao") != "1.0":
                    return False, "Versão de backup não suportada"
                
                # Obter IV dos metadados
                iv = metadados.get("iv")
                if not iv:
                    return False, "Backup corrompido: IV não encontrado"
                
                # Ler o resto do arquivo (dados criptografados)
                dados_criptografados = f.read()
            
            # Solicitar senha para descriptografar o backup
            senha = simpledialog.askstring("Senha de Backup", "Digite a senha usada para criar o backup:", show="*")
            if not senha:
                return False, "Operação cancelada pelo usuário"
            
            # Gerar hash da senha para usar como chave de descriptografia
            hash_senha, _ = self.criptografia.hash_senha(senha)
            chave_base = hash_senha[:32].encode()  # Usar os primeiros 32 caracteres do hash
            
            try:
                # Descriptografar os dados
                dados_zip = self.criptografia.descriptografar(dados_criptografados, iv, chave_base)
                
                # Criar diretório temporário para extrair os arquivos
                import tempfile
                temp_dir = tempfile.mkdtemp()
                temp_zip = os.path.join(temp_dir, "backup.zip")
                
                # Escrever o arquivo ZIP
                with open(temp_zip, 'wb') as f:
                    f.write(dados_zip)
                
                # Extrair os arquivos
                import zipfile
                with zipfile.ZipFile(temp_zip, 'r') as zipf:
                    zipf.extractall(temp_dir)
                
                # Caminhos para os arquivos extraídos
                db_extraido = os.path.join(temp_dir, "sistema.db")
                config_extraido = os.path.join(temp_dir, "config.json")
                
                # Verificar se os arquivos foram extraídos corretamente
                if not os.path.exists(db_extraido) or not os.path.exists(config_extraido):
                    return False, "Backup corrompido: arquivos não encontrados"
                
                # Fechar conexões com o banco de dados atual
                self.usuario_autenticado = False
                
                # Fazer backup do banco de dados atual antes de substituí-lo
                data_hora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_atual = os.path.join(os.path.dirname(self.caminho_db), f"pre_restauracao_{data_hora}.db")
                import shutil
                shutil.copy2(self.caminho_db, backup_atual)
                
                # Substituir os arquivos
                shutil.copy2(db_extraido, self.caminho_db)
                shutil.copy2(config_extraido, self.caminho_config)
                
                # Limpar arquivos temporários
                shutil.rmtree(temp_dir)
                
                # Reinicializar o sistema
                self.inicializar_sistema()
                
                return True, "Backup restaurado com sucesso. Por favor, faça login novamente."
            except Exception as e:
                return False, f"Erro ao descriptografar backup: {str(e)}"
        except Exception as e:
            return False, f"Erro ao restaurar backup: {str(e)}"

    def pesquisar_senhas(self, termo_busca):
        """Pesquisa senhas por título ou descrição"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado", None
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Pesquisar senhas que contenham o termo de busca no título ou descrição
            cursor.execute(
                "SELECT id, titulo, descricao, data_criacao, categoria_id FROM senhas WHERE titulo LIKE ? OR descricao LIKE ? ORDER BY titulo",
                (f"%{termo_busca}%", f"%{termo_busca}%")
            )
            resultados = cursor.fetchall()
            
            conn.close()
            
            senhas = []
            for id_senha, titulo, descricao, data_criacao, categoria_id in resultados:
                senhas.append({
                    "id": id_senha,
                    "titulo": titulo,
                    "descricao": descricao if descricao else "",
                    "data_criacao": data_criacao,
                    "categoria_id": categoria_id
                })
            
            return True, f"Encontradas {len(senhas)} senhas", senhas
        except Exception as e:
            try:
                self.banco_dados.registrar_log("erro", f"Erro ao pesquisar senhas: {str(e)}")
            except:
                pass
            return False, f"Erro ao pesquisar senhas: {str(e)}", None

    def pesquisar_notas(self, termo_busca):
        """Pesquisa notas por título"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado", None
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Pesquisar notas que contenham o termo de busca no título
            cursor.execute(
                "SELECT id, titulo, data_criacao, categoria_id FROM notas WHERE titulo LIKE ? ORDER BY titulo",
                (f"%{termo_busca}%",)
            )
            resultados = cursor.fetchall()
            
            conn.close()
            
            notas = []
            for id_nota, titulo, data_criacao, categoria_id in resultados:
                notas.append({
                    "id": id_nota,
                    "titulo": titulo,
                    "data_criacao": data_criacao,
                    "categoria_id": categoria_id
                })
            
            return True, f"Encontradas {len(notas)} notas", notas
        except Exception as e:
            try:
                self.banco_dados.registrar_log("erro", f"Erro ao pesquisar notas: {str(e)}")
            except:
                pass
            return False, f"Erro ao pesquisar notas: {str(e)}", None

    def excluir_senha(self, id_senha):
        """Exclui uma senha do cofre"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado"
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Verificar se a senha existe
            cursor.execute("SELECT titulo FROM senhas WHERE id = ?", (id_senha,))
            resultado = cursor.fetchone()
            
            if not resultado:
                conn.close()
                return False, "Senha não encontrada"
            
            titulo = resultado[0]
            
            # Excluir a senha
            cursor.execute("DELETE FROM senhas WHERE id = ?", (id_senha,))
            
            conn.commit()
            conn.close()
            
            self.banco_dados.registrar_log("sistema", f"Senha '{titulo}' excluída")
            return True, f"Senha '{titulo}' excluída com sucesso"
        except Exception as e:
            try:
                self.banco_dados.registrar_log("erro", f"Erro ao excluir senha: {str(e)}")
            except:
                pass
            return False, f"Erro ao excluir senha: {str(e)}"

    def excluir_nota(self, id_nota):
        """Exclui uma nota do cofre"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado"
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Verificar se a nota existe
            cursor.execute("SELECT titulo FROM notas WHERE id = ?", (id_nota,))
            resultado = cursor.fetchone()
            
            if not resultado:
                conn.close()
                return False, "Nota não encontrada"
            
            titulo = resultado[0]
            
            # Excluir a nota
            cursor.execute("DELETE FROM notas WHERE id = ?", (id_nota,))
            
            conn.commit()
            conn.close()
            
            self.banco_dados.registrar_log("sistema", f"Nota '{titulo}' excluída")
            return True, f"Nota '{titulo}' excluída com sucesso"
        except Exception as e:
            try:
                self.banco_dados.registrar_log("erro", f"Erro ao excluir nota: {str(e)}")
            except:
                pass
            return False, f"Erro ao excluir nota: {str(e)}"

    def excluir_arquivo(self, id_arquivo):
        """Exclui um arquivo do cofre"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado"
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Verificar se o arquivo existe
            cursor.execute("SELECT nome_original, nome_criptografado FROM arquivos WHERE id = ?", (id_arquivo,))
            resultado = cursor.fetchone()
            
            if not resultado:
                conn.close()
                return False, "Arquivo não encontrado"
            
            nome_original, nome_criptografado = resultado
            
            # Excluir o arquivo físico
            caminho_arquivo = os.path.join(self.caminho_base, "arquivos", nome_criptografado)
            if os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo)
            
            # Excluir o registro do banco de dados
            cursor.execute("DELETE FROM arquivos WHERE id = ?", (id_arquivo,))
            
            conn.commit()
            conn.close()
            
            self.banco_dados.registrar_log("sistema", f"Arquivo '{nome_original}' excluído")
            return True, f"Arquivo '{nome_original}' excluído com sucesso"
        except Exception as e:
            try:
                self.banco_dados.registrar_log("erro", f"Erro ao excluir arquivo: {str(e)}")
            except:
                pass
            return False, f"Erro ao excluir arquivo: {str(e)}"

    def carregar_configuracoes(self):
        """Carrega as configurações do sistema"""
        try:
            # Verificar se o arquivo de configuração existe
            if not os.path.exists(self.caminho_config):
                # Criar configuração padrão
                self.criar_configuracao_padrao()
            
            # Carregar configurações
            with open(self.caminho_config, 'r') as f:
                config = json.load(f)
            
            # Definir valores padrão caso não existam no arquivo
            self.intervalo_confirmacao = config.get("intervalo_confirmacao", 30)  # dias
            self.max_tentativas = config.get("max_tentativas_senha", 5)
            self.modo_camuflagem = config.get("modo_camuflagem", "bloco_notas")
            self.autodestruicao_ativada = config.get("autodestruicao_ativada", True)
            self.nome_exibicao = config.get("nome_exibicao", "Bloco de Notas Portátil")
            
            # Registrar log
            self.banco_dados.registrar_log("sistema", "Configurações carregadas com sucesso")
            
            return True
        except Exception as e:
            print(f"Erro ao carregar configurações: {str(e)}")
            # Tentar criar configuração padrão em caso de erro
            try:
                self.criar_configuracao_padrao()
                return self.carregar_configuracoes()  # Tentar novamente
            except:
                return False

    def gerar_nova_frase_mnemonica(self):
        """Gera uma nova frase mnemônica para o usuário atual"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado", None
        
        if not BIP39_DISPONIVEL:
            return False, "Suporte a frases mnemônicas não disponível", None
        
        try:
            # Gerar entropia aleatória (128 bits = 16 bytes = frase de 12 palavras)
            entropia = secrets.token_bytes(16)
            mnemo = Mnemonic("english")
            
            # Gerar frase mnemônica
            frase_mnemonica = mnemo.to_mnemonic(entropia)
            
            # Gerar seed a partir da frase (com senha vazia como passphrase)
            seed = mnemo.to_seed(frase_mnemonica, "")
            
            # Derivar identificador único do compartimento (primeiros 16 bytes do seed)
            compartimento_id = seed[:16].hex()
            
            # Derivar chave de criptografia para este compartimento
            chave_compartimento = self.derivar_chave_compartimento(seed)
            
            # Criptografar a chave do compartimento com a chave mestra do usuário
            # (isso permite que o usuário acesse todos os compartimentos com sua senha principal)
            usuario = self.banco_dados.obter_usuario()
            if not usuario:
                return False, "Usuário não encontrado", None
            
            # Desempacotar com tratamento para o caso de seed_hex não estar disponível
            if len(usuario) == 5:
                id_usuario, hash_senha, salt, hash_senha_heranca, salt_heranca = usuario
                seed_hex = None
            else:
                id_usuario, hash_senha, salt, hash_senha_heranca, salt_heranca, seed_hex = usuario
            
            # Usar o hash da senha do usuário como base para a chave de criptografia
            chave_base = hash_senha[:32].encode()
            
            # Criptografar a chave do compartimento
            chave_criptografada, iv = self.criptografia.criptografar(chave_compartimento.hex(), chave_base)
            
            # Salvar o compartimento no banco de dados
            data_atual = datetime.datetime.now().isoformat()
            sucesso = self.banco_dados.criar_compartimento(
                compartimento_id, 
                chave_criptografada, 
                iv, 
                data_atual
            )
            
            if sucesso:
                self.banco_dados.registrar_log("sistema", f"Novo compartimento criado: {compartimento_id}")
                return True, f"Compartimento '{compartimento_id}' criado com sucesso", frase_mnemonica
            else:
                return False, "Erro ao criar compartimento", None
        except Exception as e:
            self.banco_dados.registrar_log("erro", f"Erro ao criar compartimento: {str(e)}")
            return False, f"Erro ao criar compartimento: {str(e)}", None
    
    def ativar_compartimento_por_frase(self, frase_mnemonica):
        """Ativa um compartimento específico usando sua frase mnemônica"""
        if not BIP39_DISPONIVEL:
            return False, "Suporte a frases mnemônicas não disponível"
        
        try:
            # Verificar se a frase é válida
            mnemo = Mnemonic("english")
            if not mnemo.check(frase_mnemonica):
                return False, "Frase mnemônica inválida"
            
            # Gerar seed a partir da frase
            seed = mnemo.to_seed(frase_mnemonica, "")
            
            # Derivar identificador do compartimento
            compartimento_id = seed[:16].hex()
            
            # Buscar compartimento no banco de dados
            compartimento = self.banco_dados.obter_compartimento_por_id(compartimento_id)
            
            if not compartimento:
                return False, "Compartimento não encontrado para esta frase mnemônica"
            
            # Derivar chave do compartimento
            self.chave_compartimento_ativo = self.derivar_chave_compartimento(seed)
            self.compartimento_ativo = compartimento["nome"]
            
            self.banco_dados.registrar_log("sistema", f"Compartimento ativado: {self.compartimento_ativo}")
            return True, f"Compartimento '{self.compartimento_ativo}' ativado com sucesso"
        except Exception as e:
            self.banco_dados.registrar_log("erro", f"Erro ao ativar compartimento: {str(e)}")
            return False, f"Erro ao ativar compartimento: {str(e)}"
    
    def ativar_compartimento_por_nome(self, nome_compartimento):
        """Ativa um compartimento pelo nome (usando a senha principal)"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado"
        
        try:
            # Buscar compartimento no banco de dados
            compartimento = self.banco_dados.obter_compartimento_por_nome(nome_compartimento)
            
            if not compartimento:
                return False, f"Compartimento '{nome_compartimento}' não encontrado"
            
            # Obter dados do usuário
            usuario = self.banco_dados.obter_usuario()
            if not usuario:
                return False, "Usuário não encontrado"
            
            id_usuario, hash_senha, salt, hash_senha_heranca, salt_heranca, seed_hex = usuario
            
            # Usar o hash da senha do usuário como base para a chave de criptografia
            chave_base = hash_senha[:32].encode()
            
            # Descriptografar a chave do compartimento
            chave_criptografada = compartimento["chave_criptografada"]
            iv = compartimento["iv"]
            
            chave_hex = self.criptografia.descriptografar(chave_criptografada, iv, chave_base).decode()
            self.chave_compartimento_ativo = bytes.fromhex(chave_hex)
            self.compartimento_ativo = nome_compartimento
            
            self.banco_dados.registrar_log("sistema", f"Compartimento ativado: {self.compartimento_ativo}")
            return True, f"Compartimento '{self.compartimento_ativo}' ativado com sucesso"
        except Exception as e:
            self.banco_dados.registrar_log("erro", f"Erro ao ativar compartimento: {str(e)}")
            return False, f"Erro ao ativar compartimento: {str(e)}"
    
    def derivar_chave_compartimento(self, seed):
        """Deriva uma chave de criptografia para um compartimento a partir do seed"""
        # Usar HMAC-SHA256 para derivar uma chave de 32 bytes
        return hmac.new(b"compartimento", seed, hashlib.sha256).digest()
    
    def listar_compartimentos(self):
        """Lista todos os compartimentos disponíveis"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado", None
        
        try:
            compartimentos = self.banco_dados.obter_todos_compartimentos()
            return True, f"Encontrados {len(compartimentos)} compartimentos", compartimentos
        except Exception as e:
            self.banco_dados.registrar_log("erro", f"Erro ao listar compartimentos: {str(e)}")
            return False, f"Erro ao listar compartimentos: {str(e)}", None

    def criar_compartimento(self, nome, descricao=None):
        """Cria um novo compartimento de dados com sua própria frase mnemônica"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado", None
        
        if not BIP39_DISPONIVEL:
            return False, "Suporte a frases mnemônicas não disponível", None
        
        try:
            # Verificar se já existe um compartimento com este nome
            compartimento_existente = self.banco_dados.obter_compartimento_por_nome(nome)
            if compartimento_existente:
                return False, f"Já existe um compartimento chamado '{nome}'", None
            
            # Gerar entropia aleatória (128 bits = 16 bytes = frase de 12 palavras)
            entropia = secrets.token_bytes(16)
            mnemo = Mnemonic("english")
            
            # Gerar frase mnemônica
            frase_mnemonica = mnemo.to_mnemonic(entropia)
            
            # Gerar seed a partir da frase (com senha vazia como passphrase)
            seed = mnemo.to_seed(frase_mnemonica, "")
            
            # Derivar identificador único do compartimento (primeiros 16 bytes do seed)
            compartimento_id = seed[:16].hex()
            
            # Derivar chave de criptografia para este compartimento
            chave_compartimento = self.derivar_chave_compartimento(seed)
            
            # Criptografar a chave do compartimento com a chave mestra do usuário
            # (isso permite que o usuário acesse todos os compartimentos com sua senha principal)
            usuario = self.banco_dados.obter_usuario()
            if not usuario:
                return False, "Usuário não encontrado", None
            
            # Desempacotar com tratamento para o caso de seed_hex não estar disponível
            if len(usuario) == 5:
                id_usuario, hash_senha, salt, hash_senha_heranca, salt_heranca = usuario
                seed_hex = None
            else:
                id_usuario, hash_senha, salt, hash_senha_heranca, salt_heranca, seed_hex = usuario
            
            # Usar o hash da senha do usuário como base para a chave de criptografia
            chave_base = hash_senha[:32].encode()
            
            # Criptografar a chave do compartimento
            chave_criptografada, iv = self.criptografia.criptografar(chave_compartimento.hex(), chave_base)
            
            # Salvar o compartimento no banco de dados
            data_atual = datetime.datetime.now().isoformat()
            sucesso = self.banco_dados.criar_compartimento(
                nome, 
                compartimento_id, 
                chave_criptografada, 
                iv, 
                descricao, 
                data_atual
            )
            
            if sucesso:
                self.banco_dados.registrar_log("sistema", f"Novo compartimento criado: {nome}")
                return True, f"Compartimento '{nome}' criado com sucesso", frase_mnemonica
            else:
                return False, "Erro ao criar compartimento", None
        except Exception as e:
            self.banco_dados.registrar_log("erro", f"Erro ao criar compartimento: {str(e)}")
            return False, f"Erro ao criar compartimento: {str(e)}", None

    def autenticar_por_frase(self, frase_mnemonica):
        """Autentica o usuário usando uma frase mnemônica"""
        if not BIP39_DISPONIVEL:
            return False, "Suporte a frases mnemônicas não disponível", False
        
        try:
            # Verificar se a frase é válida
            mnemo = Mnemonic("english")
            if not mnemo.check(frase_mnemonica):
                self.tentativas_senha += 1
                self.banco_dados.registrar_log("autenticacao", "Tentativa de autenticação falhou: frase mnemônica inválida")
                return False, "Frase mnemônica inválida", False
            
            # Gerar seed a partir da frase
            seed = mnemo.to_seed(frase_mnemonica, "")
            
            # Derivar identificador do compartimento
            compartimento_id = seed[:16].hex()
            
            # Buscar compartimento no banco de dados
            compartimento = self.banco_dados.obter_compartimento_por_id(compartimento_id)
            
            if not compartimento:
                self.tentativas_senha += 1
                self.banco_dados.registrar_log("autenticacao", "Tentativa de autenticação falhou: compartimento não encontrado")
                return False, "Compartimento não encontrado para esta frase mnemônica", False
            
            # Autenticar o usuário em modo restrito (acesso apenas a este compartimento)
            self.usuario_autenticado = True
            self.tentativas_senha = 0
            self.modo_acesso_restrito = True
            self.compartimento_restrito = compartimento["nome"]
            
            # Derivar chave do compartimento
            self.chave_compartimento_ativo = self.derivar_chave_compartimento(seed)
            self.compartimento_ativo = compartimento["nome"]
            
            self.banco_dados.registrar_log("autenticacao", f"Usuário autenticado com frase mnemônica para o compartimento: {self.compartimento_ativo}")
            return True, f"Autenticado no compartimento '{self.compartimento_ativo}'", True
        except Exception as e:
            self.banco_dados.registrar_log("erro", f"Erro ao autenticar por frase mnemônica: {str(e)}")
            return False, f"Erro ao autenticar: {str(e)}", False

    def listar_senhas(self, filtro=None, categoria_id=None):
        """Lista todas as senhas armazenadas"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado", None
        
        try:
            # Obter senhas do compartimento ativo
            senhas = self.banco_dados.obter_senhas(
                compartimento=self.compartimento_ativo,
                filtro=filtro, 
                categoria_id=categoria_id
            )
            
            return True, f"Encontradas {len(senhas)} senhas", senhas
        except Exception as e:
            self.banco_dados.registrar_log("erro", f"Erro ao listar senhas: {str(e)}")
            return False, f"Erro ao listar senhas: {str(e)}", None

    def listar_notas(self, filtro=None, categoria_id=None):
        """Lista todas as notas armazenadas"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado", None
        
        try:
            # Obter notas do compartimento ativo
            notas = self.banco_dados.obter_notas(
                compartimento=self.compartimento_ativo,
                filtro=filtro, 
                categoria_id=categoria_id
            )
            
            return True, f"Encontradas {len(notas)} notas", notas
        except Exception as e:
            self.banco_dados.registrar_log("erro", f"Erro ao listar notas: {str(e)}")
            return False, f"Erro ao listar notas: {str(e)}", None

    def listar_arquivos(self, filtro=None, categoria_id=None):
        """Lista todos os arquivos armazenados"""
        if not self.usuario_autenticado:
            return False, "Usuário não autenticado", None
        
        try:
            # Obter arquivos do compartimento ativo
            arquivos = self.banco_dados.obter_arquivos(
                compartimento=self.compartimento_ativo,
                filtro=filtro, 
                categoria_id=categoria_id
            )
            
            return True, f"Encontrados {len(arquivos)} arquivos", arquivos
        except Exception as e:
            self.banco_dados.registrar_log("erro", f"Erro ao listar arquivos: {str(e)}")
            return False, f"Erro ao listar arquivos: {str(e)}", None

    def obter_tempo_restante(self):
        """Obtém o tempo restante até a ativação do modo de recuperação"""
        try:
            # Carregar configurações
            with open(self.caminho_config, 'r') as f:
                config = json.load(f)
            
            # Obter data da última confirmação
            ultima_confirmacao_str = config.get("ultima_confirmacao")
            
            if not ultima_confirmacao_str:
                return 0
            
            # Converter string para objeto datetime
            ultima_confirmacao = datetime.datetime.fromisoformat(ultima_confirmacao_str)
            
            # Obter intervalo de confirmação em dias
            intervalo_dias = config.get("intervalo_confirmacao", 30)
            
            # Calcular data limite
            data_limite = ultima_confirmacao + datetime.timedelta(days=intervalo_dias)
            
            # Calcular tempo restante
            agora = datetime.datetime.now()
            diferenca = data_limite - agora
            
            # Converter para segundos
            segundos_restantes = int(diferenca.total_seconds())
            
            # Se negativo, retornar 0
            return max(0, segundos_restantes)
            
        except Exception as e:
            print(f"Erro ao obter tempo restante: {str(e)}")
            traceback.print_exc()
            return 0

# Função principal para iniciar o aplicativo
def main():
    cofre = CofreDigital()
    interface = InterfaceGrafica(cofre)
    interface.iniciar()

if __name__ == "__main__":
    main()
