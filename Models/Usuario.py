from werkzeug.security import generate_password_hash, check_password_hash

class Usuario():
    def __init__(self, usuario, password, role):
        self.usuario = usuario                         
        self.password = self.__generate_hash(password)#method="sha512"

    def __generate_hash(self,password):
        return generate_password_hash(password)

    #@staticmethod
    def check_hash(password,hash_password):
        return check_password_hash(password,hash_password)