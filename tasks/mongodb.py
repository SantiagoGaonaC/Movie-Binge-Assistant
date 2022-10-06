from operator import truediv
from pymongo import MongoClient
from cryptography.fernet import Fernet

def conexion():
    cliente =  MongoClient('mongodb://moviesdb:2tgpguBaPN1wLbjF6MC58atNXAnToWUY1F5895yt0jCUF1lPgxktObXKi9iTacTHyIrCQ2Jr8oBUAUIWCpAaqA==@moviesdb.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@moviesdb@')
    return cliente

def verficiar_user_repetido(email):
    usuario = buscar_usuario(email)
    if(str(type(usuario)) == "<class 'NoneType'>"):
        return True
    else:
        return False


def insert_user(nombre, email, passwd ):
    if(verficiar_user_repetido(email)):
        cliente = conexion()
        users_col = cliente["moviesimdb"]["users"]
        key = Fernet.generate_key()
        f = Fernet(key)
        token = f.encrypt(str.encode(passwd))
        users_col.insert_one( { "nombre": nombre, "passwd": token, "key": key, "email": email } )
        cliente.close()

def buscar_usuario(email):
    cliente = conexion()
    users_col = cliente["moviesimdb"]["users"]
    usuario = users_col.find_one({"email": email})
    cliente.close()
    return usuario

def login(email,passwd):
    usuario = buscar_usuario(email)
    if(str(type(usuario)) == "<class 'dict'>"):
        f = Fernet(usuario['key'])
        token = usuario['passwd']
        pwd = f.decrypt(token)
        if(pwd.decode() == passwd):
            return True
        else:
            return False
    else:
        print("usuario no registrado")
    


    

