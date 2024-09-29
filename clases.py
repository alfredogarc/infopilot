import asyncio
import flet as ft
import time
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

class FechaHora(ft.Container):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Crear un contenedor para mostrar la fecha y la hora
        ahora = datetime.now()
        fecha = ahora.strftime("%d/%m/%Y")  # Formato de fecha
        hora = ahora.strftime("%I:%M:%S %p")  # Formato de hora en HH:MM:SS AM/PM
        self.fecha_text = ft.Text(fecha, size=16, text_align=ft.TextAlign.CENTER, key="fecha")
        self.hora_text = ft.Text(hora, size=12, text_align=ft.TextAlign.CENTER, key="hora")

        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    self.fecha_text,
                    self.hora_text
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
    
    def did_mount(self):
        self.running = True
        asyncio.create_task(self.actualizar_fecha_hora())
    def will_unmount(self):
        self.running = False
    # Función para actualizar la fecha y la hora
    def actualizar_fecha_hora(self):
        while self.running:
            ahora = datetime.now()
            fecha = ahora.strftime("%d/%m/%Y")  # Formato de fecha
            hora = ahora.strftime("%I:%M:%S %p")  # Formato de hora en HH:MM:SS AM/PM
            self.fecha_text.value = f"{fecha}"  # Formato de fecha
            self.hora_text.value = f"{hora}"  # Formato de hora en HH:MM:SS AM/PM
            #print(hora, end='\r')
            asyncio.sleep(1)  # Esperar 1 segundo antes de la próxima actualización
            #time.sleep(1)
            self.update()

def main(page):
    page.title = "Perfil de Usuario"
    
    # Crear un usuario de ejemplo
    usuario = Usuario("Juan Pérez", "Administrador")
    usuario.mostrar_usuario(page)
    
    # Crear y mostrar la fecha y hora
    #fh = FechaHora()
    page.add(FechaHora())
    #asyncio.create_task(fh.mostrar_fecha_hora(page))
    #datos = ft.Column(controls=[usuario, fh])
    #page.add(datos)
    page.update()

ft.app(target=main)
