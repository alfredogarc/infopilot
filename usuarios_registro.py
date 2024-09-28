import flet as ft
import mysql.connector
from funciones.fun_basedatos import conectarbd
from funciones.fotos import crear_widget_imagen

# Función para obtener grupos de usuarios
def obtener_grupos():
    con = conectarbd()
    cursor = con.cursor()
    cursor.execute("SELECT id, nombre FROM grupousuario")
    grupos = cursor.fetchall()
    con.close()
    return grupos

# Función para registrar un nuevo usuario
def registrar_usuario(e):
    # Aquí puedes agregar la lógica para insertar el nuevo usuario en la base de datos
    print("Usuario registrado con éxito.")
    # Puedes acceder a los valores de los campos usando e.control

def main(page):
    page.title = "Registro de Usuarios"

    # Obtener grupos de usuarios
    grupos = obtener_grupos()
    grupo_options = [ft.dropdown.Option(nombre) for id, nombre in grupos]

    # Crear el formulario
    formulario = ft.Column(
        controls=[
            ft.Column(
                controls=[
                    ft.TextField(label="Cédula"),
                    ft.TextField(label="Apellido"),
                    ft.TextField(label="Nombre"),
                ]
            ),
            crear_widget_imagen(page, False, True), 
            ft.TextField(label="Login"),
            ft.TextField(label="Clave", password=True),
            ft.TextField(label="Teléfono"),
            ft.TextField(label="Dirección"),
            ft.Dropdown(label="Tipo de Usuario", options=grupo_options),
            ft.FilePicker(),  # Eliminado el argumento 'label'
            ft.ElevatedButton("Registrar", on_click=registrar_usuario), 
        ]
    )

    page.add(formulario)

ft.app(target=main)
