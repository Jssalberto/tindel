from werkzeug.security import generate_password_hash, check_password_hash
class User():
    def __init__(self,id,nombre, usuario,password):
        self.id=id
        self.nombre=nombre
        self.usuario=usuario
        self.password = generate_password_hash(password)
    
    @classmethod
    def check_password(self,hash_password, password):
        return check_password_hash(hash_password, password)
