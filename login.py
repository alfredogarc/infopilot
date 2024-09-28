import flet as ft
import mysql.connector
from mysql.connector import Error
from funciones.fun_basedatos import conectarbd

# Diccionario para almacenar la sesión del usuario
session_data = {}

# Función para verificar las credenciales del usuario
def verificar_usuario(login, password):
    try:
        # Conectar a la base de datos
        conexion = conectarbd()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE login = %s AND clave = %s", (login, password))
        
        # Obtener los nombres de las columnas
        columnas = [desc[0] for desc in cursor.description]
        
        # Obtener el resultado y convertirlo en un diccionario
        resultado = cursor.fetchone()
        if resultado:
            # Guardar información del usuario en la sesión
            session_data.update(dict(zip(columnas, resultado)))
            return True  # Retorna True si el usuario existe
        return False  # Retorna False si el usuario no existe
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

# Función principal de la aplicación
def Login(page):
    page.title = "Login de Usuario"
    
    # Campos de entrada
    login_input = ft.TextField(label="Login", width=300)
    password_input = ft.TextField(label="Password", password=True, width=300, can_reveal_password = True)
    clave_invalida = ft.Text("")

    mensaje = ft.Column()

    # Función para manejar el evento de login
    def on_login_click(e):
        login = login_input.value
        password = password_input.value

        if verificar_usuario(login, password):

            fila = ft.Row(
                controls=[
                    ft.Text("¡ Bienvenido "), 
                    ft.Text(session_data['nombrecompleto'], color = ft.colors.GREEN), 
                    ft.Text("!")
                ]
            )
            mensaje.controls.append(fila) 
            page.overlay.append(ft.SnackBar(ft.Text("")))
            page.overlay.append(ft.SnackBar(ft.Text("¡Login exitoso!")))
            page.update()
            # Aquí puedes redirigir a otra pantalla si es necesario
        else:
            page.overlay.append(ft.SnackBar(ft.Text("Credenciales incorrectas. Intenta de nuevo.")))
            page.update()

    # Botón de login
    login_button = ft.ElevatedButton(text="Iniciar Sesión", on_click=on_login_click)
    
    # Opción para crear un nuevo usuario
    create_user_button = ft.TextButton(text="Crear nuevo usuario", on_click=lambda e: page.add(ft.Text("Aquí iría la pantalla de registro.")))
    
    # Agregar elementos a la página
    page.add(login_input, password_input, login_button, create_user_button, mensaje, clave_invalida)

ft.app(target=Login)
