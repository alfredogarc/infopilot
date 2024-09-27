import mysql.connector
from mysql.connector import Error


def inicializar_tablas(conet):
    cursor = conet.cursor()
    cursor.execute("SELECT COUNT(id) FROM grupousuario")
    resultado = cursor.fetchone()
    nregistros = resultado[0]
    if nregistros == 0:
        cursor.execute("INSERT INTO grupousuario (nombre) VALUES ('Supervisor'), ('Operador'), ('Cliente');")
        sSQL = "INSERT INTO usuarios (login, nombre, apellido, clave, supervisor, rut, idgrupo, nombrecompleto, gruponombre) VALUES "
        sSQL += "('alfredogarc', 'Alfredo', 'García', '1111', 1, '11820003', '1', 'Alfredo García', 'Supervisor'),"
        sSQL += "('cesar', 'Cesar', 'Mansilla', '1111', 0, '1212313', '2', 'Cesar Mansilla', 'Operador');"
        print(sSQL)
        cursor.execute(sSQL)

def verificar_conexion(host, usuario, contrasena,database):
    try:
        # Intentar establecer la conexión
        conexion = mysql.connector.connect(
            host=host,
            user=usuario,
            password=contrasena, 
            database=database,
        )
        
        if conexion.is_connected():
            inicializar_tablas(conexion)
            return conexion  # Retorna la conexión para usarla más adelante
    
    except Error as e:
        print(f"Error al conectar al servidor de base de datos: {e}")
        return None


def conectarbd():
    # Ejemplo de uso
    host = 'localhost'
    usuario = 'root'
    contrasena = 'jorge123.'
    nombre_base_datos = 'infopilot'

    conexion = verificar_conexion(host, usuario, contrasena,nombre_base_datos)
    
    if conexion is None:
       return False  # No se pudo conectar, salir de la función
    
    return conexion



      
conectarbd()