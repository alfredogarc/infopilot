import flet as ft
from datetime import datetime
import time
import asyncio

def mostrar_fecha_hora(page):
    # Crear un contenedor para mostrar la fecha y la hora
    ahora = datetime.now()
    fecha = ahora.strftime("%d/%m/%Y")  # Formato de fecha
    hora = ahora.strftime("%I:%M:%S %p")  # Formato de hora en HH:MM:SS AM/PM
    fecha_text = ft.Text(fecha, size=16, text_align=ft.TextAlign.CENTER, key="fecha")
    hora_text = ft.Text(hora, size=12, text_align=ft.TextAlign.CENTER, key="hora")

    fecha_hora_container = ft.Container(
        content=ft.Column(
            controls=[
                fecha_text,
                hora_text
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
    page.update()  # Ensure the control has been added to the page

    # Función para actualizar la fecha y la hora
    def actualizar_fecha_hora():
        while True:
            ahora = datetime.now()
            fecha = ahora.strftime("%d/%m/%Y")  # Formato de fecha
            hora = ahora.strftime("%I:%M:%S %p")  # Formato de hora en HH:MM:SS AM/PM
            fecha_txt = ft.Text(f"{fecha}")  # Formato de fecha
            hora_txt = ft.Text(f"{hora}")  # Formato de hora en HH:MM:SS AM/PM
            print(hora, end='\r')
            page.update()
            asyncio.sleep(1)  # Esperar 1 segundo antes de la próxima actualización
            #time.sleep(1)

    asyncio.create_task(actualizar_fecha_hora())
    #actualizar_fecha_hora()

def main(page):
    page.title = "Hora"
    mostrar_fecha_hora(page)
    
ft.app(target=main)