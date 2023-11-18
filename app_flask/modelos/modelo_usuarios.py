import re
from .modelo_bandas import Banda
from app_flask.config.mysqlconnection import connectToMySQL
from flask import flash
from app_flask import BASE_DATOS, EMAIL_REGEX

class Usuario:
    def __init__(self, datos):
        self.id = datos['id']
        self.nombre = datos['nombre']
        self.apellido = datos['apellido']
        self.email = datos['email']
        self.password = datos['password']
        self.fecha_creacion = datos['fecha_creacion']
        self.fecha_actualizacion = datos['fecha_actualizacion']

    @classmethod
    def crear_uno(cls, datos):
        query = """
                INSERT INTO usuario(nombre, apellido, email, password)
                VALUES (%(nombre)s, %(apellido)s, %(email)s, %(password)s);
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def obtener_por_email(cls, email):
        query = """
                SELECT *
                FROM usuario
                WHERE email = %(email)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'email': email})
        if len(resultado) == 0:
            return None
        return cls(resultado[0])

    @classmethod
    def obtener_uno(cls, datos):
        query = """
                SELECT *
                FROM usuario
                WHERE email = %(email)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)
        if len(resultado) == 0:
            return None
        return cls(resultado[0])
    
    @classmethod
    def obtener_por_id(cls, id_usuario):
        query = """
                SELECT *
                FROM usuario
                WHERE id = %(id_usuario)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_usuario': id_usuario})
        if len(resultado) == 0:
            return None
        return cls(resultado[0])
    

    @classmethod
    def validar_actualizacion(cls, datos):
        es_valido = True
        if len(datos['nombre']) < 3:
            es_valido = False
            flash('Por favor escribe tu nombre, 3 caracteres mínimos.', 'error_nombre')
        if len(datos['apellido']) < 3:
            es_valido = False
            flash('Por favor escribe tu apellido, 3 caracteres mínimos.', 'error_apellido')
        if not cls.validar_email(datos['email']):
            es_valido = False
            flash('Por favor ingresa un correo válido', 'error_email')
        return es_valido
    
    @classmethod
    def obtener_bandas_del_usuario(cls, id_usuario):
        query = """
                SELECT *
                FROM banda
                WHERE id_creador = %(id_usuario)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_usuario': id_usuario})
        return [Banda(banda) for banda in resultado]
    
    #logica visita de banda

    @classmethod
    def ya_esmiembro_banda(cls, id_usuario, id_banda):
        query = """
            SELECT *
            FROM miembros
            WHERE usuario_id = %(id_usuario)s AND banda_id = %(id_banda)s;
        """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_usuario': id_usuario, 'id_banda': id_banda})
        return bool(resultado)

    @classmethod
    def registrar_miembro_banda(cls, id_usuario, id_banda):
        query = """
            INSERT INTO miembros (usuario_id, banda_id)
            VALUES (%(id_usuario)s, %(id_banda)s)
        """
        data = {
            'id_usuario': id_usuario,
            'id_banda': id_banda
        }
        connectToMySQL(BASE_DATOS).query_db(query, data)

#funciones para la logica de la columna acciones
    @classmethod
    def usuario_es_creador(cls, id_usuario, id_banda):
        query = """
            SELECT COUNT(*)
            FROM banda
            WHERE id_creador = %(id_usuario)s AND id = %(id_banda)s;
        """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_usuario': id_usuario, 'id_banda': id_banda})
        return bool(resultado and resultado[0]['COUNT(*)'] > 0)

    @classmethod
    def usuario_es_miembro(cls, id_usuario, id_banda):
        query = """
            SELECT COUNT(*)
            FROM miembros
            WHERE usuario_id = %(id_usuario)s AND banda_id = %(id_banda)s;
        """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_usuario': id_usuario, 'id_banda': id_banda})
        return bool(resultado and resultado[0]['COUNT(*)'] > 0)

    @classmethod
    def obtener_usuarios_por_banda_id(cls, id_banda):
        query = """
            SELECT u.*
            FROM usuario u
            JOIN miembros m ON u.id = m.usuario_id
            WHERE m.banda_id = %(id_banda)s;
        """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_banda': id_banda})
        return [cls(usuario) for usuario in resultado]

    @staticmethod
    def validar_registro(datos):
        es_valido = True
        if len(datos['nombre']) < 2:
            es_valido = False
            flash('Por favor escribe tu nombre, 2 caracteres mínimos.', 'error_nombre')
        if len(datos['apellido']) < 2:
            es_valido = False
            flash('Por favor escribe tu apellido, 2 caracteres mínimos.', 'error_apellido')
        if not Usuario.validar_email(datos['email']):
            es_valido = False
            flash('Por favor ingresa un correo válido', 'error_email')
        if datos['password'] != datos['password_confirmar']:
            es_valido = False
            flash('Tus contraseñas no coinciden.', 'error_password')
        if len(datos['password']) < 8:
            es_valido = False
            flash('Por favor proporciona una contraseña, 8 caracteres mínimos.', 'error_password')
        return es_valido

    @staticmethod
    def validar_email(email):
        return re.match(EMAIL_REGEX, email) is not None
