import os
import base64
import secrets
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

class CryptoUtils:
    """Utilitários de criptografia para o cofre digital."""
    
    @staticmethod
    def gerar_chave_derivada(senha, salt=None, iterations=100000):
        """
        Gera uma chave segura a partir de uma senha usando PBKDF2.
        
        Args:
            senha (str): A senha para derivar a chave
            salt (bytes, optional): O salt para uso em PBKDF2. Se não for fornecido, um novo será gerado.
            iterations (int): Número de iterações para PBKDF2
            
        Returns:
            tuple: (chave_derivada, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(16)
        
        # Garantir que a senha seja bytes
        if isinstance(senha, str):
            senha = senha.encode('utf-8')
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits para ChaCha20
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        
        chave = kdf.derive(senha)
        return chave, salt
    
    @staticmethod
    def hash_senha(senha, salt=None):
        """
        Cria um hash seguro da senha usando SHA-512.
        
        Args:
            senha (str): A senha a ser hasheada
            salt (str, optional): O salt para o hash. Se não for fornecido, um novo será gerado.
            
        Returns:
            tuple: (hash_senha, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        hash_senha = hashlib.sha512((senha + salt).encode()).hexdigest()
        return hash_senha, salt
    
    @staticmethod
    def criptografar(dados, chave):
        """
        Criptografa dados usando ChaCha20Poly1305.
        
        Args:
            dados (str ou bytes): Os dados a serem criptografados
            chave (bytes): A chave de criptografia (32 bytes)
            
        Returns:
            tuple: (texto_cifrado_base64, nonce_base64)
        """
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
    
    @staticmethod
    def descriptografar(texto_cifrado, nonce, chave):
        """
        Descriptografa dados usando ChaCha20Poly1305.
        
        Args:
            texto_cifrado (str): O texto cifrado em base64
            nonce (str): O nonce em base64
            chave (bytes): A chave de descriptografia
            
        Returns:
            bytes: Os dados descriptografados
        """
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
            raise ValueError(f"Erro na descriptografia: {str(e)}")
    
    @staticmethod
    def gerar_id_seguro(comprimento=16):
        """
        Gera um ID seguro aleatório.
        
        Args:
            comprimento (int): O comprimento do ID em bytes
            
        Returns:
            str: O ID em hexadecimal
        """
        return secrets.token_hex(comprimento) 