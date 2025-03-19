import os
import struct
import hmac
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

class Encryption:
    def __init__(self):
        # ECDH klíč pro výměnu
        self.ec_private_key = ec.generate_private_key(ec.SECP256R1())
        self.ec_public_key = self.ec_private_key.public_key()

        # RSA klíč pro digitální podpisy
        self.rsa_private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=3072
        )
        self.rsa_public_key = self.rsa_private_key.public_key()

    def derive_shared_key(self, peer_public_bytes):
        """ Odvození sdíleného klíče pomocí ECDH """
        peer_public_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), peer_public_bytes)
        shared_secret = self.ec_private_key.exchange(ec.ECDH(), peer_public_key)
        return HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data'
        ).derive(shared_secret)

    def encrypt(self, key, plaintext, associated_data=None):
        """ Šifrování pomocí AES-GCM """
        nonce = os.urandom(12)
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
        return nonce + ciphertext

    def decrypt(self, key, ciphertext, associated_data=None):
        """ Dešifrování pomocí AES-GCM """
        nonce = ciphertext[:12]
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext[12:], associated_data)

    def sign(self, message):
        """ Podepsání zprávy pomocí RSA """
        signature = self.rsa_private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    def verify(self, message, signature):
        """ Ověření podpisu pomocí RSA """
        try:
            self.rsa_public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    def get_ec_public_bytes(self):
        """ Získání veřejného klíče v X9.62 formátu """
        return self.ec_public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
