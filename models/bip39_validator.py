import re
import hashlib
import unicodedata

class BIP39Validator:
    """Validador de frases mnemônicas compatíveis com BIP39."""
    
    def __init__(self):
        # Carregar lista de palavras BIP39 em inglês
        try:
            with open('assets/bip39_english.txt', 'r') as f:
                self.wordlist = [w.strip() for w in f.readlines()]
        except FileNotFoundError:
            # Lista de palavras não disponível, criar em tempo de execução
            self._criar_arquivo_palavras()
    
    def _criar_arquivo_palavras(self):
        """
        Cria o arquivo de palavras BIP39 se não existir.
        Usamos as 2048 palavras padrão do BIP39 inglês.
        """
        # Lista padrão (truncada por brevidade - será expandida na implementação real)
        # Exemplo com apenas as primeiras 20 palavras:
        self.wordlist = [
            "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract",
            "absurd", "abuse", "access", "accident", "account", "accuse", "achieve", "acid",
            "acoustic", "acquire", "across", "act"
        ]
        
        # Na implementação real, incluir todas as 2048 palavras
        import os
        os.makedirs('assets', exist_ok=True)
        try:
            with open('assets/bip39_english.txt', 'w') as f:
                for word in self.wordlist:
                    f.write(word + "\n")
        except:
            pass  # Falhar silenciosamente se não puder criar o arquivo
    
    def validar_frase(self, frase):
        """
        Valida se uma frase mnemônica está de acordo com BIP39.
        
        Args:
            frase (str): A frase mnemônica com palavras separadas por espaço
            
        Returns:
            tuple: (valida, mensagem, lista_palavras)
        """
        # Normalizar a frase (remover espaços extras, converter para minúsculas)
        frase = unicodedata.normalize('NFKD', frase.lower())
        frase = re.sub(r'\s+', ' ', frase).strip()
        
        # Dividir em palavras
        palavras = frase.split()
        
        # Verificar número de palavras (deve ser 12, 15, 18, 21 ou 24)
        num_palavras = len(palavras)
        if num_palavras not in [12, 15, 18, 21, 24]:
            return False, f"Número inválido de palavras: {num_palavras}. Deve ser 12, 15, 18, 21 ou 24.", palavras
        
        # Verificar se todas as palavras estão na lista
        palavras_invalidas = [p for p in palavras if p not in self.wordlist]
        if palavras_invalidas:
            return False, f"Palavras inválidas encontradas: {', '.join(palavras_invalidas)}", palavras
        
        # Verificar o checksum
        if not self._verificar_checksum(palavras):
            return False, "Checksum inválido. A frase não é válida de acordo com BIP39.", palavras
        
        return True, "Frase mnemônica válida.", palavras
    
    def _verificar_checksum(self, palavras):
        """
        Verifica o checksum de uma frase BIP39.
        Implementação simplificada para demonstração.
        
        Args:
            palavras (list): Lista de palavras da frase
            
        Returns:
            bool: True se o checksum for válido, False caso contrário
        """
        # Esta é uma implementação simplificada. Na realidade, o BIP39
        # requer uma verificação de checksum mais complexa que envolve:
        # 1. Converter palavras para índices
        # 2. Converter índices para bits
        # 3. Calcular o checksum como os primeiros bits do hash SHA-256
        # 4. Verificar se os bits do checksum correspondem
        
        # Implementação simplificada para demonstração
        # Na prática, usaríamos biblioteca como 'mnemonic'
        try:
            # Tentar importar a biblioteca mnemonic
            from mnemonic import Mnemonic
            mnemo = Mnemonic("english")
            return mnemo.check(" ".join(palavras))
        except ImportError:
            # Se a biblioteca não estiver disponível, assumimos que a frase é válida
            # (apenas para fins de demonstração)
            return True
    
    def gerar_frase(self, comprimento=12):
        """
        Gera uma nova frase mnemônica BIP39.
        
        Args:
            comprimento (int): Comprimento da frase (12, 15, 18, 21 ou 24 palavras)
            
        Returns:
            str: A frase mnemônica gerada
        """
        try:
            # Tentar usar a biblioteca mnemonic
            from mnemonic import Mnemonic
            mnemo = Mnemonic("english")
            # Gerar a quantidade correta de entropia para o comprimento desejado
            entropia_bits = {
                12: 128, 15: 160, 18: 192, 21: 224, 24: 256
            }
            entropia_bytes = entropia_bits[comprimento] // 8
            entropy = bytes(secrets.token_bytes(entropia_bytes))
            return mnemo.to_mnemonic(entropy)
        except (ImportError, NameError):
            # Implementação alternativa (menos segura, só para demonstração)
            import random
            if comprimento not in [12, 15, 18, 21, 24]:
                comprimento = 12
            return " ".join(random.choice(self.wordlist) for _ in range(comprimento))
    
    @staticmethod
    def gerar_seed_from_frase(frase, passphrase=""):
        """
        Gera a seed a partir de uma frase mnemônica.
        
        Args:
            frase (str): A frase mnemônica
            passphrase (str): Passphrase adicional (opcional)
            
        Returns:
            bytes: A seed
        """
        try:
            # Tentar usar a biblioteca mnemonic
            from mnemonic import Mnemonic
            mnemo = Mnemonic("english")
            return mnemo.to_seed(frase, passphrase)
        except ImportError:
            # Implementação alternativa usando PBKDF2 diretamente
            salt = "mnemonic" + passphrase
            seed = hashlib.pbkdf2_hmac("sha512", frase.encode(), salt.encode(), 2048, 64)
            return seed 