from app_flask.config.mysqlconnection import connectToMySQL
from flask import flash
from app_flask import BASE_DATOS

class Banda:
    def __init__(self, datos):
        self.id = datos['id']
        self.nombre = datos['nombre']
        self.genero = datos['genero']
        self.ciudad = datos['ciudad']
        self.id_creador = datos['id_creador']
        self.fecha_creacion = datos['fecha_creacion']
        self.fecha_actualizacion = datos['fecha_actualizacion']

    @classmethod
    def crear_banda(cls, datos_banda):
        query = """
                INSERT INTO banda(nombre, genero, ciudad, id_creador)
                VALUES (%(nombre)s, %(genero)s, %(ciudad)s, %(id_creador)s);
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos_banda)

    @classmethod
    def obtener_banda_por_id(cls, id_banda):
        query = """
                SELECT *
                FROM banda
                WHERE id = %(id_banda)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_banda': id_banda})
        if len(resultado) == 0:
            return None
        return cls(resultado[0])

    @classmethod
    def obtener_todas_las_bandas(cls):
        query = """
                SELECT *
                FROM banda;
                """
        resultados = connectToMySQL(BASE_DATOS).query_db(query)
        return [cls(resultado) for resultado in resultados]

    @classmethod
    def obtener_todas_las_bandas_con_creador(cls):
        query = """
                SELECT b.*, u.nombre AS nombre_creador
                FROM banda b
                JOIN usuario u ON b.id_creador = u.id;
                """
        resultados = connectToMySQL(BASE_DATOS).query_db(query)
        bandas = []
        for resultado in resultados:
            banda = cls(resultado)
            banda.nombre_creador = resultado['nombre_creador']
            bandas.append(banda)
        return bandas

    @classmethod
    def obtener_una_con_creador(cls, id_banda):
        query = """
                SELECT b.*, u.nombre AS nombre_creador
                FROM banda b
                JOIN usuario u ON b.id_creador = u.id
                WHERE b.id = %(id_banda)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_banda': id_banda})
        if not resultado or len(resultado) == 0:
            return None
        banda = cls(resultado[0])
        banda.nombre_creador = resultado[0]['nombre_creador']
        return banda

    @classmethod
    def eliminar_banda(cls, id_banda):
        query = """
                DELETE FROM banda
                WHERE id = %(id_banda)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, {'id_banda': id_banda})

    @classmethod
    def obtener_detalles_por_id_usuario(cls, id_usuario, id_banda):
        query = """
                SELECT b.*, u.nombre AS nombre_usuario
                FROM banda b
                JOIN usuario u ON b.id_creador = u.id
                WHERE b.id = %(id_banda)s AND b.id_creador = %(id_usuario)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_banda': id_banda, 'id_usuario': id_usuario})

        if not resultado or len(resultado) == 0:
            return None

        banda = cls(resultado[0])
        banda.nombre_usuario = resultado[0]['nombre_usuario']
        return banda

    @classmethod
    def obtener_bandas_por_usuario(cls, id_usuario):
        query = """
                SELECT *
                FROM banda
                WHERE id_creador = %(id_usuario)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_usuario': id_usuario})
        return [cls(banda) for banda in resultado]

    @classmethod
    def actualizar_banda(cls, id_banda, datos_banda):
        if cls.validar_banda(datos_banda):
            query = """
                    UPDATE banda
                    SET nombre = %(nombre)s,
                        genero = %(genero)s,
                        ciudad = %(ciudad)s,
                        fecha_actualizacion = NOW()
                    WHERE id = %(id)s;
                    """
            datos_banda['id'] = id_banda
            connectToMySQL(BASE_DATOS).query_db(query, datos_banda)
            return True
        else:
            return False
    
    @classmethod
    def contar_miembros_por_banda(cls, id_banda):
        query = """
                SELECT COUNT(*)
                FROM miembros
                WHERE banda_id = %(id_banda)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_banda': id_banda})
        if resultado:
            return resultado[0]['COUNT(*)']
        return 0
    
    @classmethod
    def unirse_a_banda(cls, id_banda, id_usuario):
        if cls.usuario_es_miembro(id_usuario, id_banda):
            return False

        query = """
                INSERT INTO miembros (usuario_id, banda_id)
                VALUES (%(usuario_id)s, %(banda_id)s);
                """
        datos = {'usuario_id': id_usuario, 'banda_id': id_banda}
        connectToMySQL(BASE_DATOS).query_db(query, datos)
        return True

    
    @classmethod
    def usuario_es_miembro(cls, id_usuario, id_banda):
        query = """
                SELECT *
                FROM miembros
                WHERE usuario_id = %(id_usuario)s AND banda_id = %(id_banda)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_usuario': id_usuario, 'id_banda': id_banda})
        return bool(resultado)
    
    @classmethod
    def salirse_de_banda(cls, id_usuario, id_banda):
        query = """
                DELETE FROM miembros
                WHERE usuario_id = %(id_usuario)s AND banda_id = %(id_banda)s;
                """
        data = {
            'id_usuario': id_usuario,
            'id_banda': id_banda
        }
        return connectToMySQL(BASE_DATOS).query_db(query, data)
    
    #bandas de un usuario
    @classmethod
    def obtener_bandas_miembro(cls, id_usuario):
        query = """
                SELECT b.*
                FROM banda b
                JOIN miembros m ON b.id = m.banda_id
                WHERE m.usuario_id = %(id_usuario)s;
                """
        resultados = connectToMySQL(BASE_DATOS).query_db(query, {'id_usuario': id_usuario})
        return [cls(resultado) for resultado in resultados]


    @staticmethod
    def validar_banda(datos_banda):
        es_valido = True
        if len(datos_banda['nombre']) < 2:
            es_valido = False
            flash('el nombre debe tener al menos 2 caracteres.', 'error_nombre')

        if len(datos_banda['genero']) < 2:
            es_valido = False
            flash('La ubicación debe tener al menos 2 caracteres.', 'error_genero')

        if len(datos_banda['ciudad']) < 1:
            es_valido = False
            flash('la ciudad necesita almenos un carater.', 'error_ciudad')

        return es_valido