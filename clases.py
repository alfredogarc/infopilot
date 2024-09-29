import asyncio
import flet as ft
from datetime import datetime

class Usuario:
    def __init__(self, nombre, perfil):
        self.nombre = nombre
        self.perfil = perfil

    def mostrar_usuario(self, page):
        contenedor = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(f"Nombre: {self.nombre}", size=16, weight="bold", text_align=ft.TextAlign.CENTER),
                    ft.Text(f"Perfil: {self.perfil}", size=12, text_align=ft.TextAlign.CENTER)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2
            ),
            padding=10,
            border=ft.border.all(2, ft.colors.GREEN_ACCENT),
            bgcolor=ft.colors.TRANSPARENT,
            width=230,
            height=60,
            alignment=ft.alignment.center
        )
        page.add(contenedor)
        page.update()

class FechaHora:
    def __init__(self):
        self.fecha_txt = ft.Text("", text_align=ft.TextAlign.CENTER, key="fecha", size=16)
        self.hora_txt = ft.Text("", text_align=ft.TextAlign.CENTER, key="hora", size=12)

    def mostrar_fecha_hora(self, page):
        # Crear un contenedor para mostrar la fecha y la hora
        fecha_hora_container = ft.Container(
            content=ft.Column(
                controls=[
                    self.fecha_txt,
                    self.hora_txt
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2
            ),
            padding=10,
            border=ft.border.all(2, ft.colors.BLUE_ACCENT),
            bgcolor=ft.colors.TRANSPARENT,
            width=120,
            height=60,
            alignment=ft.alignment.center
        )
        
        page.add(fecha_hora_container)
        page.update()  # Asegúrate de que el control se haya agregado a la página

        # Función para actualizar la fecha y la hora
        while True:
            ahora = datetime.now()
            fecha = ahora.strftime("%d/%m/%Y")  # Formato de fecha
            hora = ahora.strftime("%I:%M:%S %p")  # Formato de hora en HH:MM:SS AM/PM
            self.fecha_txt.value = fecha
            self.hora_txt.value = hora
            page.update()  # Actualiza la página para reflejar los cambios
            asyncio.sleep(1)  # Esperar 1 segundo antes de la próxima actualización

def main(page):
    page.title = "Perfil de Usuario"
    
    # Crear un usuario de ejemplo
    usuario = Usuario("Juan Pérez", "Administrador")
    usuario.mostrar_usuario(page)
    
    # Crear y mostrar la fecha y hora
    fh = FechaHora()
    asyncio.create_task(fh.mostrar_fecha_hora(page))
    datos = ft.Column(controls=[usuario, fh])
    page.add(datos)
    page.update()

ft.app(target=main)
