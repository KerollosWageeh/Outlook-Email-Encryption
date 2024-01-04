from google.cloud import firestore
import json
from cryptography.hazmat.primitives import serialization

service_account_key_path = "mail-encryption-1056c-firebase-adminsdk-ailf0-b726e3c9cc.json"
with open(service_account_key_path) as json_file:
    service_account_info = json.load(json_file)

# Initialize Firestore client
db = firestore.Client.from_service_account_info(service_account_info)

class FirebaseHandler:

    @staticmethod
    def savePublicKey(email, public_key):

        public_key_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

        data = {
            'public_key': public_key_bytes
        }
        db.collection('users').document(email).set(data)

    @staticmethod
    def getPbulicKey(email):
        user_ref = db.collection('users').document(email)
        
        # Get the document snapshot
        user_snapshot = user_ref.get()

        # Check if the document exists before accessing its data
        if user_snapshot.exists:
            return user_snapshot.to_dict().get('public_key')
        else:
            return None