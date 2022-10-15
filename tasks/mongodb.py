from operator import truediv
from pymongo import MongoClient
from cryptography.fernet import Fernet

def conexion():
    cliente =  MongoClient('mongodb+srv://omarn:Movies-Binge@movies.maq9nom.mongodb.net/?retryWrites=true&w=majority')
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
        users_col.insert_one( { "nombre": nombre, "passwd": token, "key": key, "email": email, "pelis": [] } )
        

def buscar_usuario(email):
    cliente = conexion()
    users_col = cliente["moviesimdb"]["users"]
    usuario = users_col.find_one({"email": email})
    
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
    

def peliculas():
    cliente = conexion()
    pelis = cliente["moviesimdb"]["movies"]
    pel = pelis.find()

    a = list(pel)

    return a

def buscar_pelicula(text):
    cliente = conexion()
    pelis = cliente["moviesimdb"]["movies"]
    pel = pelis.find({ 'title' : {"$regex": '.*'+text+'.*', "$options" :'i'} })
    pelicuas_busquedad = list(pel)
    return pelicuas_busquedad

def peliculas_user(email,title,ranking):
    user = buscar_usuario(email)
    array = user['pelis']
    j = {'title': title, 'rating': ranking}
    booleano = True
    for i in range(0,len(array)):
        if array[i]['title'] == title:
            booleano = False
            array[i]['rating'] = ranking
            break
    if booleano:
        array.append(j)

    cliente = conexion()
    users_col = cliente["moviesimdb"]["users"]
    users_col.update_one({'email': email}, { '$set': {'pelis': array}})





    

