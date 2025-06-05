import firebase_admin
from firebase_admin import credentials, firestore

def iniciar_firebase():
    cred = credentials.Certificate("credenciales-firebase.json")
    firebase_admin.initialize_app(cred)
    return firestore.client()
