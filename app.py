from flask import Flask, render_template, url_for, request, session, redirect, flash, jsonify
from werkzeug.security import generate_password_hash as generate_hash
from werkzeug.security import generate_password_hash
# from traducciontzozpa import traduccioness
from functools import wraps
from conexion.conexion import conexion
from flask import send_from_directory
from Models.Usuario import Usuario
from flask_sslify import SSLify
from datetime import datetime
import random
import string
import json
import os
from firebase_config import iniciar_firebase

db = iniciar_firebase()

app = Flask(__name__)
app.secret_key="B!1weNAt1TkvhUI*S"
cursor = conexion.cursor(dictionary=True)
# app.config.from_pyfile('config.py')
CARPETA = os.path.join('/static/img')
app.config['CARPETA']= CARPETA


context = ('web.crt', 'web.key')
sslify = SSLify(app)

@app.route('/static/img/<path:filename>')
def get_image(filename):
    return send_from_directory('static/img', filename)

@app.route('/img/<nuevo_nombre_img>')
def img(nuevo_nombre_img):
    return send_from_directory(app.config["CARPETA"], nuevo_nombre_img)

@app.route('/alert')
def alert():
    return render_template('alert.html')

#🔐
def login_requerido(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        if not session.get('nombreUsuario'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorator_function

@app.route('/')
def inicio():
    return render_template('inde.html')

@app.route('/inde', methods=["GET"])
def inde():
    return render_template('inde.html')

@app.route('/login/', methods=["GET"]) 
def login():
    return render_template('login.html')

@app.route("/traductor_tzozil/", methods=["GET"])
@login_requerido
def traductor_tzozil():
    return render_template('traductor_tso.html')

@app.route('/index/', methods=["GET"])
@login_requerido 
def index( ):
        return render_template('estructura.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/perfil/', methods=["GET"]) 
@login_requerido
def perfil():
    try:
        conexion.ping(reconnect=True)  # Reestablece la conexión si se ha perdido
        cursor = conexion.cursor()
        sql = "SELECT id, nombre, usuario, image FROM users"
        cursor.execute(sql)
        mostrarusuarios = cursor.fetchall()
        cursor.close()

        print(f"Usuarios recuperados: {mostrarusuarios}")
        return render_template("perfil.html", mostrarusuarios=mostrarusuarios)
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        return render_template('perfil.html', mostrarusuarios=[])  



#&OBTENER USUARIOS DE LA RUTA PERFIL
@app.route("/get_users_perfil/", methods=["GET", "POST"])
def get_users_perfil():
    if request.method == "GET":
        return render_template("formulario_registro_perfil.html")
    elif request.method == "POST":
        id = request.args.get("id")
        nombre = request.form["nombre"]
        usuario = request.form["usuario"]
        password = request.form["password"]
        image = request.files["image"]
        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")
        if image.filename != "":
            nuevo_nombre_img = tiempo+image.filename
            image.save("static/img/"+ nuevo_nombre_img)
            sql = "INSERT INTO users VALUES(%s, %s, %s, %s, %s)"
            datos_usuarios_perfil = (id,nombre, usuario, generate_hash(password), nuevo_nombre_img)
            show_users = cursor.execute(sql, datos_usuarios_perfil)
            conexion.commit()
            return redirect(url_for("perfil"))
    return render_template("perfil.html")

#! RUTA ELIMINAR DE TABLA USUARIO PERFIL
# @app.route("/eliminar_usuario_perfil/<int:id>/", methods=["GET"])
# def eliminar_usuario_perfil(id):
#     cursor.execute("SELECT image FROM users WHERE id=%s", (id,))
#     fila = cursor.fetchall()
#     os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
#     cursor.execute("DELETE FROM users WHERE id=%s", (id,))
#     conexion.commit()
#     return redirect(url_for("perfil"))

@app.route("/eliminar_usuario_perfil/<int:id>/", methods=["GET"])
def eliminar_usuario_perfil(id):
    cursor.execute("SELECT image FROM users WHERE id=%s", (id,))
    fila = cursor.fetchone()  # Usamos fetchone() en lugar de fetchall()

    if fila and fila["image"]:  # Verificamos si hay datos
        ruta_imagen = os.path.join(app.config['CARPETA'], fila["image"])

        if os.path.exists(ruta_imagen):  # Verifica si el archivo existe antes de eliminarlo
            os.remove(ruta_imagen)
    
    cursor.execute("DELETE FROM users WHERE id=%s", (id,))
    conexion.commit()

    return redirect(url_for("perfil"))



@app.route('/tabla_usuarios/', methods=["GET"])
@login_requerido
def tabla_usuarios():
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuario")
        try:
            usuarios_db = cursor.fetchall()
            return render_template('tabla_usuarios.html', usuarios_db=usuarios_db)  # Usamos render_template
        except Exception as e:
            print(f"Error: {e}")  # Para ayudar a depurar
            return render_template('login.html')  # Redirige al login si hay error


@app.route("/eliminar_usuarios/", methods=["POST"])
def eliminar_usuarios():
    try:
        # Verificar si el usuario está autenticado
        if "nombreUsuario" not in session:
            return jsonify({"success": False, "message": "Debe iniciar sesión"}), 403

        data = request.get_json()  # Obtener datos enviados en formato JSON
        user_id = data.get("id")  # Extraer el ID del usuario
        print(data)

        if not user_id:
            return jsonify({"success": False, "message": "ID de usuario no proporcionado"})

        cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
        print(user_id)
        conexion.commit()

        return jsonify({"success": True, "message": "Usuario eliminado correctamente"})

    except Exception as e:
        print("Error:", e)
        return jsonify({"success": False, "message": "Error al eliminar el usuario"})

@app.route('/Create_user/', methods=["GET", "POST"])
def Create_user():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        try:
            nombre = request.form['nombre']
            usuario = request.form['usuario']
            correo_electronico = request.form['correo_electronico']
            password = request.form['password']
            id_rol = 2  # Rol por defecto es "usuario"
            # Generar el hash de la contraseña correctamente
            hashed_password = generate_password_hash(password)  
            # Insertar en la base de datos
            consulta = "INSERT INTO usuario (nombre, usuario, correo_electronico, password, id_rol) VALUES (%s, %s, %s, %s, %s)"
            valores = (nombre, usuario, correo_electronico, hashed_password, id_rol)
            cursor.execute(consulta, valores)
            conexion.commit()
            session['nombreUsuario'] = nombre
            session['rolUsuario'] = "usuario"
            return redirect(url_for('traductor_tzozil'))
        except Exception as e:
            print(f"Error al crear usuario: {e}")
            return jsonify({"success": False, "message": "Error al crear usuario"})

    else:
        return render_template('login.html')


@app.route('/validar_user/', methods=["POST"])
def validar_user():
    usuario=request.form['usuario']
    password=request.form['password']
    #*====Realiza consulta para obtener los datos==
    consulta_user = ("SELECT usuario,password FROM usuario WHERE usuario=%s AND usuario=%s")
    valores_user = (usuario,password)
    cursor.execute(consulta_user, valores_user)
    user_valid=cursor.fetchone()
    if user_valid:
        password_in_db = user_valid[1]
        if Usuario.check_hash(password_in_db ,password):
            session['nombreUsuario'] = user_valid[0]
            return jsonify({"success": True, "message": "Inicio de sesión exitoso"})
    else:
        return jsonify({"success": False, "message": "Credenciales incorrectas"})


# @app.route('/validar_usuario/', methods=["GET", "POST"])
# def validar_usuario():
#     try:
#         usuario = request.form['usuario']
#         password = request.form['password']
#         consulta_get_users = """
#             SELECT u.id, u.nombre, u.usuario, u.password, r.nombre_rol 
#             FROM usuario u 
#             JOIN roles r ON u.id_rol = r.id 
#             WHERE u.usuario = %s
#         """
#         valores_usuario = (usuario,)
#         cursor.execute(consulta_get_users, valores_usuario)
#         user_valido = cursor.fetchone()
#         if user_valido:
#             hash_password_db = user_valido["password"]  # Usar clave de diccionario
#             try:
#                 if Usuario.check_hash(hash_password_db, password):
#                     nombre_rol = user_valido["nombre_rol"]
#                     session['nombreUsuario'] = user_valido["usuario"]
#                     session['nombre_rol'] = nombre_rol
#                     nombre_rol = user_valido["nombre_rol"]
#                     if nombre_rol == "admin":
#                         return redirect(url_for('tabla_usuarios'))
#                     else:
#                         return redirect(url_for('traductor_tzozil'))
#                 else:
#                     flash("Error: Contraseña incorrecta Credenciales incorrectas", "danger")
#                     return render_template('login.html')
#             except Exception as hash_error:
#                 msm = (f"Error en check_hash(): {hash_error}")
#                 return flash(msm)
#         else:
#             flash("Error: Usuario no encontrado")
#             return flash("Usuario no encontrado")
#     except Exception as e:
#         print(f"Error en la función validar_usuario: {str(e)}")
#         return jsonify({"success": False, "message": f"Error en el servidor: {str(e)}"})


@app.route('/validar_usuario/', methods=["GET", "POST"])
def validar_usuario():
    try:
        if request.method == "POST":
            usuario = request.form['usuario']
            password = request.form['password']
            consulta_get_users = """
                SELECT u.id, u.nombre, u.usuario, u.password, r.nombre_rol 
                FROM usuario u 
                JOIN roles r ON u.id_rol = r.id 
                WHERE u.usuario = %s
            """
            valores_usuario = (usuario,)
            cursor.execute(consulta_get_users, valores_usuario)
            user_valido = cursor.fetchone()

            if user_valido:
                hash_password_db = user_valido["password"]  # Usar clave de diccionario
                try:
                    if Usuario.check_hash(hash_password_db, password):
                        nombre_rol = user_valido["nombre_rol"]
                        session['nombreUsuario'] = user_valido["usuario"]
                        session['nombre_rol'] = nombre_rol

                        if nombre_rol == "admin":
                            return redirect(url_for('tabla_usuarios'))
                        else:
                            return redirect(url_for('traductor_tzozil'))
                    else:
                        flash("Error: Contraseña incorrecta. Credenciales incorrectas.", "danger")
                        return render_template('login.html')
                except Exception as hash_error:
                    msm = f"Error en check_hash(): {hash_error}"
                    flash(msm, "danger")
                    return render_template('login.html')
            else:
                flash("Error: Usuario no encontrado.", "danger")
                return render_template('login.html')

    except Exception as e:
        print(f"Error en la función validar_usuario: {str(e)}")
        return jsonify({"success": False, "message": f"Error en el servidor: {str(e)}"})
 
@app.route('/tablaregistrodocentes/', methods=["GET"])
@login_requerido
def tablaregistrodocentes():
        cursor.execute("SELECT * FROM personas")
        una_persona = cursor.fetchall()
        return render_template('tablaregistrodocentes.html', una_persona=una_persona)


@app.route('/cerrarsesion/', methods=["POST"])
def cerrarsesion():
    if "nombreUsuario" in session:
        session.pop('nombreUsuario', None)
        return jsonify({"success": True, "message": "Sesión cerrada correctamente"})
    else:
        return jsonify({"success": False, "message": "No hay sesión activa"})


@app.route('/alfabeto/', methods=['GET'])
@login_requerido
def alfabeto():
        return render_template('alfabeto.html')

@app.route('/animales/', methods=['GET'])
@login_requerido
def animales():
        return render_template('animales.html')

@app.route('/cosasobjetos/', methods=['GET'])
@login_requerido
def cosasobjetos():
        return render_template('cosasobjetos.html')

@app.route('/familia/', methods=['GET'])
@login_requerido
def familia():
        return render_template('familia.html')
    
@app.route('/numeros/',methods=["GET"])
@login_requerido
def numeros():
    return render_template('numeros.html')

@app.route('/politicas/', methods=['GET'])
@login_requerido
def politicas():
        return render_template('politicas.html') 


@app.route('/traducir', methods=['POST'])
def traducir():
    datos = request.json
    palabra = datos.get("texto", "").lower()
    idioma_origen = datos.get("idioma_origen", "").lower().strip()
    idioma_destino = datos.get("idioma_destino", "").lower().strip()
    try:
        doc_ref = db.collection('traducciones').document(idioma_origen)
        doc = doc_ref.get()
        if doc.exists:
            diccionario = doc.to_dict()
            traduccion = diccionario.get(palabra, "Frase no encontrada")
        else:
            traduccion = "⚠️ Idioma no encontrado en la base de datos."
    except Exception as e:
        traduccion = f"❌ Error al traducir: {str(e)}"

    return jsonify({"traduccion": traduccion})


@app.route('/recuperar_password/')
def recuperar_password():
    return render_template('recuperar.html')

def generar_nueva_contrasena():
    """Genera una nueva contraseña de 12 caracteres aleatorios con mayúsculas, minúsculas, números y caracteres especiales"""
    caracteres = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?/~"
    return ''.join(random.choices(caracteres, k=12))  # Aumenté a 12 caracteres para más seguridad
 
@app.route('/recuperar_contrasena', methods=['POST'])
def recuperar_contrasena():
    if request.method == 'POST':
        usuario = request.form['usuario']
        correo = request.form['correo']
        cursor.execute("SELECT * FROM usuario WHERE usuario = %s AND correo_electronico = %s", (usuario, correo))
        user = cursor.fetchone()
        if user:
            nueva_contrasena = generar_nueva_contrasena()
            hashed_password = generate_password_hash(nueva_contrasena)  # Cifrar la nueva contraseña
            cursor.execute("UPDATE usuario SET password = %s WHERE usuario = %s AND correo_electronico = %s",
                (hashed_password, usuario, correo))
            conexion.commit()
            flash(f"Tu nueva contraseña es: {nueva_contrasena}. Cámbiala después de iniciar sesión.", "success")
            return redirect(url_for('recuperar'))  # Redirigir al login

        else:
            flash("El usuario o correo electrónico no existen.", "danger")
            return redirect(url_for('mostrar_recuperar_contrasena'))
    return redirect(url_for('login'))


@app.route('/mostrar_recuperar_contrasena')
def mostrar_recuperar_contrasena():
    return render_template('recuperar.html')

@app.route('/enviar_msm/', methods=["POST"])
def enviar_msm():
    nombre = request.form["nombre"]
    correo = request.form["correo"]
    telefono = request.form["telefono"]
    mensaje = request.form["mensaje"]
    if not nombre or not correo or not mensaje:
        return flash("Error: Faltan datos obligatorios", "danger")
    try:
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO mensajes (nombre, correo, telefono, mensaje) VALUES (%s, %s, %s, %s)",
            (nombre, correo, telefono, mensaje))
        conexion.commit()
        cursor.close()
        conexion.close()
        flash("Mensaje enviado con éxito. Pronto te responderemos.", "success")
        return redirect(url_for('inde'))
    except Exception as e:
            # En caso de error, mostrar el error
            flash(f"Hubo un error al enviar el mensaje: {str(e)}", "danger")
            return redirect(url_for('inde'))  # Redirige al index o donde lo necesites

# Ruta para que el administrador vea los mensajes
@app.route('/adminmensajes/')
def adminmensajes():
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, correo, telefono, mensaje, fecha FROM mensajes WHERE visto = FALSE")
    mensajes = cursor.fetchall()
    cursor.close()
    return render_template('mensajes.html', mensajes=mensajes) 

if __name__ == '__main__':
    context = ('web.crt', 'web.key')
    app.run(ssl_context='adhoc', port='5000', host='0.0.0.0')