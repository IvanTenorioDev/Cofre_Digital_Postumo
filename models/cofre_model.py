import os
import sqlite3
import json
import datetime
import secrets
import base64
from dateutil.relativedelta import relativedelta

from models.crypto_utils import CryptoUtils
from models.bip39_validator import BIP39Validator

class CofreDigitalModel:
    """Modelo principal do Cofre Digital Póstumo."""
    
    def __init__(self):
        """Inicializa o modelo do cofre digital."""
        # Configuração de caminhos
        self.caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.caminho_dados = os.path.join(self.caminho_base, "dados")
        self.caminho_db = os.path.join(self.caminho_dados, "cofre.db")
        self.caminho_config = os.path.join(self.caminho_dados, "config.json")
        self.caminho_arquivos = os.path.join(self.caminho_base, "arquivos")
        self.caminho_backup = os.path.join(self.caminho_base, "backup")
        
        # Criar diretórios necessários
        os.makedirs(self.caminho_dados, exist_ok=True)
        os.makedirs(self.caminho_arquivos, exist_ok=True)
        os.makedirs(self.caminho_backup, exist_ok=True)
        
        # Estado do sistema
        self.usuario_autenticado = False
        self.usuario_atual = None
        self.modo_heranca_ativo = False
        self.compartimento_ativo = "principal"
        self.chave_compartimento_ativo = None
        self.tentativas_senha = 0
        
        # Configuração padrão
        self.config = {
            "intervalo_confirmacao": 90,  # dias
            "ultima_confirmacao": datetime.datetime.now().isoformat(),
            "max_tentativas_senha": 5,
            "modo_camuflagem": "bloco_notas",
            "autodestruicao_ativada": False,
            "nome_exibicao": "Cofre Digital Póstumo",
            "email_notificacao": "",
            "periodo_notificacao": 15  # dias antes do vencimento
        }
        
        # Utilitários
        self.crypto = CryptoUtils()
        self.bip39 = BIP39Validator()
        
        # Inicializar banco de dados e configurações
        self.inicializar_sistema()
    
    def inicializar_sistema(self):
        """Inicializa o banco de dados e configurações."""
        # Criar estrutura do banco de dados
        self.criar_estrutura_db()
        
        # Verificar e atualizar a estrutura se necessário
        self.verificar_estrutura_db()
        
        # Carregar configurações
        self.carregar_configuracoes()
        
        # Verificar modo de herança
        self.verificar_modo_heranca()
    
    def criar_estrutura_db(self):
        """Cria a estrutura inicial do banco de dados."""
        conn = sqlite3.connect(self.caminho_db)
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            hash_senha TEXT NOT NULL,
            salt TEXT NOT NULL,
            hash_senha_heranca TEXT,
            salt_heranca TEXT,
            data_criacao TEXT NOT NULL,
            seed_hex TEXT,
            email TEXT
        )
        """)
        
        # Tabela de senhas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS senhas (
            id INTEGER PRIMARY KEY,
            titulo TEXT NOT NULL,
            senha TEXT NOT NULL,
            usuario TEXT,
            url TEXT,
            categoria TEXT,
            notas TEXT,
            data_criacao TEXT NOT NULL,
            data_modificacao TEXT
        )
        """)
        
        # Tabela de notas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY,
            titulo TEXT NOT NULL,
            conteudo_criptografado TEXT NOT NULL,
            iv TEXT NOT NULL,
            data_criacao TEXT NOT NULL,
            data_modificacao TEXT NOT NULL,
            categoria_id INTEGER,
            compartimento TEXT DEFAULT 'principal',
            FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        )
        """)
        
        # Tabela de arquivos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS arquivos (
            id INTEGER PRIMARY KEY,
            nome_original TEXT NOT NULL,
            nome_criptografado TEXT NOT NULL,
            descricao TEXT,
            iv TEXT NOT NULL,
            data_upload TEXT NOT NULL,
            categoria_id INTEGER,
            compartimento TEXT DEFAULT 'principal',
            FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        )
        """)
        
        # Tabela de categorias
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            descricao TEXT,
            data_criacao TEXT NOT NULL
        )
        """)
        
        # Tabela de logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            tipo TEXT NOT NULL,
            mensagem TEXT NOT NULL,
            data TEXT NOT NULL
        )
        """)
        
        # Tabela de compartimentos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS compartimentos (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            compartimento_id TEXT NOT NULL UNIQUE,
            chave_criptografada TEXT NOT NULL,
            iv TEXT NOT NULL,
            descricao TEXT,
            data_criacao TEXT NOT NULL
        )
        """)
        
        # Tabela de carteiras BTC
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS carteiras_btc (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            descricao TEXT,
            frase_criptografada TEXT NOT NULL,
            iv TEXT NOT NULL,
            passphrase_criptografada TEXT,
            iv_passphrase TEXT,
            data_criacao TEXT NOT NULL,
            data_modificacao TEXT NOT NULL,
            categoria_id INTEGER,
            compartimento TEXT DEFAULT 'principal',
            FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        )
        """)
        
        # Tabela de herança
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS herancas (
            id INTEGER PRIMARY KEY,
            nome_herdeiro TEXT NOT NULL,
            email_herdeiro TEXT,
            compartimentos TEXT NOT NULL,  -- Lista de IDs de compartimentos separados por vírgula
            instrucoes TEXT,
            hash_chave_acesso TEXT,
            salt_chave_acesso TEXT,
            data_criacao TEXT NOT NULL
        )
        """)
        
        conn.commit()
        conn.close()
        
        # Registrar log
        self.registrar_log("sistema", "Estrutura do banco de dados verificada")
    
    def verificar_estrutura_db(self):
        """Verifica e atualiza a estrutura do banco de dados conforme necessário."""
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Verificar se a tabela senhas tem todas as colunas necessárias
            cursor.execute("PRAGMA table_info(senhas)")
            colunas = {info[1] for info in cursor.fetchall()}
            
            # Colunas que devem existir na tabela senhas
            colunas_necessarias = {
                "titulo", "senha", "usuario", "url", "categoria", "notas", 
                "data_criacao", "data_modificacao"
            }
            
            # Verificar se alguma coluna está faltando
            colunas_faltando = colunas_necessarias - colunas
            
            # Se houver colunas faltando, adicionar uma a uma
            if colunas_faltando:
                self.registrar_log("sistema", f"Atualizando estrutura da tabela senhas. Adicionando colunas: {', '.join(colunas_faltando)}")
                
                # SQLite não permite ALTER TABLE ADD COLUMN com NOT NULL sem valor padrão
                # Por isso, vamos recriar a tabela se ela estiver muito diferente
                
                if "senha" in colunas_faltando or "titulo" in colunas_faltando or "data_criacao" in colunas_faltando:
                    # Casos que exigiriam NOT NULL, melhor recriar a tabela
                    # Primeiro, fazer backup da tabela existente
                    try:
                        cursor.execute("ALTER TABLE senhas RENAME TO senhas_old")
                        
                        # Criar a nova tabela com a estrutura correta
                        cursor.execute("""
                        CREATE TABLE senhas (
                            id INTEGER PRIMARY KEY,
                            titulo TEXT NOT NULL,
                            senha TEXT NOT NULL,
                            usuario TEXT,
                            url TEXT,
                            categoria TEXT,
                            notas TEXT,
                            data_criacao TEXT NOT NULL,
                            data_modificacao TEXT
                        )
                        """)
                        
                        # Transferir dados da tabela antiga para a nova (apenas colunas existentes)
                        cursor.execute("PRAGMA table_info(senhas_old)")
                        colunas_old = [info[1] for info in cursor.fetchall()]
                        
                        # Colunas em comum entre ambas as tabelas
                        colunas_comuns = list(set(colunas_old) & set(["id", "titulo", "senha", "usuario", "url", "categoria", "notas", "data_criacao", "data_modificacao"]))
                        
                        if colunas_comuns:
                            # Copiar dados preservando as colunas em comum
                            colunas_str = ", ".join(colunas_comuns)
                            cursor.execute(f"INSERT INTO senhas ({colunas_str}) SELECT {colunas_str} FROM senhas_old")
                        
                        # Excluir tabela antiga
                        cursor.execute("DROP TABLE senhas_old")
                        
                    except Exception as e:
                        self.registrar_log("erro", f"Erro ao recriar tabela senhas: {str(e)}")
                else:
                    # Adicionar apenas colunas opcionais (sem NOT NULL)
                    for coluna in colunas_faltando:
                        try:
                            cursor.execute(f"ALTER TABLE senhas ADD COLUMN {coluna} TEXT")
                        except Exception as e:
                            self.registrar_log("erro", f"Erro ao adicionar coluna {coluna}: {str(e)}")
                            pass
                
                conn.commit()
            
            conn.close()
            return True
            
        except Exception as e:
            self.registrar_log("erro", f"Erro ao verificar estrutura do banco de dados: {str(e)}")
            return False
    
    def carregar_configuracoes(self):
        """Carrega as configurações do sistema."""
        try:
            if os.path.exists(self.caminho_config):
                with open(self.caminho_config, 'r') as f:
                    configuracoes = json.load(f)
                    # Atualizar configurações existentes
                    for chave, valor in configuracoes.items():
                        self.config[chave] = valor
            else:
                # Criar arquivo de configuração padrão
                self.salvar_configuracoes()
                
            # Registrar log
            self.registrar_log("sistema", "Configurações carregadas")
            
        except Exception as e:
            self.registrar_log("erro", f"Erro ao carregar configurações: {str(e)}")
    
    def salvar_configuracoes(self):
        """Salva as configurações atuais no arquivo de configuração."""
        try:
            with open(self.caminho_config, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            # Registrar log
            self.registrar_log("sistema", "Configurações salvas")
            return True, "Configurações salvas com sucesso"
        
        except Exception as e:
            self.registrar_log("erro", f"Erro ao salvar configurações: {str(e)}")
            return False, f"Erro ao salvar configurações: {str(e)}"
    
    def verificar_modo_heranca(self):
        """Verifica se o modo de herança deve ser ativado."""
        try:
            # Obter data da última confirmação
            ultima_confirmacao_str = self.config.get("ultima_confirmacao")
            
            if not ultima_confirmacao_str:
                self.modo_heranca_ativo = False
                return False
            
            # Converter string para objeto datetime
            ultima_confirmacao = datetime.datetime.fromisoformat(ultima_confirmacao_str)
            
            # Calcular diferença de tempo
            agora = datetime.datetime.now()
            diferenca = agora - ultima_confirmacao
            
            # Verificar se passou o intervalo de confirmação
            intervalo_dias = self.config.get("intervalo_confirmacao", 90)
            
            if diferenca.days >= intervalo_dias:
                # Ativar modo de herança
                self.modo_heranca_ativo = True
                self.registrar_log("sistema", "Modo de herança ativado")
                return True
            else:
                # Modo normal
                self.modo_heranca_ativo = False
                return False
                
        except Exception as e:
            self.registrar_log("erro", f"Erro ao verificar modo de herança: {str(e)}")
            return False
    
    def dias_restantes_confirmacao(self):
        """Calcula o número de dias restantes até a próxima confirmação."""
        try:
            # Obter data da última confirmação
            ultima_confirmacao_str = self.config.get("ultima_confirmacao")
            
            if not ultima_confirmacao_str:
                return 0
            
            # Converter string para objeto datetime
            ultima_confirmacao = datetime.datetime.fromisoformat(ultima_confirmacao_str)
            
            # Calcular data limite
            intervalo_dias = self.config.get("intervalo_confirmacao", 90)
            data_limite = ultima_confirmacao + datetime.timedelta(days=intervalo_dias)
            
            # Calcular dias restantes
            agora = datetime.datetime.now()
            dias_restantes = (data_limite - agora).days
            
            return max(0, dias_restantes)
            
        except Exception as e:
            self.registrar_log("erro", f"Erro ao calcular dias restantes: {str(e)}")
            return 0
    
    def renovar_periodo(self):
        """Renova o período de confirmação."""
        try:
            # Atualizar data da última confirmação
            self.config["ultima_confirmacao"] = datetime.datetime.now().isoformat()
            
            # Desativar modo de herança
            self.modo_heranca_ativo = False
            
            # Salvar configurações
            self.salvar_configuracoes()
            
            # Registrar log
            self.registrar_log("sistema", "Período renovado")
            
            return True, "Período renovado com sucesso"
            
        except Exception as e:
            self.registrar_log("erro", f"Erro ao renovar período: {str(e)}")
            return False, f"Erro ao renovar período: {str(e)}"
    
    def configurar_usuario(self, nome, senha, senha_heranca, email=None):
        """Configura o usuário principal do sistema."""
        try:
            # Verificar se já existe um usuário
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            count = cursor.fetchone()[0]
            
            if count > 0:
                conn.close()
                return False, "Já existe um usuário configurado"
            
            # Criar hash da senha principal
            hash_senha, salt = self.crypto.hash_senha(senha)
            
            # Criar hash da senha de herança
            hash_senha_heranca, salt_heranca = self.crypto.hash_senha(senha_heranca)
            
            # Gerar seed para backup
            seed_hex = None
            frase_mnemonica = None
            
            try:
                # Gerar entropia aleatória (128 bits = 16 bytes = frase de 12 palavras)
                frase_mnemonica = self.bip39.gerar_frase(12)
                
                # Gerar seed a partir da frase (com senha vazia como passphrase)
                seed = self.bip39.gerar_seed_from_frase(frase_mnemonica, "")
                seed_hex = seed.hex()
                
                # Registrar log
                self.registrar_log("sistema", "Frase mnemônica gerada com sucesso")
            except Exception as e:
                self.registrar_log("erro", f"Erro ao gerar frase mnemônica: {str(e)}")
            
            # Inserir usuário
            cursor.execute(
                "INSERT INTO usuarios (nome, hash_senha, salt, hash_senha_heranca, salt_heranca, data_criacao, seed_hex, email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (nome, hash_senha, salt, hash_senha_heranca, salt_heranca, datetime.datetime.now().isoformat(), seed_hex, email)
            )
            
            conn.commit()
            conn.close()
            
            self.registrar_log("sistema", f"Usuário {nome} configurado com sucesso")
            
            # Retornar a frase mnemônica para exibição ao usuário
            if frase_mnemonica:
                return True, "Usuário configurado com sucesso", frase_mnemonica
            else:
                return True, "Usuário configurado com sucesso", None
                
        except Exception as e:
            self.registrar_log("erro", f"Erro ao configurar usuário: {str(e)}")
            return False, f"Erro ao configurar usuário: {str(e)}", None
    
    def autenticar(self, senha):
        """Autentica o usuário no sistema."""
        try:
            # Obter dados do usuário
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, nome, hash_senha, salt, hash_senha_heranca, salt_heranca FROM usuarios LIMIT 1")
            resultado = cursor.fetchone()
            
            if not resultado:
                self.tentativas_senha += 1
                self.registrar_log("autenticacao", "Tentativa de autenticação falhou: usuário não encontrado")
                return False, "Usuário não encontrado", False
            
            id_usuario, nome, hash_senha, salt, hash_senha_heranca, salt_heranca = resultado
            
            # Verificar senha principal
            hash_verificacao, _ = self.crypto.hash_senha(senha, salt)
            senha_principal_correta = hash_verificacao == hash_senha
            
            # Verificar senha de herança
            hash_verificacao_heranca, _ = self.crypto.hash_senha(senha, salt_heranca)
            senha_heranca_correta = hash_verificacao_heranca == hash_senha_heranca
            
            if senha_principal_correta:
                # Senha principal correta
                self.usuario_autenticado = True
                self.usuario_atual = {"id": id_usuario, "nome": nome}
                self.registrar_log("autenticacao", f"Usuário {nome} autenticado com sucesso")
                
                # Gerar chave para o compartimento principal
                chave, _ = self.crypto.gerar_chave_derivada(senha, salt.encode() if isinstance(salt, str) else salt)
                self.chave_compartimento_ativo = chave
                
                # Verificar modo de herança
                modo_heranca = self.verificar_modo_heranca()
                
                return True, "Autenticação bem-sucedida", modo_heranca
                
            elif senha_heranca_correta:
                # Senha de herança correta - modo de herança ativado
                self.usuario_autenticado = True
                self.usuario_atual = {"id": id_usuario, "nome": nome}
                self.modo_heranca_ativo = True
                self.registrar_log("autenticacao", f"Usuário {nome} autenticado com senha de herança")
                
                # Gerar chave para o compartimento principal
                chave, _ = self.crypto.gerar_chave_derivada(senha, salt_heranca.encode() if isinstance(salt_heranca, str) else salt_heranca)
                self.chave_compartimento_ativo = chave
                
                return True, "Autenticação com senha de herança bem-sucedida", True
            
            else:
                # Senha incorreta
                self.tentativas_senha += 1
                self.registrar_log("autenticacao", f"Tentativa de autenticação falhou: senha incorreta ({self.tentativas_senha})")
                
                return False, "Senha incorreta", False
                
        except Exception as e:
            self.registrar_log("erro", f"Erro ao autenticar: {str(e)}")
            return False, f"Erro ao autenticar: {str(e)}", False
    
    def autenticar_por_frase(self, frase):
        """Autentica o usuário usando a frase mnemônica."""
        try:
            # Validar a frase primeiro
            valida, mensagem, _ = self.bip39.validar_frase(frase)
            
            if not valida:
                return False, mensagem, False
            
            # Obter dados do usuário
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, nome, seed_hex FROM usuarios LIMIT 1")
            resultado = cursor.fetchone()
            
            if not resultado:
                self.registrar_log("autenticacao", "Tentativa de autenticação com frase falhou: usuário não encontrado")
                return False, "Usuário não encontrado", False
            
            id_usuario, nome, seed_hex = resultado
            
            if not seed_hex:
                self.registrar_log("autenticacao", "Tentativa de autenticação com frase falhou: seed não configurada")
                return False, "Usuário não possui seed configurada", False
            
            # Gerar seed a partir da frase informada
            seed = self.bip39.gerar_seed_from_frase(frase, "")
            seed_verificacao = seed.hex()
            
            if seed_verificacao == seed_hex:
                # Seed correta
                self.usuario_autenticado = True
                self.usuario_atual = {"id": id_usuario, "nome": nome}
                self.registrar_log("autenticacao", f"Usuário {nome} autenticado com frase mnemônica")
                
                # Gerar chave para o compartimento principal
                chave, _ = self.crypto.gerar_chave_derivada(frase, seed[:16])
                self.chave_compartimento_ativo = chave
                
                # Ativar modo de recuperação (somente leitura)
                self.modo_heranca_ativo = True
                
                return True, "Autenticação com frase mnemônica bem-sucedida", True
            
            else:
                # Frase incorreta
                self.registrar_log("autenticacao", "Tentativa de autenticação com frase falhou: frase incorreta")
                return False, "Frase mnemônica incorreta", False
                
        except Exception as e:
            self.registrar_log("erro", f"Erro ao autenticar com frase: {str(e)}")
            return False, f"Erro ao autenticar com frase: {str(e)}", False
    
    def registrar_log(self, tipo, mensagem):
        """Registra uma mensagem no log do sistema."""
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO logs (tipo, mensagem, data) VALUES (?, ?, ?)",
                (tipo, mensagem, datetime.datetime.now().isoformat())
            )
            
            conn.commit()
            conn.close()
            
        except Exception:
            # Falha silenciosa - não podemos registrar o erro de registro :)
            pass
    
    def obter_estatisticas(self):
        """Obtém estatísticas do uso do sistema no compartimento atual."""
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Definir as tabelas com base no compartimento ativo
            tabela_senhas = "senhas"
            tabela_notas = "notas"
            tabela_arquivos = "arquivos"
            tabela_carteiras = "carteiras_btc"
            
            if self.compartimento_ativo != "principal":
                tabela_senhas = f"compartimento_{self.compartimento_ativo}_senhas"
                tabela_notas = f"compartimento_{self.compartimento_ativo}_notas"
                tabela_arquivos = f"compartimento_{self.compartimento_ativo}_arquivos"
                tabela_carteiras = f"compartimento_{self.compartimento_ativo}_carteiras_btc"
            
            # Contar senhas - verifica se a tabela existe primeiro
            count_senhas = 0
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela_senhas}")
                count_senhas = cursor.fetchone()[0]
            except:
                # A tabela pode não existir ainda
                pass
            
            # Contar notas - verifica se a tabela existe primeiro
            count_notas = 0
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela_notas}")
                count_notas = cursor.fetchone()[0]
            except:
                # A tabela pode não existir ainda
                pass
            
            # Contar arquivos - verifica se a tabela existe primeiro
            count_arquivos = 0
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela_arquivos}")
                count_arquivos = cursor.fetchone()[0]
            except:
                # A tabela pode não existir ainda
                pass
            
            # Contar carteiras BTC - verifica se a tabela existe primeiro
            count_carteiras = 0
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela_carteiras}")
                count_carteiras = cursor.fetchone()[0]
            except:
                # A tabela pode não existir ainda
                pass
            
            conn.close()
            
            return {
                "senhas": count_senhas,
                "notas": count_notas,
                "arquivos": count_arquivos,
                "carteiras_btc": count_carteiras
            }
            
        except Exception as e:
            self.registrar_log("erro", f"Erro ao obter estatísticas: {str(e)}")
            return {"senhas": 0, "notas": 0, "arquivos": 0, "carteiras_btc": 0}
    
    def criar_compartimento(self, nome, senha, descricao=None):
        """Cria um novo compartimento seguro."""
        try:
            if not self.usuario_autenticado:
                return False, "Usuário não autenticado", None
            
            if self.modo_heranca_ativo:
                return False, "Não é possível criar compartimentos no modo de herança", None
            
            # Gerar ID único para o compartimento
            compartimento_id = self.crypto.gerar_id_seguro(16)
            
            # Gerar chave aleatória para o compartimento
            chave_comp = secrets.token_bytes(32)
            
            # Criptografar a chave do compartimento com a senha fornecida
            chave_derivada, salt = self.crypto.gerar_chave_derivada(senha)
            chave_criptografada_base64, iv_base64 = self.crypto.criptografar(chave_comp, chave_derivada)
            
            # Preparar frase de recuperação (usando BIP39)
            # Converter a chave do compartimento em frase mnemônica
            try:
                # Usar apenas os primeiros 16 bytes (128 bits) para uma frase de 12 palavras
                from mnemonic import Mnemonic
                mnemo = Mnemonic("english")
                # Usar os primeiros 16 bytes da chave do compartimento
                frase_recuperacao = mnemo.to_mnemonic(chave_comp[:16])
            except:
                # Fallback se não conseguir usar a biblioteca
                frase_recuperacao = base64.b64encode(chave_comp).decode()
            
            # Inserir informações do compartimento no banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO compartimentos (nome, compartimento_id, chave_criptografada, iv, descricao, data_criacao) VALUES (?, ?, ?, ?, ?, ?)",
                (nome, compartimento_id, chave_criptografada_base64, iv_base64, descricao, datetime.datetime.now().isoformat())
            )
            
            conn.commit()
            conn.close()
            
            self.registrar_log("compartimento", f"Compartimento '{nome}' criado com sucesso")
            
            return True, f"Compartimento '{nome}' criado com sucesso", frase_recuperacao
            
        except Exception as e:
            self.registrar_log("erro", f"Erro ao criar compartimento: {str(e)}")
            return False, f"Erro ao criar compartimento: {str(e)}", None
    
    def listar_compartimentos(self):
        """Lista os compartimentos disponíveis."""
        try:
            if not self.usuario_autenticado:
                return False, "Usuário não autenticado", None
            
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, nome, compartimento_id, descricao, data_criacao FROM compartimentos")
            compartimentos = []
            
            for row in cursor.fetchall():
                id_comp, nome, comp_id, descricao, data_criacao = row
                compartimentos.append({
                    "id": id_comp,
                    "nome": nome,
                    "compartimento_id": comp_id,
                    "descricao": descricao,
                    "data_criacao": data_criacao
                })
            
            conn.close()
            
            return True, "Compartimentos listados com sucesso", compartimentos
            
        except Exception as e:
            self.registrar_log("erro", f"Erro ao listar compartimentos: {str(e)}")
            return False, f"Erro ao listar compartimentos: {str(e)}", None
    
    def alternar_compartimento(self, compartimento_id, senha):
        """Alterna para um compartimento específico."""
        try:
            if not self.usuario_autenticado:
                return False, "Usuário não autenticado"
            
            if self.modo_heranca_ativo:
                return False, "Não é possível alternar compartimentos no modo de herança"
            
            # Buscar informações do compartimento
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT nome, chave_criptografada, iv FROM compartimentos WHERE compartimento_id = ?",
                (compartimento_id,)
            )
            
            resultado = cursor.fetchone()
            conn.close()
            
            if not resultado:
                return False, "Compartimento não encontrado"
            
            nome, chave_criptografada, iv = resultado
            
            # Derivar a chave a partir da senha
            chave_derivada, _ = self.crypto.gerar_chave_derivada(senha)
            
            try:
                # Descriptografar a chave do compartimento
                chave_comp = self.crypto.descriptografar(chave_criptografada, iv, chave_derivada)
                
                # Se chegou aqui, a chave foi descriptografada com sucesso
                self.compartimento_ativo = compartimento_id
                self.chave_compartimento_ativo = chave_comp
                
                self.registrar_log("compartimento", f"Alternado para compartimento '{nome}'")
                
                return True, f"Compartimento '{nome}' ativado com sucesso"
                
            except:
                return False, "Senha incorreta para este compartimento"
            
        except Exception as e:
            self.registrar_log("erro", f"Erro ao alternar compartimento: {str(e)}")
            return False, f"Erro ao alternar compartimento: {str(e)}"
    
    # === Funções de gerenciamento de senhas ===
    
    def listar_senhas(self):
        """Lista as senhas do compartimento atual."""
        self._verifica_autenticacao()
        
        # Definir a tabela correta com base no compartimento ativo
        tabela = "senhas"
        if self.compartimento_ativo != "principal":
            tabela = f"compartimento_{self.compartimento_ativo}_senhas"
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Executar consulta
            cursor.execute(
                f"SELECT * FROM {tabela} ORDER BY titulo"
            )
            
            # Converter para lista de dicionários
            colunas = [coluna[0] for coluna in cursor.description]
            resultado = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
            
            # Fechar conexão
            conn.close()
            
            return resultado
            
        except Exception as e:
            self.registrar_log("erro", f"Erro ao listar senhas: {str(e)}")
            return []
    
    def obter_senha(self, senha_id):
        """Obtém os detalhes de uma senha específica."""
        self._verifica_autenticacao()
        
        # Definir a tabela correta com base no compartimento ativo
        tabela = "senhas"
        if self.compartimento_ativo != "principal":
            tabela = f"compartimento_{self.compartimento_ativo}_senhas"
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Executar consulta
            cursor.execute(
                f"SELECT * FROM {tabela} WHERE id = ?",
                (senha_id,)
            )
            
            # Obter resultado
            resultado = cursor.fetchone()
            
            if not resultado:
                conn.close()
                raise Exception("Senha não encontrada")
            
            # Converter para dicionário
            colunas = [coluna[0] for coluna in cursor.description]
            senha = dict(zip(colunas, resultado))
            
            # Fechar conexão
            conn.close()
            
            return senha
            
        except Exception as e:
            self.registrar_log("erro", f"Erro ao obter senha: {str(e)}")
            raise e
    
    def adicionar_senha(self, titulo, senha, usuario=None, url=None, categoria=None, notas=None):
        """Adiciona uma nova senha ao sistema."""
        self._verifica_autenticacao()
        
        # Verificar modo de herança
        if self.modo_heranca_ativo:
            return False, "Não é possível adicionar senhas no modo de herança"
        
        # Definir a tabela correta com base no compartimento ativo
        tabela = "senhas"
        if self.compartimento_ativo != "principal":
            tabela = f"compartimento_{self.compartimento_ativo}_senhas"
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Data atual
            data_criacao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Inserir senha
            cursor.execute(
                f"""
                INSERT INTO {tabela} 
                (titulo, senha, usuario, url, categoria, notas, data_criacao) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (titulo, senha, usuario, url, categoria, notas, data_criacao)
            )
            
            # Salvar alterações
            conn.commit()
            conn.close()
            
            # Registrar log
            self.registrar_log("sistema", f"Senha '{titulo}' adicionada ao compartimento '{self.compartimento_ativo}'")
            
            return True, "Senha adicionada com sucesso"
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            self.registrar_log("erro", f"Erro ao adicionar senha: {str(e)}")
            return False, f"Erro ao adicionar senha: {str(e)}"
    
    def atualizar_senha(self, senha_id, titulo=None, senha=None, usuario=None, url=None, categoria=None, notas=None):
        """Atualiza uma senha existente."""
        self._verifica_autenticacao()
        
        # Verificar modo de herança
        if self.modo_heranca_ativo:
            return False, "Não é possível atualizar senhas no modo de herança"
        
        # Definir a tabela correta com base no compartimento ativo
        tabela = "senhas"
        if self.compartimento_ativo != "principal":
            tabela = f"compartimento_{self.compartimento_ativo}_senhas"
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Verificar se a senha existe
            cursor.execute(
                f"SELECT titulo FROM {tabela} WHERE id = ?",
                (senha_id,)
            )
            
            resultado = cursor.fetchone()
            if not resultado:
                conn.close()
                return False, "Senha não encontrada"
            
            titulo_original = resultado[0]
            
            # Criar conjunto de campos a atualizar
            campos = []
            valores = []
            
            if titulo is not None:
                campos.append("titulo = ?")
                valores.append(titulo)
            
            if senha is not None:
                campos.append("senha = ?")
                valores.append(senha)
            
            if usuario is not None:
                campos.append("usuario = ?")
                valores.append(usuario)
            
            if url is not None:
                campos.append("url = ?")
                valores.append(url)
            
            if categoria is not None:
                campos.append("categoria = ?")
                valores.append(categoria)
            
            if notas is not None:
                campos.append("notas = ?")
                valores.append(notas)
            
            # Se não há campos para atualizar
            if not campos:
                conn.close()
                return True, "Nenhum campo para atualizar"
            
            # Atualizar senha
            cursor.execute(
                f"""
                UPDATE {tabela} 
                SET {", ".join(campos)}
                WHERE id = ?
                """,
                valores + [senha_id]
            )
            
            # Salvar alterações
            conn.commit()
            conn.close()
            
            # Registrar log
            self.registrar_log("sistema", f"Senha '{titulo_original}' atualizada no compartimento '{self.compartimento_ativo}'")
            
            return True, "Senha atualizada com sucesso"
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            self.registrar_log("erro", f"Erro ao atualizar senha: {str(e)}")
            return False, f"Erro ao atualizar senha: {str(e)}"
    
    def excluir_senha(self, senha_id):
        """Exclui uma senha existente."""
        self._verifica_autenticacao()
        
        # Verificar modo de herança
        if self.modo_heranca_ativo:
            return False, "Não é possível excluir senhas no modo de herança"
        
        # Definir a tabela correta com base no compartimento ativo
        tabela = "senhas"
        if self.compartimento_ativo != "principal":
            tabela = f"compartimento_{self.compartimento_ativo}_senhas"
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Verificar se a senha existe
            cursor.execute(
                f"SELECT titulo FROM {tabela} WHERE id = ?",
                (senha_id,)
            )
            
            resultado = cursor.fetchone()
            if not resultado:
                conn.close()
                return False, "Senha não encontrada"
            
            titulo = resultado[0]
            
            # Excluir senha
            cursor.execute(
                f"DELETE FROM {tabela} WHERE id = ?",
                (senha_id,)
            )
            
            # Salvar alterações
            conn.commit()
            conn.close()
            
            # Registrar log
            self.registrar_log("sistema", f"Senha '{titulo}' excluída do compartimento '{self.compartimento_ativo}'")
            
            return True, "Senha excluída com sucesso"
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            self.registrar_log("erro", f"Erro ao excluir senha: {str(e)}")
            return False, f"Erro ao excluir senha: {str(e)}"
    
    def _verifica_autenticacao(self):
        """Verifica se o usuário está autenticado e levanta uma exceção se não estiver."""
        if not self.usuario_autenticado:
            raise Exception("Usuário não autenticado")
        return True 