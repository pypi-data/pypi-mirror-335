import os

from cryptography.fernet import Fernet, InvalidToken


class EncryptionHelper:
    def __init__(self, key: str = None):
        if key is None:
            key = os.getenv("PLURALLY_ENCRYPTION_KEY")
        if key is None:
            raise ValueError("Should provide encryption key or set env variable PLURALLY_ENCRYPTION_KEY")
        self.cipher = Fernet(key)

    def encrypt(self, plain_text: str) -> str:
        try:
            return self.cipher.encrypt(plain_text.encode()).decode()
        except InvalidToken:
            raise ValueError("Invalid encryption key")

    def decrypt(self, encrypted_text: str) -> str:
        if isinstance(encrypted_text, bytes):
            encrypted_text = encrypted_text.decode()
        try:
            return self.cipher.decrypt(encrypted_text.encode()).decode()
        except InvalidToken:
            raise ValueError("Invalid encryption key")


def encrypt(val):
    return EncryptionHelper().encrypt(val)


def decrypt(val):
    return EncryptionHelper().decrypt(val)
