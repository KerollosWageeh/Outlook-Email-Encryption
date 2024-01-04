from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from cryptography.hazmat.primitives.asymmetric.padding import PSS, MGF1, OAEP
from cryptography.hazmat.primitives.padding import PKCS7
import json
from outlook import OutlookHandler
import base64
from firebase import FirebaseHandler


class EncryptionHandler:

    @staticmethod
    def ecryptMail(to, subject, message, attachments):
        attachments_data = EncryptionHandler.loadAttachments(attachments)
        email = json.dumps({
        "subject": subject,
        "message": message,
        "attachments_data": {attachment.split('/')[-1]: base64.b64encode(attachments_data[attachment]).decode('utf-8') for attachment in attachments_data.keys()},
        "attachments_names": [attachment.split('/')[-1] for attachment in attachments_data.keys()]
        }, sort_keys=True)
        recipient_public_key = FirebaseHandler.getPbulicKey(to)
        recipient_public_key = serialization.load_pem_public_key(recipient_public_key, backend=default_backend())
        if(recipient_public_key is None):
            raise ValueError("Recipient not found")

        current_user = OutlookHandler.get_current_user()
        sender_private_key = EncryptionHandler.load_key_from_file(f'{current_user}PrivateKey.pem', 'private')
        if(sender_private_key is None):
            EncryptionHandler.initApp()

        # Hash the file contents
        hashed = EncryptionHandler.sha256(email) #64 hex characters = 256 bits

        # Sign the hash using the sender private key
        signature = EncryptionHandler.sign_message(sender_private_key, hashed) #256 bytes

        # Concatenate the file contents and the signature
        concatenated = signature + email.encode('utf-8')  #file_content + 256 bytes

        # Generate AES key
        aes_key = os.urandom(32)
        # Encrypt the file content using the AES key
        encrypted_email = EncryptionHandler.aes_encrypt(aes_key, concatenated)

        # Encrypt the AES key using the RSA receiver public key
        encrypted_aes_key = EncryptionHandler.rsa_encrypt(recipient_public_key, aes_key)


        print("Done encryption")
        return encrypted_aes_key+encrypted_email


    @staticmethod
    def loadAttachments(attachments):
        attachments_data = {}
        for attachment in attachments:
            with open(attachment, 'rb') as file:
                attachments_data[attachment] = file.read()
        return attachments_data


    @staticmethod
    def check_email(email):
        pass

    @staticmethod
    def initApp():
        private_key = None
        current_user = OutlookHandler.get_current_user()
        public_key = FirebaseHandler.getPbulicKey(current_user)
        print(os.path.isfile(f'{current_user}PrivateKey.pem'))
        if(os.path.isfile(f'{current_user}PrivateKey.pem')):
            private_key = EncryptionHandler.load_key_from_file(f'{current_user}PrivateKey.pem', 'private')

        private_public_key = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

        if(public_key is None or private_key is None or private_public_key != public_key):
        # if first time or the private key is lost, corrupted or the key pair doesn't match: genrate a new pair and save it
            private_key, public_key = EncryptionHandler.generate_key_pair()
            FirebaseHandler.savePublicKey(current_user, public_key)
            EncryptionHandler.save_key_to_file(private_key, f'{current_user}PrivateKey.pem')

    
    @staticmethod
    def generate_key_pair():
        # Key Pair Generation
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        return private_key, public_key
    
    @staticmethod
    def save_key_to_file(key, filename):
        private_key = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
            )
        with open(filename, 'wb') as file:
            file.write(private_key)

    @staticmethod
    def load_key_from_file(filename, key_type):
        with open(filename, 'rb') as file:
            key_data = file.read()
            if key_type == 'private':
                key = serialization.load_pem_private_key(key_data, password=None, backend=default_backend())
            elif key_type == 'public':
                key = serialization.load_pem_public_key(key_data, backend=default_backend())
            else:
                raise ValueError("Invalid key type. Use 'private' or 'public'.")
        return key

    @staticmethod
    def sha256(message):
        # Create a SHA-256 hasher object
        hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())

        # Update the hasher with the message
        hasher.update(message.encode('utf-8'))

        # Get the hash digest
        digest = hasher.finalize()

        # Return the hash digest in hexadecimal
        return digest.hex()

    @staticmethod
    def sign_message(private_key, data):
        # Digital Signature Generation
        signature = private_key.sign(
            data.encode('latin-1'),
            PSS(
            mgf=MGF1(hashes.SHA256()),
            salt_length=PSS.MAX_LENGTH
            ),
            hashes.SHA256()
            )
        return signature

    @staticmethod
    def aes_encrypt(key, text):

        key = key[:32]
        # Convert the key to bytes if it's not already
        key_bytes = key if isinstance(key, bytes) else key.encode('utf-8')

        # Generate a random IV (Initialization Vector)
        iv = os.urandom(16)

        # Create an AES cipher object
        cipher = Cipher(algorithms.AES(key_bytes), modes.CFB(iv), backend=default_backend())

        # Create a padder
        padder = PKCS7(algorithms.AES.block_size).padder()

        # Pad the text
        padded_text = padder.update(text) + padder.finalize()

        # Create an encryptor object
        encryptor = cipher.encryptor()

        # Encrypt the padded text
        ciphertext = encryptor.update(padded_text) + encryptor.finalize()
        
        # Return the IV and ciphertext
        return iv + ciphertext
    
    @staticmethod
    def rsa_encrypt(public_key, data):
        ciphertext = public_key.encrypt(
            data,
            OAEP(
                mgf=MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext
