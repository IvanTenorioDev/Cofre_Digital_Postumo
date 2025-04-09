import hashlib
import secrets
import base64
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

class Criptografia:
    def __init__(self):
        pass
    
    def gerar_chave_derivada(self, senha, salt=None):
        """Gera uma chave derivada a partir da senha usando PBKDF2"""
        if salt is None:
            salt = secrets.token_bytes(16)
        
        # Garantir que a senha seja bytes
        if isinstance(senha, str):
            senha = senha.encode('utf-8')
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits para ChaCha20
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        chave = kdf.derive(senha)
        return chave, salt
    
    def hash_senha(self, senha, salt=None):
        """Cria um hash seguro da senha usando SHA-512"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        hash_senha = hashlib.sha512((senha + salt).encode()).hexdigest()
        return hash_senha, salt
    
    def criptografar(self, dados, chave):
        """Criptografa dados usando ChaCha20Poly1305"""
        # Garantir que os dados sejam bytes
        if isinstance(dados, str):
            dados = dados.encode('utf-8')
        
        # Garantir que a chave seja bytes e tenha o tamanho correto
        if isinstance(chave, str):
            chave = chave.encode('utf-8')
        
        # ChaCha20Poly1305 requer uma chave de 32 bytes
        if len(chave) != 32:
            raise ValueError("A chave deve ter 32 bytes")
        
        cipher = ChaCha20Poly1305(chave)
        nonce = secrets.token_bytes(12)  # ChaCha20Poly1305 usa nonce de 12 bytes
        
        # Criptografar os dados
        texto_cifrado = cipher.encrypt(nonce, dados, None)
        
        # Retornar como strings base64 para armazenamento seguro
        return base64.b64encode(texto_cifrado).decode(), base64.b64encode(nonce).decode()
    
    def descriptografar(self, texto_cifrado, nonce, chave):
        """Descriptografa dados usando ChaCha20Poly1305"""
        try:
            # Garantir que a chave seja bytes e tenha o tamanho correto
            if isinstance(chave, str):
                chave = chave.encode('utf-8')
            
            # ChaCha20Poly1305 requer uma chave de 32 bytes
            if len(chave) != 32:
                raise ValueError("A chave deve ter 32 bytes")
            
            # Converter de base64 para bytes
            texto_cifrado_bytes = base64.b64decode(texto_cifrado)
            nonce_bytes = base64.b64decode(nonce)
            
            # Descriptografar os dados
            cipher = ChaCha20Poly1305(chave)
            dados = cipher.decrypt(nonce_bytes, texto_cifrado_bytes, None)
            
            return dados
        except Exception as e:
            print(f"Erro na descriptografia: {str(e)}")
            raise 