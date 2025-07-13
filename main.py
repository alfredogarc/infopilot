import locale
import flet as ft
import warnings
import os
from conectarbd import ejecutar_sql
from variables_globales import assets_dir, upload_dir, usuario_logueado, aplicar_tema_a_pagina, colores, estilos
from funciones import obtener_ip_local
from menu import Menu
from tema import aplicar_estilo, crear_gradiente_lineal
from fastapi import FastAPI
from fastapi.responses import FileResponse
import flet.fastapi
from estilos_modernos import (
    COLORES_MODERNOS, 
    crear_boton_moderno,
    crear_campo_moderno,
    aplicar_tema_moderno_a_pagina
)

# Importar los nuevos estilos modernos
from estilos_modernos import (
    COLORES_MODERNOS, 
    ESTILOS_COMPONENTES,
    crear_boton_moderno,
    aplicar_tema_moderno_a_pagina
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(PROJECT_ROOT, "storage", "data")

warnings.filterwarnings("ignore", message="remove second argument of ws_handler")

class LoginView:
    def __init__(self, page: ft.Page, on_login_success):
        self.page = page
        self.on_login_success = on_login_success
        self.ip = obtener_ip_local()
        self.idusuario = 0
        self.setup_ui()

    def setup_ui(self):
        aplicar_tema_moderno_a_pagina(self.page)
        self.main_container = ft.Container(
            width=400,
            height=500,
            border_radius=12,  # Más redondeado
            bgcolor=COLORES_MODERNOS["fondo_secundario"],  # Color moderno
            border=ft.border.all(1, COLORES_MODERNOS["borde_sutil"]),
            padding=30,  # Más espaciado
        )
        #self.main_container = ft.Container(
        #    width=400,
        #    height=500,
        #    border_radius=10,
        #    bgcolor=COLORES_MODERNOS["fondo_secundario"],
        #    border=ft.border.all(1, COLORES_MODERNOS["borde_sutil"]),
        #    padding=20,
        #)
        user_icon = ft.Container(
            content=ft.Icon(name=ft.Icons.PERSON_OUTLINE, size=80, color=colores["texto_claro"]),
            margin=ft.margin.only(top=20)
        )
        title = ft.Text("InfoPilot", size=30, color=colores["texto_claro"], weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        self.username_input = crear_campo_moderno(
            label="Usuario",
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            width=340,
            on_submit=self.try_login
        )
        #self.username_input = ft.TextField(
        #    label="Usuario",
        #    width=300,
        #    bgcolor=colores["texto_claro"],
        #    border_color=colores["primario"],
        #    focused_border_color=colores["acento"],
        #    cursor_color=colores["secundario"],
        #    border_radius=8,
        #    prefix_icon=ft.Icons.PERSON_OUTLINE,
        #    label_style=ft.TextStyle(
        #        color=ft.Colors.BLUE_GREY_700,  # Color del texto de la etiqueta
        #        weight=ft.FontWeight.BOLD,  # Hacer el texto más grueso
        #        size=18,  # Tamaño del texto
        #    ),
        #    text_style=ft.TextStyle(
        #        color=colores["primario"],  # Color del texto ingresado
        #        size=14,
        #    ),
        #)
        self.password_input = crear_campo_moderno(
            label="Contraseña",
            password=True,  
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            width=340,
            on_submit=self.try_login
        )
        #self.password_input.can_reveal_password = False

        #self.password_input = ft.TextField(
        #    label="Contraseña",
        #    password=True,
        #    can_reveal_password=True,
        #    width=300,
        #    bgcolor=colores["texto_claro"],
        #    border_color=colores["primario"],
        #    focused_border_color=colores["acento"],
        #    cursor_color=colores["secundario"],
        #    border_radius=8,
        #    prefix_icon=ft.Icons.LOCK_OUTLINE,
        #    label_style=ft.TextStyle(
        #        color=ft.Colors.BLUE_GREY_700,  # Color del texto de la etiqueta
        #        weight=ft.FontWeight.BOLD,  # Hacer el texto más grueso
        #        size=18,  # Tamaño del texto
        #    ),
        #    text_style=ft.TextStyle(
        #        color=colores["primario"],  # Color del texto ingresado
        #        size=14,
        #    ),
        #    on_submit=self.try_login
        #)
        self.login_button = crear_boton_moderno(
            "Iniciar Sesión",
            color_fondo=COLORES_MODERNOS["azul_primario"],
            ancho=320,
            alto=50,
            on_click=self.try_login
        )
        self.mensaje = ft.Text("", size=14, color=ft.Colors.YELLOW, visible=False)

        if self.ip == "192.168.1.106":
            self.username_input.value = "alfredogarc"
            self.password_input.value = "1111"

        login_column = ft.Column(
            controls=[user_icon, title, ft.Container(height=20), self.username_input, self.password_input, ft.Container(height=10), self.login_button, self.mensaje],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        self.main_container.content = login_column
        self.content = ft.Container(content=self.main_container, alignment=ft.alignment.center, expand=True)

    def try_login(self, _):
        username = self.username_input.value
        password = self.password_input.value
        sql = f"SELECT us.id, trim(concat(us.nombre, ' ', us.apellido)) as usuario, us.idgrupo, gr.nombre as grupo FROM usuarios us LEFT JOIN grupousuario gr ON us.idgrupo = gr.id WHERE us.login = '{username}' AND us.clave = '{password}'"
        result = ejecutar_sql(sql)
        
        if result:
            self.page.session.set("usuario_logueado", username)
            self.page.session.set("idusuario", result[0][0])
            self.page.session.set("usuario_nombre", result[0][1])
            self.page.session.set("idgrupo", result[0][2])
            self.page.session.set("grupo", result[0][3])
            self.mensaje.visible = False
            self.on_login_success()
        else:
            self.mensaje.value = "Usuario o contraseña incorrectos"
            self.mensaje.visible = True
        self.page.update()

def main(page: ft.Page):
    locale.setlocale(locale.LC_TIME, 'Spanish_Chile')
    
    #page.theme_mode = ft.ThemeMode.LIGHT

    # Aplicar el tema global a la página
    #aplicar_tema_a_pagina(page)
    
    usuario_logueado = page.session.get("usuario_logueado")
    print("Usuario logueado al iniciar:", usuario_logueado)

    # Definimos el fondo con dimensiones explícitas
    background = ft.Container(
        content=ft.Image(
            src="fondo2.jpg",
            fit=ft.ImageFit.COVER,  # Cubre todo el espacio
            repeat=ft.ImageRepeat.NO_REPEAT,
        ),
        width=page.width,  # Usamos el ancho de la página
        height=page.height,  # Usamos el alto de la página
        expand=True,  # Aseguramos que se expanda
    )
    src="https://dvzpv6x5302g1.cloudfront.net/AcuCustom/Sitename/DAM/086/Hempel_drone_inspection_Hempelweby_Main.jpg",
    #src="http://s.ekabu.ru/localStorage/post/c6/a7/b5/76/c6a7b576_resizedScaled_740to493.jpg",

    def download(e, archivo):
        download_url = f"/download/sounds/{archivo}"
        print(f"Iniciando descarga desde: {download_url}")
        page.launch_url(download_url)

    def show_main_view():
        page.clean()
        # Usamos una Stack para apilar el fondo y el menú
        stack = ft.Stack(
            controls=[
                background,  # Fondo que cubre toda la pantalla
                ft.Container(
                    content=Menu(page).content,  # Menú superpuesto
                    expand=True,
                )
            ],
            width=page.width,  # Ancho completo de la página
            height=page.height,  # Alto completo de la página
            expand=True,  # Expandimos el Stack
        )
        page.add(stack)
        page.scroll = True
        page.update()

    def show_login_view():
        page.clean()
        login_view = LoginView(page, show_main_view)
        page.add(login_view.content)
        page.update()

    if not usuario_logueado:
        show_login_view()
    else:
        show_main_view()


def prepare_file(relative_path):
    # Construye la ruta completa al archivo usando la estructura del proyecto
    full_path = os.path.join(STORAGE_DIR, relative_path)
    print(f"Buscando archivo en: {full_path}")

    # Verifica que el archivo exista
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"No se encontró el archivo: {full_path}")

    return full_path

# Configuración de FastAPI
app = FastAPI()

@app.get("/download/{file_path:path}")
def download_file(file_path: str):
    try:
        file_to_download = prepare_file(file_path)
        filename = os.path.basename(file_to_download)

        print(f"Sirviendo archivo: {file_to_download} como {filename}")

        return FileResponse(
            file_to_download,
            media_type="audio/mpeg",
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        print(f"Error en la descarga: {str(e)}")
        return {"error": str(e)}

# Montar la aplicación Flet
#api.mount("/", flet.fastapi.app(main,assets_dir=assets_dir, upload_dir=upload_dir, use_color_emoji=True))

if __name__ == "__main__":
    #import uvicorn

    #uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
    ft.app(target=main, assets_dir=assets_dir, upload_dir=upload_dir, use_color_emoji=True)