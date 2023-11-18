from flask import render_template, request, redirect, session, flash
from app_flask.modelos.modelo_bandas import Banda
from app_flask.modelos.modelo_usuarios import Usuario
from app_flask import app
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@app.route('/', methods=['GET'])
def despliega_login_registro():
    return render_template('login_registro.html')

@app.route('/procesa/registro', methods=['POST'])
def procesa_registro():
    datos_registro = {
        "nombre": request.form.get('nombre', ''),
        "apellido": request.form.get('apellido', ''),
        "email": request.form.get('email', ''),
        "password": request.form.get('password', ''),
        "password_confirmar": request.form.get('password_confirmar', '')
    }

    if not Usuario.validar_registro(datos_registro):
        return redirect('/')

    password_encriptado = bcrypt.generate_password_hash(datos_registro['password'])
    nuevo_usuario = {
        **datos_registro,
        'password': password_encriptado
    }
    id_usuario = Usuario.crear_uno(nuevo_usuario)

    session['id_usuario'] = id_usuario
    session['nombre'] = nuevo_usuario['nombre']
    session['apellido'] = nuevo_usuario['apellido']

    return redirect('/dashboard')

@app.route('/procesa/login', methods=['POST'])
def procesa_login():
    usuario_login = Usuario.obtener_uno({"email": request.form.get('email', '')})

    if usuario_login is None:
        flash('Este correo no existe', 'error_login')
        return redirect('/')

    if not bcrypt.check_password_hash(usuario_login.password, request.form.get('password', '')):
        flash('Credenciales incorrectas', 'error_login')
        return redirect('/')

    session['id_usuario'] = usuario_login.id
    session['nombre'] = usuario_login.nombre
    session['apellido'] = usuario_login.apellido

    return redirect('/dashboard')

@app.route('/user/account')
def user_account():
    if 'id_usuario' not in session:
        return redirect('/')

    usuario_actual = Usuario.obtener_por_id(session.get('id_usuario'))

    bandas_del_usuario = Banda.obtener_bandas_por_usuario(session.get('id_usuario'))
    bandas_miembro = Banda.obtener_bandas_miembro(session.get('id_usuario'))

    return render_template('account.html', usuario=usuario_actual, bandas_del_usuario=bandas_del_usuario, bandas_miembro=bandas_miembro)



@app.route('/procesa/logout', methods=['POST'])
def procesa_logout():
    session.clear()
    return redirect('/')
