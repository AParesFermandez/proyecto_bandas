from flask import flash, redirect, request
from flask import session
from flask import render_template
from app_flask.modelos.modelo_bandas import Banda
from app_flask import app
from app_flask.modelos.modelo_usuarios import Usuario

@app.route('/dashboard', methods=['GET'])
def desplegar_bandas():
    if 'id_usuario' not in session:
        return redirect('/')

    id_usuario_actual = session['id_usuario']

    todas_las_bandas_con_creador = Banda.obtener_todas_las_bandas_con_creador()

    es_creador = {}
    es_miembro = {}
    for banda in todas_las_bandas_con_creador:
        es_creador[banda.id] = Usuario.usuario_es_creador(id_usuario_actual, banda.id)
        es_miembro[banda.id] = Usuario.usuario_es_miembro(id_usuario_actual, banda.id)

    return render_template('dashboard.html', todas_las_bandas=todas_las_bandas_con_creador, es_creador=es_creador, es_miembro=es_miembro)



@app.route('/new', methods=['GET'])
def desplegar_formulario_bandas():
    if 'id_usuario' not in session:
        return redirect('/')

    return render_template('new.html')

@app.route('/new', methods=['POST'])
def crear_bandas():
    if 'id_usuario' not in session:
        return redirect('/')

    nombre = request.form.get('nombre', '')
    genero = request.form.get('genero', '')
    ciudad = request.form.get('ciudad', '')

    nueva_banda = {
        'id_creador': session['id_usuario'],
        'nombre': nombre,
        'genero': genero,
        'ciudad': ciudad
    }

    if not Banda.validar_banda(nueva_banda):
        flash('Error al crear la banda. Verifica los campos e inténtalo nuevamente.', 'error_creacion_banda')
        return redirect('/new')

    id_banda = Banda.crear_banda(nueva_banda)

    if not id_banda:
        flash('Error al crear la banda.', 'error_creacion_banda')
    else:
        flash('Banda creada exitosamente.', 'success_creacion_banda')

    return redirect('/dashboard')

@app.route('/eliminar/banda/<int:id>', methods=['POST'])
def eliminar_bandas(id):
    resultado = Banda.eliminar_banda(id)

    if resultado:
        flash('Banda eliminada exitosamente.', 'success_eliminar_banda')
    else:
        flash('Error al eliminar la banda.', 'error_eliminar_banda')

    return redirect('/dashboard')
#bandas usuario
@app.route('/bandas/usuario', methods=['GET'])
def obtener_bandas_usuario():
    if 'id_usuario' not in session:
        return redirect('/')

    id_usuario = session['id_usuario']
    
    bandas_del_usuario = Banda.obtener_bandas_por_usuario(id_usuario)
    
    bandas_miembro_no_creador = Banda.obtener_bandas_miembro(id_usuario)

    return render_template('bandas_usuario.html', bandas_del_usuario=bandas_del_usuario, bandas_miembro_no_creador=bandas_miembro_no_creador)


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_banda(id):
    if request.method == 'GET':
        banda = Banda.obtener_banda_por_id(id)
        if banda:
            return render_template('editar_banda.html', banda=banda)
        else:
            flash('Banda no encontrada.', 'error')
            return redirect('/dashboard')

    elif request.method == 'POST':
        nombre = request.form['nombre']
        genero = request.form['genero']
        ciudad = request.form['ciudad']

        datos_banda = {
            'nombre': nombre,
            'genero': genero,
            'ciudad': ciudad
        }

        if not Banda.validar_banda(datos_banda):
            return redirect(f'/editar/{id}')

        resultado_actualizacion = Banda.actualizar_banda(id, datos_banda)
        if resultado_actualizacion:
            flash('Banda actualizada correctamente.', 'success')
            return redirect('/dashboard')  
        else:
            flash('Error al actualizar la banda.', 'error')
            return redirect(f'/editar/{id}')

#logica unirse
@app.route('/unirse/<int:id>', methods=['POST'])
def unirse_banda(id):
    if 'id_usuario' not in session:
        return redirect('/')

    id_usuario = session['id_usuario']
    resultado = Banda.unirse_a_banda(id, id_usuario)

    if resultado:
        flash('Te has unido a la banda correctamente.', 'success_unirse_banda')
    else:
        flash('Error al unirse a la banda.', 'error_unirse_banda')

    return redirect('/dashboard')

#logica salirse
@app.route('/salirse/<int:id_banda>', methods=['POST'])
def salirse_banda(id_banda):
    if 'id_usuario' not in session:
        return redirect('/')

    id_usuario = session['id_usuario']

    if Banda.usuario_es_miembro(id_usuario, id_banda):
        Banda.salirse_de_banda(id_usuario, id_banda)
        flash('Has abandonado la banda correctamente.', 'success_salirse_banda')
    else:
        flash('No eres miembro de esta banda.', 'error_salirse_banda')

    return redirect('/dashboard')
