import sqlite3
import datetime

class BancoDados:
    def __init__(self, caminho_db):
        self.caminho_db = caminho_db
    
    def criar_estrutura(self):
        """Cria a estrutura inicial do banco de dados"""
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
            seed_hex TEXT
        )
        """)
        
        # Tabela de senhas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS senhas (
            id INTEGER PRIMARY KEY,
            titulo TEXT NOT NULL,
            descricao TEXT,
            dados_criptografados TEXT NOT NULL,
            iv TEXT NOT NULL,
            data_criacao TEXT NOT NULL,
            data_modificacao TEXT NOT NULL,
            categoria_id INTEGER,
            compartimento TEXT DEFAULT 'principal',
            FOREIGN KEY (categoria_id) REFERENCES categorias (id)
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
        
        conn.commit()
        conn.close()
    
    def atualizar_estrutura(self):
        """Atualiza a estrutura do banco de dados para incluir novas colunas"""
        conn = sqlite3.connect(self.caminho_db)
        cursor = conn.cursor()
        
        try:
            # Verificar se a coluna categoria_id existe na tabela senhas
            cursor.execute("PRAGMA table_info(senhas)")
            colunas_senhas = [info[1] for info in cursor.fetchall()]
            
            if 'categoria_id' not in colunas_senhas:
                # Adicionar a coluna categoria_id à tabela senhas
                cursor.execute("ALTER TABLE senhas ADD COLUMN categoria_id INTEGER")
                self.registrar_log("sistema", "Adicionada coluna categoria_id à tabela senhas")
            
            # Verificar se a coluna categoria_id existe na tabela notas
            cursor.execute("PRAGMA table_info(notas)")
            colunas_notas = [info[1] for info in cursor.fetchall()]
            
            if 'categoria_id' not in colunas_notas:
                # Adicionar a coluna categoria_id à tabela notas
                cursor.execute("ALTER TABLE notas ADD COLUMN categoria_id INTEGER")
                self.registrar_log("sistema", "Adicionada coluna categoria_id à tabela notas")
            
            # Verificar se a coluna dados_criptografados existe na tabela notas
            if 'dados_criptografados' in colunas_notas and 'conteudo_criptografado' not in colunas_notas:
                # Renomear a coluna dados_criptografados para conteudo_criptografado
                # SQLite não suporta ALTER TABLE RENAME COLUMN, então precisamos criar uma nova tabela
                cursor.execute("""
                CREATE TABLE notas_new (
                    id INTEGER PRIMARY KEY,
                    titulo TEXT NOT NULL,
                    conteudo_criptografado TEXT NOT NULL,
                    iv TEXT NOT NULL,
                    data_criacao TEXT NOT NULL,
                    data_modificacao TEXT NOT NULL,
                    categoria_id INTEGER,
                    FOREIGN KEY (categoria_id) REFERENCES categorias (id)
                )
                """)
                
                # Copiar dados da tabela antiga para a nova
                cursor.execute("""
                INSERT INTO notas_new (id, titulo, conteudo_criptografado, iv, data_criacao, data_modificacao, categoria_id)
                SELECT id, titulo, dados_criptografados, iv, data_criacao, data_modificacao, categoria_id FROM notas
                """)
                
                # Excluir tabela antiga
                cursor.execute("DROP TABLE notas")
                
                # Renomear a nova tabela
                cursor.execute("ALTER TABLE notas_new RENAME TO notas")
                
                self.registrar_log("sistema", "Renomeada coluna dados_criptografados para conteudo_criptografado na tabela notas")
            
            # Verificar se a coluna categoria_id existe na tabela arquivos
            cursor.execute("PRAGMA table_info(arquivos)")
            colunas_arquivos = [info[1] for info in cursor.fetchall()]
            
            if 'categoria_id' not in colunas_arquivos:
                # Adicionar a coluna categoria_id à tabela arquivos
                cursor.execute("ALTER TABLE arquivos ADD COLUMN categoria_id INTEGER")
                self.registrar_log("sistema", "Adicionada coluna categoria_id à tabela arquivos")
            
            # Verificar se a coluna seed_hex existe na tabela usuarios
            cursor.execute("PRAGMA table_info(usuarios)")
            colunas_usuarios = [info[1] for info in cursor.fetchall()]
            
            if 'seed_hex' not in colunas_usuarios:
                # Adicionar a coluna seed_hex à tabela usuarios
                cursor.execute("ALTER TABLE usuarios ADD COLUMN seed_hex TEXT")
                self.registrar_log("sistema", "Adicionada coluna seed_hex à tabela usuarios")
            
            # Verificar se a coluna compartimento existe na tabela senhas
            if 'compartimento' not in colunas_senhas:
                cursor.execute("ALTER TABLE senhas ADD COLUMN compartimento TEXT DEFAULT 'principal'")
                self.registrar_log("sistema", "Adicionada coluna compartimento à tabela senhas")
            
            # Verificar se a coluna compartimento existe na tabela notas
            if 'compartimento' not in colunas_notas:
                cursor.execute("ALTER TABLE notas ADD COLUMN compartimento TEXT DEFAULT 'principal'")
                self.registrar_log("sistema", "Adicionada coluna compartimento à tabela notas")
            
            # Verificar se a coluna compartimento existe na tabela arquivos
            if 'compartimento' not in colunas_arquivos:
                cursor.execute("ALTER TABLE arquivos ADD COLUMN compartimento TEXT DEFAULT 'principal'")
                self.registrar_log("sistema", "Adicionada coluna compartimento à tabela arquivos")
            
            conn.commit()
        except Exception as e:
            print(f"Erro ao atualizar estrutura do banco de dados: {str(e)}")
        finally:
            conn.close()
    
    def registrar_log(self, tipo, descricao):
        """Registra um evento no log do sistema"""
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            # Verificar se a tabela logs existe e tem a estrutura correta
            cursor.execute("PRAGMA table_info(logs)")
            colunas = cursor.fetchall()
            
            data_hora = datetime.datetime.now().isoformat()
            
            # Verificar quais colunas existem e usar os nomes corretos
            if any(col[1] == 'tipo_evento' for col in colunas):
                cursor.execute(
                    "INSERT INTO logs (tipo_evento, descricao, data_hora) VALUES (?, ?, ?)",
                    (tipo, descricao, data_hora)
                )
            else:
                cursor.execute(
                    "INSERT INTO logs (tipo, mensagem, data) VALUES (?, ?, ?)",
                    (tipo, descricao, data_hora)
                )
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erro ao registrar log: {str(e)}")
    
    def verificar_usuario_existente(self):
        """Verifica se já existe um usuário configurado"""
        conn = sqlite3.connect(self.caminho_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count > 0
    
    def criar_usuario(self, nome, hash_senha, salt, hash_senha_heranca, salt_heranca, seed_hex=None):
        """Cria um novo usuário no sistema"""
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            data_criacao = datetime.datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO usuarios (nome, hash_senha, salt, hash_senha_heranca, salt_heranca, data_criacao, seed_hex) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (nome, hash_senha, salt, hash_senha_heranca, salt_heranca, data_criacao, seed_hex)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao criar usuário: {str(e)}")
            return False
    
    def obter_usuario(self):
        """Obtém os dados do usuário"""
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, hash_senha, salt, hash_senha_heranca, salt_heranca, seed_hex FROM usuarios LIMIT 1")
            resultado = cursor.fetchone()
            
            conn.close()
            return resultado
        except Exception as e:
            print(f"Erro ao obter usuário: {str(e)}")
            return None
    
    def apagar_dados_sensiveis(self):
        """Apaga todos os dados sensíveis do banco de dados"""
        conn = sqlite3.connect(self.caminho_db)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM senhas")
        cursor.execute("DELETE FROM notas")
        cursor.execute("DELETE FROM arquivos")
        
        conn.commit()
        conn.close()
    
    def obter_arquivos_para_exclusao(self):
        """Obtém a lista de nomes de arquivos criptografados para exclusão"""
        conn = sqlite3.connect(self.caminho_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT nome_criptografado FROM arquivos")
        arquivos = [arquivo[0] for arquivo in cursor.fetchall()]
        
        conn.close()
        return arquivos
    
    def atualizar_seed_usuario(self, seed_hex):
        """Atualiza o seed do usuário"""
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            cursor.execute("UPDATE usuarios SET seed_hex = ? WHERE id = 1", (seed_hex,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao atualizar seed do usuário: {str(e)}")
            return False
    
    def obter_seed_usuario(self):
        """Obtém o seed do usuário"""
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT seed_hex FROM usuarios LIMIT 1")
            resultado = cursor.fetchone()
            
            conn.close()
            
            if resultado and resultado[0]:
                return resultado[0]
            else:
                return None
        except Exception as e:
            print(f"Erro ao obter seed do usuário: {str(e)}")
            return None
    
    def atualizar_senha_usuario(self, hash_senha, salt):
        """Atualiza a senha do usuário"""
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            cursor.execute("UPDATE usuarios SET hash_senha = ?, salt = ? WHERE id = 1", (hash_senha, salt))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao atualizar senha do usuário: {str(e)}")
            return False
    
    def criar_compartimento(self, nome, compartimento_id, chave_criptografada, iv, descricao, data_criacao):
        """Cria um novo compartimento de dados"""
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO compartimentos (nome, compartimento_id, chave_criptografada, iv, descricao, data_criacao) VALUES (?, ?, ?, ?, ?, ?)",
                (nome, compartimento_id, chave_criptografada, iv, descricao, data_criacao)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao criar compartimento: {str(e)}")
            return False
    
    def obter_compartimento_por_id(self, compartimento_id):
        """Obtém um compartimento pelo ID"""
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, nome, compartimento_id, chave_criptografada, iv, descricao, data_criacao FROM compartimentos WHERE compartimento_id = ?",
                (compartimento_id,)
            )
            resultado = cursor.fetchone()
            
            conn.close()
            
            if resultado:
                id_comp, nome, comp_id, chave_criptografada, iv, descricao, data_criacao = resultado
                return {
                    "id": id_comp,
                    "nome": nome,
                    "compartimento_id": comp_id,
                    "chave_criptografada": chave_criptografada,
                    "iv": iv,
                    "descricao": descricao,
                    "data_criacao": data_criacao
                }
            else:
                return None
        except Exception as e:
            print(f"Erro ao obter compartimento por ID: {str(e)}")
            return None
    
    def obter_compartimento_por_nome(self, nome):
        """Obtém um compartimento pelo nome"""
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, nome, compartimento_id, chave_criptografada, iv, descricao, data_criacao FROM compartimentos WHERE nome = ?",
                (nome,)
            )
            resultado = cursor.fetchone()
            
            conn.close()
            
            if resultado:
                id_comp, nome, comp_id, chave_criptografada, iv, descricao, data_criacao = resultado
                return {
                    "id": id_comp,
                    "nome": nome,
                    "compartimento_id": comp_id,
                    "chave_criptografada": chave_criptografada,
                    "iv": iv,
                    "descricao": descricao,
                    "data_criacao": data_criacao
                }
            else:
                return None
        except Exception as e:
            print(f"Erro ao obter compartimento por nome: {str(e)}")
            return None
    
    def obter_todos_compartimentos(self):
        """Obtém todos os compartimentos"""
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, nome, compartimento_id, descricao, data_criacao FROM compartimentos ORDER BY nome"
            )
            resultados = cursor.fetchall()
            
            conn.close()
            
            compartimentos = []
            for id_comp, nome, comp_id, descricao, data_criacao in resultados:
                compartimentos.append({
                    "id": id_comp,
                    "nome": nome,
                    "compartimento_id": comp_id,
                    "descricao": descricao,
                    "data_criacao": data_criacao
                })
            
            return compartimentos
        except Exception as e:
            print(f"Erro ao obter todos os compartimentos: {str(e)}")
            return []
    
    def obter_senhas(self, compartimento="principal", filtro=None, categoria_id=None):
        """Obtém todas as senhas armazenadas"""
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            query = "SELECT id, titulo, descricao, dados_criptografados, iv, data_criacao, data_modificacao, categoria_id FROM senhas WHERE compartimento = ?"
            params = [compartimento]
            
            if filtro:
                query += " AND (titulo LIKE ? OR descricao LIKE ?)"
                params.extend([f"%{filtro}%", f"%{filtro}%"])
            
            if categoria_id:
                query += " AND categoria_id = ?"
                params.append(categoria_id)
            
            query += " ORDER BY titulo"
            
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            
            conn.close()
            
            senhas = []
            for id_senha, titulo, descricao, dados_criptografados, iv, data_criacao, data_modificacao, categoria_id in resultados:
                senhas.append({
                    "id": id_senha,
                    "titulo": titulo,
                    "descricao": descricao,
                    "dados_criptografados": dados_criptografados,
                    "iv": iv,
                    "data_criacao": data_criacao,
                    "data_modificacao": data_modificacao,
                    "categoria_id": categoria_id
                })
            
            return senhas
        except Exception as e:
            print(f"Erro ao obter senhas: {str(e)}")
            return []
    
    def obter_notas(self, compartimento="principal", filtro=None, categoria_id=None):
        """Obtém todas as notas armazenadas"""
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            query = "SELECT id, titulo, conteudo_criptografado, iv, data_criacao, data_modificacao, categoria_id, compartimento FROM notas WHERE compartimento = ?"
            params = [compartimento]
            
            if filtro:
                query += " AND (titulo LIKE ?)"
                params.append(f"%{filtro}%")
            
            if categoria_id:
                query += " AND categoria_id = ?"
                params.append(categoria_id)
            
            query += " ORDER BY titulo"
            
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            
            conn.close()
            
            notas = []
            for id_nota, titulo, conteudo_criptografado, iv, data_criacao, data_modificacao, categoria_id, compartimento in resultados:
                notas.append({
                    "id": id_nota,
                    "titulo": titulo,
                    "conteudo_criptografado": conteudo_criptografado,
                    "iv": iv,
                    "data_criacao": data_criacao,
                    "data_modificacao": data_modificacao,
                    "categoria_id": categoria_id,
                    "compartimento": compartimento
                })
            
            return notas
        except Exception as e:
            print(f"Erro ao obter notas: {str(e)}")
            return []
    
    def obter_arquivos(self, compartimento="principal", filtro=None, categoria_id=None):
        """Obtém todos os arquivos armazenados"""
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            query = "SELECT id, nome_original, nome_criptografado, descricao, iv, data_upload, categoria_id FROM arquivos WHERE compartimento = ?"
            params = [compartimento]
            
            if filtro:
                query += " AND (nome_original LIKE ? OR descricao LIKE ?)"
                params.extend([f"%{filtro}%", f"%{filtro}%"])
            
            if categoria_id:
                query += " AND categoria_id = ?"
                params.append(categoria_id)
            
            query += " ORDER BY nome_original"
            
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            
            conn.close()
            
            arquivos = []
            for id_arquivo, nome_original, nome_criptografado, descricao, iv, data_upload, categoria_id in resultados:
                arquivos.append({
                    "id": id_arquivo,
                    "nome_original": nome_original,
                    "nome_criptografado": nome_criptografado,
                    "descricao": descricao,
                    "iv": iv,
                    "data_upload": data_upload,
                    "categoria_id": categoria_id
                })
            
            return arquivos
        except Exception as e:
            print(f"Erro ao obter arquivos: {str(e)}")
            return []
    
    def adicionar_nota(self, titulo, conteudo_criptografado, iv, data_criacao, data_modificacao, categoria_id=None, compartimento="principal"):
        """Adiciona uma nova nota"""
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO notas (titulo, conteudo_criptografado, iv, data_criacao, data_modificacao, categoria_id, compartimento) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (titulo, conteudo_criptografado, iv, data_criacao, data_modificacao, categoria_id, compartimento)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao adicionar nota: {str(e)}")
            return False
    
    def obter_nota_por_id(self, id_nota):
        """Obtém uma nota pelo ID"""
        try:
            conn = sqlite3.connect(self.caminho_db)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, titulo, conteudo_criptografado, iv, data_criacao, data_modificacao, categoria_id, compartimento FROM notas WHERE id = ?",
                (id_nota,)
            )
            resultado = cursor.fetchone()
            
            conn.close()
            
            if resultado:
                id_nota, titulo, conteudo_criptografado, iv, data_criacao, data_modificacao, categoria_id, compartimento = resultado
                return {
                    "id": id_nota,
                    "titulo": titulo,
                    "conteudo_criptografado": conteudo_criptografado,
                    "iv": iv,
                    "data_criacao": data_criacao,
                    "data_modificacao": data_modificacao,
                    "categoria_id": categoria_id,
                    "compartimento": compartimento
                }
            else:
                return None
        except Exception as e:
            print(f"Erro ao obter nota por ID: {str(e)}")
            return None 