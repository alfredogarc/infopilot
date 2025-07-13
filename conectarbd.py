import mysql.connector
from funciones import whatsapp_inicializar

#def connect_db():
#    return sqlite3.connect('analisis.db')  # Cambiado a analisis.db

def conectarBD():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='jorge123.',
            database='infopilot'
        )
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Error al conectar a la base de datos: {err}")
        return None

def conectarBD_anterior():
    # Conectar a la base de datos (se creará si no existe)
    conn = mysql.connector.connect(
        host='localhost',  # Cambia esto si tu base de datos está en otro host
        user='root',  # Reemplaza con tu usuario de MariaDB
        password='jorge123.',  # Reemplaza con tu contraseña de MariaDB
        database='infopilot'  # Reemplaza con el nombre de tu base de datos
    )
    return conn

def nuevo_registro(tabla, campos, valores):
    # Dividir los campos y valores en listas
    campos = campos.replace(" ","")
    campos_lista = [campo.strip() for campo in campos.split(',')]
    valores_lista = [valor.strip() for valor in valores.split(',')]

    # Verificar que el número de campos y valores coincida
    if len(campos_lista) != len(valores_lista):
        raise ValueError("El número de campos y valores no coincide")

    # Procesar campos y valores
    campos_procesados = []
    valores_procesados = []
    for campo, valor in zip(campos_lista, valores_lista):
        if campo.startswith('s_'):
            # Si el campo empieza con 's_', quitar el prefijo y poner el valor entre comillas
            campos_procesados.append(campo[2:])
            valores_procesados.append(f"'{valor}'")
        else:
            # Si no, dejar el campo como está y el valor sin comillas
            campos_procesados.append(campo)
            valores_procesados.append(valor)

    # Construir la sentencia SQL
    campos_str = ', '.join(campos_procesados)
    valores_str = ', '.join(valores_procesados)
    sql = f"INSERT INTO {tabla} ({campos_str}) VALUES ({valores_str})"
    #print(f"SQL: {sql}")
    return ejecutar_sql(sql)

def editar_registro(tabla, campos, valores, condicion):
    # Dividir los campos y valores en listas
    campos_lista = [campo.strip() for campo in campos.split(',')]
    valores_lista = [valor.strip() for valor in valores.split(',')]

    # Verificar que el número de campos y valores coincida
    if len(campos_lista) != len(valores_lista):
        raise ValueError("El número de campos y valores no coincide")

    # Procesar campos y valores
    actualizaciones = []
    for campo, valor in zip(campos_lista, valores_lista):
        if campo.startswith('s_'):
            # Si el campo empieza con 's_', quitar el prefijo y poner el valor entre comillas
            campo_procesado = campo[2:]
            valor_procesado = f"'{valor}'"
        else:
            # Si no, dejar el campo como está y el valor sin comillas
            campo_procesado = campo
            valor_procesado = valor
        actualizaciones.append(f"{campo_procesado} = {valor_procesado}")

    # Construir la sentencia SQL
    actualizaciones_str = ', '.join(actualizaciones)
    sql = f"UPDATE {tabla} SET {actualizaciones_str} WHERE {condicion}"
    #print(sql)
    ejecutar_sql(sql)

def delete_record(tabla, campo_id, id):
    sql = f"DELETE FROM {tabla} WHERE {campo_id} = {id}"
    print(sql)
    #ejecutar_sql(sql)

def ejecutar_sql(sql):
    conn = None
    cursor = None
    nDevolver = None
    try:
        conn = conectarBD()
        if not conn:
            print("❌ Error al conectar a la base de datos")
            return None
        #else:
        #    print("✅✅✅✅ Conexión a la base de datos exitosa")
        cursor = conn.cursor()
        cursor.execute(sql)
        if sql.lower().startswith("select"):
            nDevolver = cursor.fetchall()
            #print("    3 (SELECT) ")
        else:
            conn.commit()
            if sql.lower().startswith("insert"):
                # Para INSERT, obtenemos el last_insert_id
                # Es mejor usar un nuevo cursor o asegurar que el anterior esté limpio
                # Sin embargo, mysql.connector suele manejar esto si no hay fetchall() previo
                # La forma más segura es obtenerlo directamente del cursor si es posible,
                # o ejecutar una nueva consulta en un nuevo cursor si el driver lo requiere.
                # En mysql.connector, cursor.lastrowid es a menudo suficiente para INSERTs.
                nDevolver = cursor.lastrowid
                #print("✅ INSERT exitoso")
                #print("    1 (INSERT) ")
            else:
                # Para UPDATE/DELETE, no hay resultados que leer, solo commit
                nDevolver = 0 # Indicar éxito sin retorno de datos
                #print("✅ Consulta (UPDATE/DELETE) exitosa.")
                #print("    2 (UPDATE/DELETE) ")                
    except mysql.connector.Error as err: # Captura errores específicos de MySQL Connector
        print(f"❌ Error en consulta SQL: {err}")
        # Puedes añadir un rollback aquí si es una transacción
        if conn:
            conn.rollback()
        return None
    except Exception as e: # Captura cualquier otra excepción
        print(f"❌ Error general en ejecutar_sql: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return nDevolver

def ejecutar_sql_anterior(sql):
    conn = conectarBD()
    if not conn:
        print("❌ Error al conectar a la base de datos")
        return None
    else:
        print("✅✅✅✅ Conexión a la base de datos exitosa")
    cursor = conn.cursor()
    cursor.execute(sql) 
    nDevolver = None
    try:
        if not sql.lower().startswith("select"):
            conn.commit()
            if sql.lower().startswith("insert"):
                cursor.execute("SELECT LAST_INSERT_ID()")
                last_id = cursor.fetchone()[0]
                conn.close()
                print("✅ INSERT exitoso")
                nDevolver = last_id
                print("    1 ")
                #return last_id
            else:
                conn.close()
                print("✅ Consulta exitosa.")
                nDevolver = 0
                print("    2 ")
                #return 0
        else:
            print("    3 ")
            nDevolver = cursor.fetchall()
    except Exception as e:
        print(f"❌ Error en consulta segura: {e}")
        return None
    finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return nDevolver

def validar_registros_tabla(tabla, campo, id):
    sql = f"SELECT id FROM {tabla} WHERE {campo} = {id}"
    print(sql)
    rows = ejecutar_sql(sql)
    if len(rows) > 0:
        return True
    else:
        return False