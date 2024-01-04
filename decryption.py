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


class DecryptionHandler:

    @staticmethod
    def decrypt(sender, message):
        sender_public_key = FirebaseHandler.getPbulicKey(sender)
        sender_public_key = serialization.load_pem_public_key(sender_public_key, backend=default_backend())
        if(sender_public_key is None):
            raise ValueError("Sender not found")
        
        current_user = OutlookHandler.get_current_user()
        
        recipient_private_key = DecryptionHandler.load_key_from_file(f'{current_user}PrivateKey.pem', 'private')
        
        if(recipient_private_key is None):
            raise ValueError("You lost your private key")
        
        # Split the encrypted file into the encrypted AES key, the IV, and the ciphertext
        message = base64.b64decode(message)
        encrypted_aes_key = message[:256]
        ciphertext = message[256:]

        aes_key = DecryptionHandler.rsa_decrypt(recipient_private_key, encrypted_aes_key)

        decrypted_content = DecryptionHandler.aes_decrypt(aes_key, ciphertext)
        signature = decrypted_content[:256]
        email = decrypted_content[256:].decode('utf-8')
        # Hash the file contents
        file_hash = DecryptionHandler.sha256(email) #64 hex characters = 256 bits
        # Verify the signature using the sender public key
        if not DecryptionHandler.verify_signature(sender_public_key, file_hash, signature):
            raise ValueError("Signature verification failed")
        contents = json.loads(email)
        contents['attachments_data'] = {
            attachment: base64.b64decode(contents['attachments_data'][attachment]) for attachment in contents['attachments_data'].keys()
            }
        return contents

    
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
        with open(filename, 'wb') as file:
            file.write(key)

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
    def aes_decrypt(key, ciphertext):
        # Extract the IV from the ciphertext
        iv = ciphertext[:16]

        # Extract the actual ciphertext
        ciphertext = ciphertext[16:]

        key = key[:32]

        # Convert the key to bytes if it's not already
        key_bytes = key if isinstance(key, bytes) else key.encode('utf-8')

        # Create an AES cipher object
        cipher = Cipher(algorithms.AES(key_bytes), modes.CFB(iv), backend=default_backend())

        # Create a decryptor object
        decryptor = cipher.decryptor()

        # Decrypt the ciphertext
        decrypted_text = decryptor.update(ciphertext) + decryptor.finalize()

        # Create an unpadder
        unpadder = PKCS7(algorithms.AES.block_size).unpadder()

        # Unpad the decrypted text
        unpadded_text = unpadder.update(decrypted_text) + unpadder.finalize()
        # Return the unpadded text
        return unpadded_text
    
    
    @staticmethod
    def rsa_decrypt(private_key, ciphertext):
        data = private_key.decrypt(
            ciphertext,
            OAEP(
                mgf=MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return data

    @staticmethod
    def verify_signature(public_key, message, signature):
        # Digital Signature Verification
        try:
            public_key.verify(
                signature,
                message.encode('utf-8'),
                PSS(
                    mgf=MGF1(hashes.SHA256()),
                    salt_length=PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            print("Signature is valid.")
            return True
        except Exception as e:
            print("Signature is invalid:", str(e))
            return False