import firebase_admin
from firebase_admin import credentials, firestore
import os

def iniciar_firebase():
    ruta = os.path.expanduser("~/Escritorio/credenciales-firebase.json")
    cred = credentials.Certificate(ruta)
    # cred = credentials.Certificate("credenciales-firebase.json")
    firebase_admin.initialize_app(cred)
    return firestore.client()
