from ast import Lambda
from gc import enable
from math import e
from pydoc import describe
#from sys import deactivate_stack_trampoline
from tkinter import CENTER
import flet as ft
from conectarbd import ejecutar_sql, delete_record, nuevo_registro, editar_registro, validar_registros_tabla
# Cambiar la importación de SubirArchivo a SubirArchivoManager
from subir_archivo import SubirArchivoManager
from datetime import datetime, time, timedelta
from funciones import calcular_horas_diferencia, validar_enteros, format_timedelta, format_time, parse_time_string, validar_correos, grabar_en_disco, enviar_correo
from imagen_dibujable import ImagenDibujable
from variables_globales import assets_dir, upload_dir, color_names
import warnings
import os
import pyperclip
import flet.canvas as cv
import base64
from imprimir.reporte_redes import Imprimir_Informe_Redes
from reportlab.lib.pagesizes import letter
import asyncio
from estilos_modernos import (
    COLORES_MODERNOS,
    crear_dropdown_moderno,
    crear_boton_moderno,
    crear_contenedor_moderno,
    crear_texto_moderno,
    crear_tabla_moderna, 
    crear_campo_moderno,
)

warnings.filterwarnings("ignore", message="remove second argument of ws_handler")

class InformeRedesUI(ft.Container):
    def __init__(self, page: ft.Page, nIDSolicitud: int):
        self.page = page
        self.nIDSolicitud = nIDSolicitud
        self.jaula_buttons = []
        self.altura_combos = 40
        # Reemplazar SubirArchivo con SubirArchivoManager
        self.imagen_subir = SubirArchivoManager(self.page, allowed_extensions=["png", "jpg", "jpeg", "gif"])
        self.initialize_ui()

    def initialize_ui(self):
        #self.page.clean()
        self.selected_files = ft.Text("")
        self.entidad = "solicitudes"
        self.caption = "Informe Redes"
        self.snackBar = ft.SnackBar(
            content=ft.Text("", color=ft.Colors.YELLOW),
            duration=5000,
            show_close_icon=True,
            close_icon_color=ft.Colors.RED
        )
        self.page.overlay.append(self.snackBar)
        self.titulo = ft.Text(f"{self.caption} N° {self.nIDSolicitud}", size=20)
        self.jaula_seleccionada = ""
        self.jaula_seleccionada_id = 0
        self.nRegistros = 0
        self.fecha_indicada = datetime.now()

        # TAB 1
        self.hora_desde = ft.TimePicker(
            confirm_text="Confirmar",
            error_invalid_text="Hora inválida",
            help_text="Seleccione la hora desde",
            on_change=self.actualizar_hora_desde,
        )
        self.hora_hasta = ft.TimePicker(
            confirm_text="Confirmar",
            error_invalid_text="Hora inválida",
            help_text="Seleccione la hora hasta",
            on_change=self.actualizar_hora_hasta,
        )
        self.btn_hora_desde = ft.ElevatedButton(
            "Hora desde",
            icon=ft.Icons.ACCESS_TIME,
            on_click=lambda _: self.page.open(self.hora_desde),
            bgcolor=COLORES_MODERNOS['azul_primario'],
            color="white",
            icon_color="white",
            tooltip="Hora inicio"            
        )
        self.btn_hora_hasta = ft.ElevatedButton(
            "Hora hasta",
            icon=ft.Icons.ACCESS_TIME,
            on_click=lambda _: self.page.open(self.hora_hasta),
            bgcolor=COLORES_MODERNOS['azul_primario'],
            color="white",
            icon_color="white",
            tooltip="Hora fin"  
        )
        self.hora_diferencia = ft.Text("")
        self.hora_diferencia_elegido = ""
        self.hora_desde_elegida = timedelta(hours=0, minutes=0)
        self.hora_hasta_elegida = timedelta(hours=0, minutes=0)

        self.Realizo_trabajos = ft.Checkbox(label="Realizó trabajos")
        self.cbo_empresa = crear_dropdown_moderno(
            label="Empresa",
            options_data=[(str(id), nombre) for id, nombre in ejecutar_sql("SELECT id, nombre FROM empresas")],
            prefix_icon=ft.Icons.BUSINESS,
            visible=True,
            width="100%",
            height=self.altura_combos,
        )
        #ft.Dropdown(label="Empresa", options=[ft.dropdown.Option(str(id), nombre) for id, nombre in ejecutar_sql("SELECT id, nombre FROM empresas")])
        self.cbo_centros = self.cbo_centros = crear_dropdown_moderno(
            label="Centro",
            options_data=[(str(id), centro) for id, centro in ejecutar_sql("SELECT id, centro FROM centros")],
            prefix_icon=ft.Icons.LOCATION_CITY,
            visible=True,
            width="100%",
            height=self.altura_combos,
        )
        #ft.Dropdown(label="Centro", options=[ft.dropdown.Option(str(id), centro) for id, centro in ejecutar_sql("SELECT id, centro FROM centros")])
        self.num_jaulas = crear_campo_moderno(label = "# Jaulas", prefix_icon = ft.Icons.SQUARE_OUTLINED, width=120 )
        self.desde = crear_campo_moderno(label = "Desde", prefix_icon = ft.Icons.NUMBERS, width=120 )
        #ft.TextField(label="# Jaulas")
        #ft.TextField(label="Desde")

        # TAB 2
        self.Urgente = ft.Checkbox(label="Urgente")
        
        self.asunto = crear_campo_moderno(label = "Asunto:", prefix_icon = ft.Icons.SUBJECT, width="100%" )
        self.para = crear_campo_moderno(label = "Para:", prefix_icon = ft.Icons.PERM_CONTACT_CALENDAR_ROUNDED, width="100%" )

        #self.asunto = ft.TextField(label="Asunto:", icon=ft.Icons.SUBJECT, text_size=13, height=30)
        #self.para = ft.TextField(label="Para:", icon=ft.Icons.EMAIL_SHARP, text_size=13, height=30)
        self.para_anterior = ""
        #crear_campo_moderno(label="Cuerpo:", prefix_icon=ft.Icons.DESCRIPTION, multilinea=True, min_l=3, max_l=6, expandir=True, width="100%")
        self.cuerpo = crear_campo_moderno(label="Cuerpo:", prefix_icon=ft.Icons.DESCRIPTION, width="100%", estilo = "input_memo")
        #self.cuerpo = ft.TextField(label="Cuerpo:", icon=ft.Icons.DESCRIPTION, multiline=True, min_lines=3, max_lines=6, text_size=13)
        self.lista_archivos = ft.Row(wrap=True, spacing=10, run_spacing=10)
        self.archivos = []
        self.archivo1 = ""
        self.archivo_nombre1 = ""
        self.archivo2 = ""
        self.archivo_nombre2 = ""
        self.archivo3 = ""
        self.archivo_nombre3 = ""
        self.archivo4 = ""
        self.archivo_nombre4 = ""
        # Reemplazar SubirArchivo con SubirArchivoManager
        self.subir_adjunto = SubirArchivoManager(self.page, allowed_extensions=["*"])
        self.datos_correo = ft.ListView()
        self.contenedor_correo = ft.Container()

        # TAB 3
        self.zoom_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Vista Ampliada"),
            content=ft.Image(
                src_base64=None,
                width=500,
                height=500,
                fit=ft.ImageFit.CONTAIN,
            ),
            actions=[
                crear_boton_moderno("Cerrar", color_fondo = COLORES_MODERNOS["rojo_cerrar"], on_click = lambda e: self.close_zoom(), icono = ft.Icons.EXIT_TO_APP)
                #ft.TextButton("Cerrar", on_click=lambda e: self.close_zoom())
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(self.zoom_dialog)

        self.jaulas_rows = []
        self.opciones_jaula = ft.RadioGroup(
            value="tapa",  # Valor predeterminado
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Radio(value="tapa", label="Jaula con Tapa"),
                    ft.Radio(value="separador", label="Jaula con Separador"),
                    ft.Radio(value="sin_separador", label="Jaula sin Separador"),
                ],
            ),
            on_change=self.cambiar_tipo_jaula  # Función que se ejecutará cuando cambie la selección
        )
        self.opciones_jaula_container = ft.Container(
            content=self.opciones_jaula,
            border=ft.border.all(1, ft.Colors.GREY_400),  # Ancho 1, color gris
            border_radius=10,  # Bordes redondeados
            padding=10,  # Espacio interno
            margin=5,   # Espacio externo
        )
        self.tipo_seleccionado = ""

        self.jaula_izq = ImagenDibujable(src_64="", ancho=500, alto=500)
        self.jaula_der = ImagenDibujable(src_64="", ancho=500, alto=500)
        # Reemplazar SubirArchivo con SubirArchivoManager
        self.subir_archivo = SubirArchivoManager(self.page, allowed_extensions=["png", "jpg", "jpeg", "gif"])
        self.image_container_izq = ft.Container(
            content=self.jaula_izq,
            height=500,
            width=500,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            padding=10,
            expand=True,
            visible=False
        )
        self.image_container_der = ft.Container(
            content=self.jaula_der,
            height=500,
            width=500,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            padding=10,
            expand=True,
            visible=False
        )

        self.image_container_izq.on_tap_down = lambda e: self.al_tocar_imagen_sync(e, True)
        self.image_container_der.on_tap_down = lambda e: self.al_tocar_imagen_sync(e, False)

        self.markers_container_izq = ft.Column()
        self.markers_container_der = ft.Column()
        self.posiciones_clic_izq = []
        self.posiciones_clic_der = []

        self.tab_jaula_izq = ft.Tab(
            text="Jaula Izquierda",
            content=ft.Column(
                [
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),  # Corrige aquí
                    ft.Row(
                        [
                            ft.Container(
                                content=self.image_container_izq,
                                width=500,
                                height=500,
                                alignment=ft.alignment.center
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("Marcadores:", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Container(
                                            content=self.markers_container_izq,
                                            expand=True,
                                            # scroll=ft.ScrollMode.AUTO
                                        )
                                    ],
                                    expand=True
                                ),
                                width=900,
                                expand=True
                            ),
                        ],
                        expand=True,
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.START
                    )
                ]
            )
        )

        self.tab_jaula_der = ft.Tab(
            text="Jaula Derecha",
            content=ft.Column(
                [
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),  # Corrige aquí
                    ft.Row(
                        [
                            ft.Container(
                                content=self.image_container_der,
                                width=500,
                                height=500,
                                alignment=ft.alignment.center
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("Marcadores:", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Container(
                                            content=self.markers_container_der,
                                            expand=True,
                                            # scroll=ft.ScrollMode.AUTO
                                        )
                                    ],
                                    expand=True
                                ),
                                width=900,
                                expand=True
                            ),
                        ],
                        expand=True,
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.START
                    )
                ]
            )
        )

        self.imagen_original_izq = ""
        self.imagen_original_der = ""
        self.posiciones_clic_izq = []
        self.posiciones_clic_der = []
        self.color_seleccionado = ""
        self.anomalia_seleccionada = ""
        self.estado_seleccionado = ""
        self.sector_seleccionado = ""
        self.seleccione_un_color = ft.Text("Seleccione un color:", size=20, color=ft.Colors.GREEN)
        self.color_buttons = []
        self.selected_color = None

        self.btn_posiciones_izq = []
        self.edt_posicion_izq = ft.TextField(
            "", 
            hint_text="Comentario", 
            multiline=True, 
            max_lines=10, 
            min_lines=3, 
            on_change = lambda e: self.grabar_descripcion(e)
        )

        self.btn_posiciones_der = []
        self.edt_posicion_der = ft.TextField(
            "", 
            hint_text="Comentario", 
            multiline=True, 
            max_lines=10, 
            min_lines=3, 
            on_change = lambda e: self.grabar_descripcion(e)
        )

        colors = ejecutar_sql("SELECT color, nombre, id FROM anomalias ORDER BY color ASC, nombre ASC")
        
        for color_tuple in colors:
            color = color_tuple[0]  # Extraemos el primer elemento de la tupla
            anomalia = color_tuple[1]
            idanomalia = color_tuple[2]
            if color is not None:
                # Convertimos el color a hexadecimal si es un número
                color_hex = color.lower()
                if color.startswith('#'):
                    color_normalized = color.lower().lower()
                else:
                    color_normalized = f"#{color}".lower()
                
                # Obtener el nombre del color del diccionario
                nombre_color = color_names.get(color_normalized)
                
                # Si no se encuentra, intentar con otras normalizaciones
                if nombre_color is None:
                    # Intentar sin el símbolo #
                    nombre_color = color_names.get(color_normalized.replace('#', ''))
                    
                # Si aún no se encuentra, usar un nombre genérico
                if nombre_color is None:
                    nombre_color = color_hex
                else:
                    nombre_color = nombre_color
                    
                button = ft.ElevatedButton(
                    content=ft.Text(
                        anomalia, color=(ft.Colors.BLACK if color == "yellow" else ft.Colors.WHITE) , size=10,
                        max_lines=3,  # Asegurar que el texto sea de una sola línea
                        #overflow=ft.TextOverflow.CLIP
                    ),
                    bgcolor=color_hex,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.padding.symmetric(horizontal=10, vertical=5),  # Padding para mejor apariencia
                    ),
                    on_click=lambda e, color = color_hex: self.select_color(e,color), 
                    tooltip=f"{anomalia} / {nombre_color}",
                    data = idanomalia,
                    width=50
                )
                self.color_buttons.append(button)

        self.selected_color_text = ft.Text("")

        self.color_buttons_grid = ft.GridView(
            controls=self.color_buttons,
            runs_count=14,  # Número exacto de columnas
            max_extent=None,  # Tamaño máximo de cada celda (ajusta según necesites)
            spacing=5,  # Espacio entre celdas horizontalmente
            run_spacing=5,  # Espacio entre filas
            padding=5,  # Padding interno
            width="100%",  # Ancho fijo para el contenedor
            height=None,  # Altura automática basada en el contenido
            expand=False,  # No expandir para llenar el espacio disponible
        )
        self.btn_colores = ft.Column([
            self.seleccione_un_color,
            ft.Row(self.color_buttons, alignment=ft.MainAxisAlignment.CENTER, wrap=True),
        ])

        self.faena_realizada = crear_campo_moderno(label="Faena", prefix_icon=ft.Icons.DESCRIPTION,estilo="input_memo", width="100%", tooltip="Faena realizada")
        #ft.TextField(label="Faena Realizada", icon=ft.Icons.DESCRIPTION, multiline=True, min_lines=1, max_lines=6, text_size=13)
        self.cbo_anomalias = crear_dropdown_moderno(
            label="Anomalía:",
            options_data=[(str(id), nombre, color) for id, nombre, color in ejecutar_sql("SELECT id, nombre, color FROM anomalias")],
            on_change=self.on_change_anomalia,
            prefix_icon=ft.Icons.SMS_FAILED,
            height=self.altura_combos,
        )
        #ft.Dropdown(
        #    label="Anomalía:",
        #    options=[
        #        ft.dropdown.Option(
        #            key=str(id),
        #            text=nombre,
        #            data=color
        #        ) for id, nombre, color in ejecutar_sql("SELECT id, nombre, color FROM anomalias")
        #    ],
        #    on_change = self.on_change_anomalia
        #)
        self.cbo_sector = crear_dropdown_moderno(
            label="Sector",
            options_data=[(str(id), nombre) for id, nombre in ejecutar_sql("SELECT id, nombre FROM sector ORDER BY nombre")],
            on_change=self.on_change_sector,
            prefix_icon="🚦",
            visible=True,
            height=self.altura_combos,
        )
        #ft.Dropdown(
        #    #on_change=lambda e, i=id: print(f"color: {e.control.data} y nombre: {e.control.value} e ID: {i}"),
        #    label="Sector:",
        #    options=[
        #        ft.dropdown.Option(
        #            key=str(id),
        #            text=nombre,
        #        ) for id, nombre in ejecutar_sql("SELECT id, nombre FROM sector")
        #    ],
        #    on_change = self.on_change_sector
        #)
        self.cbo_estado = crear_dropdown_moderno(
            label="Estado",
            options_data=[(str(id), nombre) for id, nombre in ejecutar_sql("SELECT id, nombre FROM estado ORDER BY nombre ASC")],
            on_change=self.on_change_estado,
            prefix_icon=ft.Icons.REAL_ESTATE_AGENT_ROUNDED,
            visible=True,
            height=self.altura_combos,
        )
        #ft.Dropdown(
        #    #on_change=lambda e, i=id: print(f"color: {e.control.data} y nombre: {e.control.value} e ID: {i}"),
        #    label="Estado:",
        #    options=[
        #        ft.dropdown.Option(
        #            key=str(id),
        #            text=nombre,
        #        ) for id, nombre in ejecutar_sql("SELECT id, nombre FROM estado")
        #    ],
        #   on_change = self.on_change_estado
        #)
        
        self.jaulas = ft.Row(
            scroll=ft.ScrollMode.AUTO,
            expand=1,
            alignment=ft.MainAxisAlignment.START
        )  # Lista para almacenar las jaulas (botones)
        self.jaula_container = ft.Container(
            content=self.jaulas
        )

        self.crear_interfaz()

    def pedir_fecha(self):
        print(f"Seleccione la fecha para el informe de redes") 
        #self.desde_hasta = desde_hasta
        self.date_picker.open = True
        self.page.update()

    def show_message(self, message):
        self.snackBar.content = ft.Text(message)
        self.snackBar.open = True
        self.page.update()

    # FUNCIONES TAB 1
    def on_change_urgente(self):
        if self.Urgente.value == True:
            self.grabar_datos_tab2()

    def cambios_jaulas(self, e):
        if validar_enteros(e):
            #print(f"     {self.num_jaulas.value}    {self.num_jaulas.data}")
            if self.num_jaulas.data is not None and int(self.num_jaulas.value) > self.num_jaulas.data:
                self.show_message("El número de jaulas no puede ser mayor al número de jaulas en el centro.")
                self.num_jaulas.value = self.num_jaulas.data
                self.num_jaulas.update()
                return
            if self.desde.data is not None and int(self.desde.value) < self.desde.data:
                self.show_message("El número de jaula desde no puede ser menor al número de jaulas en el centro.")
                self.desde.value = self.desde.data
                self.desde.update()
                return

            self.grabar_datos_tab1()
            self.registrar_jaulas_en_tabla_jaulas()
            self.crear_jaulas()
            self.page.update()

    def grabar_datos_tab1(self):
        urgente = 1 if self.Urgente.value else 0
        fecha = self.fecha_indicada
        hora_desde = self.hora_desde_elegida if self.hora_desde_elegida else 0
        hora_hasta = self.hora_hasta_elegida if self.hora_hasta_elegida else 0
        tiempo = self.hora_diferencia_elegido
        rt = 1 if self.Realizo_trabajos.value else 0
        empresa = self.cbo_empresa.value if self.cbo_empresa.value else 0
        centro = self.cbo_centros.value if self.cbo_centros.value else 0
        num_jaulas = self.num_jaulas.value if self.num_jaulas.value else 0
        desde = self.desde.value if self.desde.value else 0
        sql = f"UPDATE solicitudes SET fecha = '{fecha}', hora_inicio = '{hora_desde}', hora_fin = '{hora_hasta}', duracion = '{tiempo}', idempresa = {empresa}, idcentro = {centro}, urgente = {urgente}, realizo_trabajos = {rt}, jaulas = {num_jaulas}, jaula_desde = {desde} WHERE id = {self.nIDSolicitud}"
        ejecutar_sql(sql)

    def mostrar_datos_tab1(self):
        sql = f"SELECT id, jaulas, jaula_desde, realizo_trabajos, idempresa, idcentro, fecha, hora_inicio, hora_fin, duracion FROM solicitudes WHERE id = {self.nIDSolicitud}"
        datos = ejecutar_sql(sql)
        if datos:
            fecha = datos[0][6]
            self.fecha_button.content.controls[1].value = datetime.strftime(fecha, "%d/%m/%Y") if fecha != None else ""
            #self.fecha_button.text = datetime.strftime(fecha, "%d/%m/%Y") if fecha != None else ""
            self.fecha_indicada = fecha if fecha != None else ""
            self.num_jaulas.value = datos[0][1]
            self.desde.value = datos[0][2]
            self.num_jaulas.data = int(datos[0][1])
            self.desde.data = int(datos[0][2])

            self.Realizo_trabajos.value = False if datos[0][3] == 0 else True
            self.cbo_empresa.value = datos[0][4]
            self.cbo_centros.value = datos[0][5]

            # Horas
            self.hora_desde_elegida = datos[0][7] if datos[0][7] != None else ""
            self.btn_hora_desde.text = format_time(self.hora_desde_elegida)

            self.hora_hasta_elegida = datos[0][8] if datos[0][8] != None else ""
            self.btn_hora_hasta.text = format_time(self.hora_hasta_elegida)

            # Duración
            if datos[0][9]:
                horas, minutos = datos[0][9].split(":")
                hora = int(horas)
                min = int(minutos)
                self.hora_diferencia.value = f"Diferencia: {hora} horas y {min} minutos"
                self.hora_diferencia.color = "red" if hora < 0 or min < 0 else "green"
                self.hora_diferencia_elegido = f"{hora:02d}:{min:02d}"

            self.page.update()

    # FUNCIONES TAB 2
    def on_focus_para(self, e):
        self.para_anterior = self.para.value

    def on_blur_validar_correos(self, e):
        correos = self.para.value
        correos_invalidos = validar_correos(correos)

        if correos_invalidos:
            mensaje_error = f"Los siguientes correos son inválidos: {', '.join(correos_invalidos)}"
            self.para.value = self.para_anterior
            self.para.update()
            self.show_message(mensaje_error)
        else:
            self.show_message("Todos los correos son válidos.")

    def eliminar_archivo(self, index):
        del self.archivos[index]
        self.actualizar_lista_adjuntos()

    def actualizar_lista_adjuntos(self, Grabar: bool = True):
        self.archivo1 = ""
        self.archivo_nombre1 = ""
        self.archivo2 = ""
        self.archivo_nombre2 = ""
        self.archivo3 = ""
        self.archivo_nombre3 = ""
        self.archivo4 = ""
        self.archivo_nombre4 = ""
        self.lista_archivos.controls = [
            ft.Container(
                content=ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.FILE_PRESENT),
                                title=ft.Text(os.path.basename(archivo['nombre'])[:15], style=ft.TextStyle(weight=ft.FontWeight.BOLD)),
                                tooltip=os.path.basename(archivo['nombre']),
                                subtitle=ft.Text(f"Archivo {i+1}"),
                            ),
                            ft.Row([
                                ft.TextButton("Eliminar", on_click=lambda _, i=i: self.eliminar_archivo(i), icon=ft.Icons.DELETE, icon_color="red"),
                            ], alignment=ft.MainAxisAlignment.END)
                        ]),
                        padding=10
                    ),
                ),
                width=250,
            )
            for i, archivo in enumerate(self.archivos)
        ]
        if Grabar:
            sql = f"UPDATE solicitudes SET archivo1 = '{self.archivo1}', archivo_nombre1 = '{self.archivo_nombre1}', archivo2 = '{self.archivo2}', archivo_nombre2 = '{self.archivo_nombre2}', archivo3 = '{self.archivo3}', archivo_nombre3 = '{self.archivo_nombre3}', archivo3 = '{self.archivo3}', archivo_nombre4 = '{self.archivo_nombre4}' where id = {self.nIDSolicitud}"
            ejecutar_sql(sql)
            self.page.update()
            for i, archivo in enumerate(self.archivos):
                cI = str(i+1)
                con = f"archivo{cI}"
                arc = f"archivo_nombre{cI}"
                setattr(self, arc, os.path.basename(archivo['nombre']))
                setattr(self, con, archivo['contenido'])
                con = archivo['contenido']
                arc = os.path.basename(archivo['nombre'])
                sql = f"UPDATE solicitudes SET archivo{cI} = '{con}', archivo_nombre{cI} = '{arc}' where id = {self.nIDSolicitud}"
                ejecutar_sql(sql)

        self.btn_Subir_Adjunto.disabled = len(self.archivos) >= 4
        self.page.update()

    def mostrar_datos_tab2(self):
        sql = f"SELECT id, urgente, asunto, emails, cuerpo, archivo1, archivo_nombre1, archivo2, archivo_nombre2, archivo3, archivo_nombre3, archivo4, archivo_nombre4 FROM solicitudes WHERE id = {self.nIDSolicitud}"
        datos = ejecutar_sql(sql)
        if datos:
            self.Urgente.value = 1 if datos[0][1] else 0
            self.asunto.value = datos[0][2]
            self.para.value = datos[0][3]
            self.cuerpo.value = datos[0][4]
            self.archivo1 = datos[0][5]
            self.archivo_nombre1 = datos[0][6]
            self.archivo2 = datos[0][7]
            self.archivo_nombre2 = datos[0][8]
            self.archivo3 = datos[0][9]
            self.archivo_nombre3 = datos[0][10]
            self.archivo4 = datos[0][11]
            self.archivo_nombre4 = datos[0][12]
            self.archivos = []

            if self.archivo1:
                self.archivos.append({
                    "nombre": self.archivo_nombre1,
                    "contenido": self.archivo1
                })
            if self.archivo2:
                self.archivos.append({
                    "nombre": self.archivo_nombre2,
                    "contenido": self.archivo2
                })
            if self.archivo3:
                self.archivos.append({
                    "nombre": self.archivo_nombre3,
                    "contenido": self.archivo3
                })
            if self.archivo4:
                self.archivos.append({
                    "nombre": self.archivo_nombre4,
                    "contenido": self.archivo4
                })
            self.actualizar_lista_adjuntos(False)

            self.page.update()

    def grabar_datos_tab2(self):
        rt = 1 if self.Realizo_trabajos.value else 0
        asunto = self.asunto.value
        para = self.para.value
        cuerpo = self.cuerpo.value
        archivo1 = self.archivo1
        archivo_nombre1 = self.archivo_nombre1
        archivo2 = self.archivo2
        archivo_nombre2 = self.archivo_nombre2
        archivo3 = self.archivo3
        archivo_nombre3 = self.archivo_nombre3
        archivo4 = self.archivo4
        archivo_nombre4 = self.archivo_nombre4

        sql = f"UPDATE solicitudes SET realizo_trabajos = {rt}, asunto = '{asunto}', emails = '{para}', cuerpo = '{cuerpo}', archivo1 = '{archivo1}', archivo_nombre1 = '{archivo_nombre1}', archivo2 = '{archivo2}', archivo_nombre2 = '{archivo_nombre2}', archivo3 = '{archivo3}', archivo_nombre3 = '{archivo_nombre3}', archivo4 = '{archivo4}', archivo_nombre4 = '{archivo_nombre4}' WHERE id = {self.nIDSolicitud}"
        ejecutar_sql(sql)
    
    def grabar_datos_tab3(self):
        sql = f"UPDATE solicitudes SET faena_realizada = '{self.faena_realizada.value}' WHERE id = {self.nIDSolicitud}"
        ejecutar_sql(sql)

    def registrar_jaulas_en_tabla_jaulas(self):
        solicitud = ejecutar_sql(f"SELECT solicitudes.jaulas, solicitudes.jaula_desde, centros.jaula_izq, centros.jaula_der FROM solicitudes LEFT JOIN centros ON solicitudes.idcentro = centros.id WHERE solicitudes.id = {self.nIDSolicitud}")

        ejecutar_sql(f"DELETE FROM jaulas WHERE idsolicitud = {self.nIDSolicitud}")
        ejecutar_sql(f"DELETE FROM jaulas_detalle WHERE idsolicitud = {self.nIDSolicitud}")
        desde = int(self.desde.value)
        jaulas = int(self.num_jaulas.value)
        #desde = solicitud[0][1]
        #jaulas = solicitud[0][0]
        for i in range(1, jaulas + 1):
            sql = f"INSERT INTO jaulas (idsolicitud, jaula, jaula_imagen_izq, jaula_imagen_der) VALUES "
            sql += f"({self.nIDSolicitud}, {desde}, '{solicitud[0][2]}', '{solicitud[0][3]}')"
            ejecutar_sql(sql)
            desde = desde + 1

    
    def on_change_centros(self, e):
        if self.nIDSolicitud == 0:
            return

        sql = f"SELECT jaulas, jaula_desde, jaula_izq, jaula_der FROM centros WHERE id = {e.control.value}"
        centros = ejecutar_sql(sql)
        if centros:
            self.num_jaulas.data = int(centros[0][0])
            self.num_jaulas.value = centros[0][0]
            self.desde.value = centros[0][1]

            self.num_jaulas.data = int(centros[0][0])
            self.desde.data = int(centros[0][1])
            

            self.grabar_datos_tab1()
            self.registrar_jaulas_en_tabla_jaulas()
            self.crear_jaulas()
            self.page.update()

    def actualizar_fecha(self, e):
        fecha = e.control.value
        fecha_formateada = datetime.strftime(fecha, "%d/%m/%Y")
        self.fecha_button.content.controls[1].value = fecha_formateada
        self.fecha_indicada = fecha
        self.grabar_datos_tab1()
        self.page.update()

    def actualizar_hora_desde(self, e):
        if not e.control.value:
            return

        self.hora_desde_elegida = e.control.value
        self.btn_hora_desde.text = format_time(self.hora_desde_elegida)
        self.btn_hora_desde.update()

        # Calcular diferencia solo si ambas horas están establecidas
        if self.hora_desde_elegida and self.hora_hasta_elegida:
            hora, minuto, mensaje = calcular_horas_diferencia(
                self.hora_desde_elegida,
                self.hora_hasta_elegida
            )
            self.hora_diferencia.value = mensaje
            self.hora_diferencia.color = "red" if hora < 0 or minuto < 0 else "green"
            self.hora_diferencia_elegido = f"{hora:02d}:{minuto:02d}"
            self.hora_diferencia.update()

        self.grabar_datos_tab1()

    def actualizar_hora_hasta(self, e):
        if not e.control.value:
            return

        self.hora_hasta_elegida = e.control.value
        self.btn_hora_hasta.text = format_time(self.hora_hasta_elegida)
        self.btn_hora_hasta.update()

        # Calcular diferencia solo si ambas horas están establecidas
        if self.hora_desde_elegida and self.hora_hasta_elegida:
            hora, minuto, mensaje = calcular_horas_diferencia(
                self.hora_desde_elegida,
                self.hora_hasta_elegida
            )
            self.hora_diferencia.value = mensaje
            self.hora_diferencia.color = "red" if hora < 0 or minuto < 0 else "green"
            self.hora_diferencia_elegido = f"{hora:02d}:{minuto:02d}"
            self.hora_diferencia.update()

        self.grabar_datos_tab1()

    # FUNCIONES TAB 2
    def on_change_realizo_trabajo(self):
        if self.Realizo_trabajos.value == True:
            self.cuerpo.value = """
Estimados

    Junto con saludar, informo que el día de hoy no se realizó labores de inspección submarina, envío Registro de cese de actividades (RCA) perteneciente al día de hoy, se adjunta enlace de puerto cerrado.

https://sitport.directemar.cl/#/general

Saludos Cordiales 

Giovanni Caripan
    """
            self.cuerpo.update()
            self.grabar_datos_tab1()

    # FUNCIONES TAB 3
    def close_zoom(self):
        self.zoom_dialog.open = False
        self.page.update()
    
    def show_image_zoom(self, current_image_path):
        if current_image_path:
            self.zoom_dialog.content.src_base64 = current_image_path
            self.page.dialog = self.zoom_dialog
            self.zoom_dialog.open = True
            self.page.update()
        else:
            print("No hay imagen válida para mostrar en zoom")  # Debug

    def cambiar_tipo_jaula(self, e):
        valor_seleccionado = e.control.value
        if self.jaula_seleccionada_id == 0:
           return
        sql = f"UPDATE jaulas SET jaula_tipo = %1 WHERE idsolicitud = {self.nIDSolicitud} and jaula = {self.jaula_seleccionada}"
        # Asignar el valor específico según la opción seleccionada
        if valor_seleccionado == "tapa":
            self.tipo_seleccionado = ""  # Primer elemento: Jaula con Tapa
            sql = sql.replace("%1", "1")
        elif valor_seleccionado == "separador":
            self.tipo_seleccionado = "con_separador"  # Segundo elemento: Jaula con Separador
            sql = sql.replace("%1", "2")
        elif valor_seleccionado == "sin_separador":
            self.tipo_seleccionado = "sin_separador"  # Tercer elemento: Jaula sin Separador
            sql = sql.replace("%1", "3")
        print("     xxxxxxxxxxxxxx  ", self.jaula_seleccionada_id)
        if self.jaula_seleccionada_id > 0:
            print(sql)
            ejecutar_sql(sql)
        self.mostrar_imagenes_jaula()

    def save_comment(self, e):
        comment = e.control.value
        nID = e.control.data
        # Guardamos el comentario en la base de datos
        sql = f"""UPDATE pasos 
                    SET descripcion = '{comment}' 
                    WHERE idsolicitud = {self.nIDSolicitud} 
                    AND id = {nID}"""
        ejecutar_sql(sql)

    def on_change_anomalia(self, e):
        self.anomalia_seleccionada = e.control.value

    def on_change_estado(self, e):
        self.estado_seleccionado = e.control.value  
    
    def on_change_sector(self, e):
        self.sector_seleccionado = e.control.value

    def agregar_marca(self, paso, jaula, markers_container, is_izq):
        # Dibujar el marcador en la imagen
        pintura_relleno = ft.Paint(style=ft.PaintingStyle.FILL, color=paso[5])
        circulo = cv.Circle(paso[1], paso[2], 10, paint=pintura_relleno)
        texto = cv.Text(x=paso[1], y=paso[2], text=str(paso[3]), style=ft.TextStyle(color="white", size=16, weight=ft.FontWeight.BOLD), alignment=ft.alignment.center)
        jaula.agregar_forma(circulo)
        jaula.agregar_forma(texto)

        # Crear el botón y controles del marcador
        btn_posicion = ft.ElevatedButton(text=str(paso[3]), bgcolor=paso[5], color=ft.Colors.WHITE, width=50, height=50, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)), data={'numero': paso[3], 'color': paso[5], 'x': paso[1], 'y': paso[2]}, disabled=True)
        anomalia_seleccionada = ft.Text(f"A: {paso[6]}", size=12, color=ft.Colors.BLACK)
        estado_seleccionado = ft.Text(f"E: {paso[7]}", size=12, color=ft.Colors.BLACK)
        sector_seleccionado = ft.Text(f"S: {paso[8]}", size=12, color=ft.Colors.BLACK)
        detalles_paso = ft.Column([anomalia_seleccionada, sector_seleccionado, estado_seleccionado], alignment=ft.MainAxisAlignment.START, spacing=2, width=150)
        comment_field = ft.TextField(value=paso[4], hint_text="Introduzca una observación", hint_style=ft.TextStyle(color=ft.Colors.GREY_400), width=200, border_color=ft.Colors.GREY_400, multiline=True, on_blur=self.save_comment, data=paso[0], focused_border_color=paso[5])
        btn_imagen_foto = crear_boton_moderno(
            texto=">", icono=ft.Icons.IMAGE, 
            on_click=self.crear_manejador_subir_imagen(paso[0]),
            tooltip="Subir imagen",
            color_fondo=COLORES_MODERNOS["verde_hover"],
        )
        #ft.ElevatedButton(">", on_click=self.crear_manejador_subir_imagen(paso[0]), icon=ft.Icons.IMAGE, icon_color=ft.Colors.GREEN, tooltip="Subir imagen")
        imagen_args = {"width": 50, "height": 50, "fit": ft.ImageFit.CONTAIN}
        if not paso[9]:
            imagen_args["src"] = "fondo_blanco.png"
        else:
            imagen_args["src_base64"] = paso[9]

        imagen_foto = ft.Image(**imagen_args)
        cnt_imagen_foto = ft.Container(content=imagen_foto, border=ft.border.all(2, paso[5]), border_radius=10)

        marker_container = ft.Row(controls=[btn_posicion, comment_field, ft.IconButton(icon=ft.Icons.DELETE, icon_color="white", bgcolor=ft.Colors.RED, on_click=lambda e, id=paso[0]: self.borrar_marca(id, is_izq), tooltip="Eliminar marca"), detalles_paso, btn_imagen_foto, cnt_imagen_foto], alignment=ft.MainAxisAlignment.START, spacing=10, width=900)
        markers_container.controls.append(marker_container)    
    
    def al_tocar_imagen_sync(self, e: ft.TapEvent, is_izq: bool):
        asyncio.run(self.al_tocar_imagen(e, is_izq))

    async def al_tocar_imagen(self, e: ft.TapEvent, is_izq: bool):
        if not self.color_seleccionado or not self.anomalia_seleccionada or not self.sector_seleccionado or not self.estado_seleccionado:
            if not self.color_seleccionado:
                print("color no seleccionado")
            if not self.anomalia_seleccionada:
                print("anomalía no seleccionado")
            self.show_message("Seleccione todos los campos requeridos")
            return

        x_rel, y_rel = e.local_x, e.local_y
        jaula = self.jaula_izq if is_izq else self.jaula_der
        markers_container = self.markers_container_izq if is_izq else self.markers_container_der

        sql = f"""INSERT INTO pasos 
                (idsolicitud, idjaula, jaula, idanomalia, idestado, idsector, color, pos_x, pos_y, numero, izq) 
                SELECT {self.nIDSolicitud}, {self.jaula_seleccionada_id}, {self.jaula_seleccionada}, {self.anomalia_seleccionada}, 
                        {self.estado_seleccionado}, {self.sector_seleccionado}, '{self.color_seleccionado}', 
                        {x_rel}, {y_rel}, COALESCE(MAX(numero), 0) + 1, {1 if is_izq else 0}
                FROM pasos 
                WHERE idsolicitud = {self.nIDSolicitud} 
                AND idjaula = {self.jaula_seleccionada_id} 
                AND izq = {1 if is_izq else 0}"""
        await asyncio.get_event_loop().run_in_executor(None, ejecutar_sql, sql)

        # Obtener el nuevo marcador insertado
        sql = f"""SELECT p.id, p.pos_x, p.pos_y, p.numero, p.descripcion, p.color, 
                a.nombre as anomalia, e.nombre as estado, s.nombre as sector, p.imagen 
                FROM pasos p
                LEFT JOIN anomalias a ON p.idanomalia = a.id 
                LEFT JOIN estado e ON p.idestado = e.id 
                LEFT JOIN sector s ON p.idsector = s.id 
                WHERE p.idsolicitud = {self.nIDSolicitud} 
                AND p.idjaula = {self.jaula_seleccionada_id} 
                AND p.izq = {1 if is_izq else 0}
                ORDER BY p.numero DESC LIMIT 1"""
        nuevo_paso = (await asyncio.get_event_loop().run_in_executor(None, ejecutar_sql, sql))[0]
        self.agregar_marca(nuevo_paso, jaula, markers_container, is_izq)

        if self.selected_button:
            self.selected_button.color = ft.Colors.YELLOW_ACCENT_700
            self.selected_button.data['color_texto'] = ft.Colors.YELLOW_ACCENT_700
            self.selected_button.update()
        
        jaula.update()
        markers_container.update()
        await asyncio.get_event_loop().run_in_executor(None, self.guardar_imagen, is_izq)
        self.page.update()

    def mostrar_marcas(self, is_izq: bool):
        jaula = self.jaula_izq if is_izq else self.jaula_der
        markers_container = self.markers_container_izq if is_izq else self.markers_container_der

        sql = f"""SELECT p.id, p.pos_x, p.pos_y, p.numero, p.descripcion, p.color, 
                a.nombre as anomalia, e.nombre as estado, s.nombre as sector, p.imagen 
                FROM pasos p
                LEFT JOIN anomalias a ON p.idanomalia = a.id 
                LEFT JOIN estado e ON p.idestado = e.id 
                LEFT JOIN sector s ON p.idsector = s.id 
                WHERE p.idsolicitud = {self.nIDSolicitud} 
                AND p.idjaula = {self.jaula_seleccionada_id} 
                AND p.izq = {1 if is_izq else 0}"""
        pasos = ejecutar_sql(sql)

        markers_container.controls.clear()
        jaula.formas.clear()

        for paso in pasos:
            # Dibujar el marcador en la imagen
            pintura_relleno = ft.Paint(
                style=ft.PaintingStyle.FILL, 
                color=paso[5]
            )
            circulo = cv.Circle(paso[1], paso[2], 10, paint=pintura_relleno)
            jaula.agregar_forma(circulo)
            
            # Agregar el número como texto
            texto = cv.Text(
                x=paso[1],
                y=paso[2],
                text=str(paso[3]),
                style=ft.TextStyle(
                    color="white",
                    size=16,
                    weight=ft.FontWeight.BOLD
                ),
                alignment=ft.alignment.center
            )
            jaula.agregar_forma(texto)

            # Crear el botón del marcador
            btn_posicion = ft.ElevatedButton(
                text=str(paso[3]),
                bgcolor=paso[5],
                color=ft.Colors.WHITE,
                width=50,
                height=50,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                ),
                data={
                    'numero': paso[3],
                    'color': paso[5],
                    'x': paso[1],
                    'y': paso[2]
                },
                disabled=True
            )

            tamano_letras = 12
            color_letras = ft.Colors.BLACK
            anomalia_seleccionada = ft.Text(f"A: {paso[6]}", size=tamano_letras, color=color_letras)
            estado_seleccionado = ft.Text(f"E: {paso[7]}", size=tamano_letras, color=color_letras)
            sector_seleccionado = ft.Text(f"S: {paso[8]}", size=tamano_letras, color=color_letras)
            detalles_paso = ft.Column(
                [anomalia_seleccionada, sector_seleccionado, estado_seleccionado], 
                alignment=ft.MainAxisAlignment.START, 
                spacing=2,
                width=150
            )

            # Crear el campo de comentario
            comment_field = ft.TextField(
                value=paso[4],
                hint_text="Introduzca una observación",
                hint_style=ft.TextStyle(color=ft.Colors.GREY_400),
                width=200,
                border_color=ft.Colors.GREY_400,
                multiline=True,
                on_blur=self.save_comment,
                data=paso[0],
                focused_border_color=paso[5]
            )

            btn_imagen_foto = crear_boton_moderno(
                texto=">", icono=ft.Icons.IMAGE, 
                on_click=self.crear_manejador_subir_imagen(paso[0]),
                tooltip="Subir imagen",
                color_fondo=COLORES_MODERNOS["verde_hover"],
            )
            #ft.ElevatedButton(">", on_click=self.crear_manejador_subir_imagen(paso[0]), icon=ft.Icons.IMAGE, icon_color=ft.Colors.GREEN, tooltip="Subir imagen")
            if not paso[9]:
                imagen_foto = ft.Image(src = "fondo_blanco.png", width = 50, height = 50, fit=ft.ImageFit.CONTAIN)
                imagen_mostrar = None
            else:
                imagen_foto = ft.Image(src_base64 = paso[9], width = 50, height = 50, fit=ft.ImageFit.CONTAIN)
                imagen_mostrar = paso[9]
            cnt_imagen_foto = ft.Container(
                content=imagen_foto,
                border=ft.border.all(2, paso[5]),
                border_radius=10,
                on_click=lambda e, img=imagen_mostrar: self.show_image_zoom(img) if img else None
            )

            # Crear el contenedor para el botón y el campo de comentario
            marker_container = ft.Row(
                controls=[
                    btn_posicion,
                    comment_field, 
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color="white",
                        bgcolor=ft.Colors.RED,
                        on_click=lambda e, id=paso[0]: self.borrar_marca(id, is_izq),
                        tooltip="Eliminar marca"
                    ),
                    detalles_paso, 
                    btn_imagen_foto, 
                    cnt_imagen_foto
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=10, 
                width=900, 
            )
            markers_container.controls.append(marker_container)

        markers_container.update()
        jaula.update()
        self.page.update()

    async def subir_imagen(self, nID):
        print(f"ID es {nID}")
        if self.jaula_seleccionada:
            # El contenedor se mostrará automáticamente durante la carga
            await self.imagen_subir.seleccionar_archivo()
            
            if hasattr(self.imagen_subir, 'hide_container_after_complete') and self.imagen_subir.hide_container_after_complete:
                self.imagen_subir.container.visible = False
                self.imagen_subir.hide_container_after_complete = False
                self.page.update()

            archivo_subido_jaula = await self.imagen_subir.get_archivo_subido()
            if archivo_subido_jaula and archivo_subido_jaula != ["", None]:
                # Extraer solo el nombre base del archivo (sin ruta)
                nombre_archivo = os.path.basename(archivo_subido_jaula)
                archivo_subido_jaula_contenido = self.imagen_subir.get_archivo_contenido()
                sql = f"UPDATE pasos SET imagen = '{archivo_subido_jaula_contenido}' WHERE id = {nID}"
                ejecutar_sql(sql)
                self.mostrar_marcas(True) 
                self.mostrar_marcas(False)

                # Asegurarse de que el contenedor esté oculto después de procesar
                if hasattr(self.imagen_subir, 'container'):
                    self.imagen_subir.container.visible = False
                    self.page.update()
            else:
                print("No se seleccionó ningún archivo.")

                if hasattr(self.imagen_subir, 'container'):
                    self.imagen_subir.container.visible = False
                    self.page.update()

    def crear_manejador_subir_imagen(self, nID):
        async def manejador(_):
            await self.subir_imagen(nID)
        return manejador

    def borrar_marca(self, id_paso: int, is_izq: bool):
        sql = f"DELETE FROM pasos WHERE id = {id_paso}"
        ejecutar_sql(sql)
        self.renumerar_marcas(is_izq)
        self.page.update()

    def renumerar_marcas(self, is_izq: bool):
        sql = f"""SELECT numero 
                    FROM pasos 
                    WHERE idsolicitud = {self.nIDSolicitud} 
                    AND idjaula = {self.jaula_seleccionada_id} 
                    AND izq = {1 if is_izq else 0}"""
        pasos = ejecutar_sql(sql)
        sql = ""
        for i, paso in enumerate(pasos):
            sql = f"""UPDATE pasos 
                        SET numero = {i + 1} 
                        WHERE idsolicitud = {self.nIDSolicitud} 
                        AND idjaula = {self.jaula_seleccionada_id} 
                        AND izq = {1 if is_izq else 0} 
                        AND numero = {paso[0]}"""
            ejecutar_sql(sql)
        self.inicializar_imagen(is_izq)
        self.guardar_imagen(is_izq)
    
    def enviar_correo_informe(self):
        sql = f"SELECT asunto, emails, cuerpo, realizo_trabajos, archivo1, archivo_nombre1, archivo2, archivo_nombre2, archivo3, archivo_nombre3, archivo4, archivo_nombre4, idtipo_informe FROM solicitudes WHERE id = {self.nIDSolicitud}"    
        datos_correo = ejecutar_sql(sql)
        adjuntos = []
        if datos_correo[0][4]:
            grabar_en_disco(datos_correo[0][5], datos_correo[0][4])
            archivo = os.path.join(upload_dir, datos_correo[0][5])
            adjuntos.append(archivo)
        if datos_correo[0][6]:
            grabar_en_disco(datos_correo[0][7], datos_correo[0][6])
            archivo = os.path.join(upload_dir, datos_correo[0][7])
            adjuntos.append(archivo)
        if datos_correo[0][8]:
            grabar_en_disco(datos_correo[0][9], datos_correo[0][8])
            archivo = os.path.join(upload_dir, datos_correo[0][9])
            adjuntos.append(archivo)
        if datos_correo[0][10]:
            grabar_en_disco(datos_correo[0][11], datos_correo[0][10])
            archivo = os.path.join(upload_dir, datos_correo[0][11])
            adjuntos.append(archivo)
        if datos_correo[0][12] == 3:
            reporte = self.imprimir_informe(abrir_url=False)
            adjuntos.append(reporte)

        enviar_correo(destinatarios=datos_correo[0][1], asunto=datos_correo[0][0], cuerpo=datos_correo[0][2], archivos_adjuntos=adjuntos, borrar_temporales=False)
        self.show_message("Correo enviado con éxito")

    def imprimir_informe(self, abrir_url=True):
        sql = f"SELECT centros.centro, idtipo_informe, fecha FROM solicitudes LEFT JOIN centros on solicitudes.idcentro = centros.id WHERE solicitudes.id = {self.nIDSolicitud}"
        tipo_informe = ejecutar_sql(sql)
        centro, ti, fecha = tipo_informe[0]
        fecha_formateada = fecha.strftime("%d-%m-%Y") if fecha is not None else "Sin fecha"
        titulo = f"{centro} {fecha_formateada}"
        titulo = f"Informe Redes {titulo} {self.nIDSolicitud}.pdf"
        archivo = os.path.join(upload_dir, titulo)
        alf = archivo
        if not os.path.isabs(alf):
            original_file_path = archivo
            original_file_path = os.path.abspath(original_file_path)
            print("Entro aqui,   ", original_file_path)
        else:
            archivo = alf
        os.makedirs(os.path.dirname(archivo), exist_ok=True)
        Reporte = Imprimir_Informe_Redes(
            archivo, 
            id = self.nIDSolicitud,
            pagesize=letter,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )
        Reporte.generar_reporte()

        if abrir_url:
            pass
            #await self.page.download_async(archivo)
            #await self.show_message("Descarga del informe iniciada")
        return archivo

    def guardar_imagen(self, is_izq):
        jaula = self.jaula_izq if is_izq else self.jaula_der
        lado = "izq" if is_izq else "der"
        
        imagen_base64 = jaula.guardar_imagen()
        solo_imagen_64 = imagen_base64.split(',')[1]
        imagen_bytes = base64.b64decode(solo_imagen_64)
        nombre_archivo = f"jaula_{lado}_{self.jaula_seleccionada_id}.png"
        ruta_archivo = os.path.join(assets_dir, nombre_archivo)
        
        with open(ruta_archivo, 'wb') as f:
            f.write(imagen_bytes)
        
        # Actualizar la base de datos con la nueva ruta de la imagen
        sql = f"UPDATE jaulas SET jaula_imagen_{lado} = '{solo_imagen_64}' WHERE idsolicitud = {self.nIDSolicitud} AND id = {self.jaula_seleccionada_id}"
        ejecutar_sql(sql)
      
        print(f"Imagen guardada en: {ruta_archivo}")
        self.page.update()

    def select_color(self, e, color_hex):
        if self.selected_color:
            self.selected_color.style.side = None
            self.selected_color.update()

        print(f"anomalia id: {e.control.data}")
        self.anomalia_seleccionada = e.control.data
        e.control.style.side = ft.BorderSide(width=3, color=ft.Colors.YELLOW)
        self.selected_color = e.control
        self.color_seleccionado = color_hex
        #sql = f"SELECT id, nombre FROM anomalias WHERE color = '{color_hex}'"
        #self.cbo_anomalias.options = [
        #    ft.dropdown.Option(
        #            key=str(id),
        #            text=nombre,
        #        ) for id, nombre in ejecutar_sql(sql)
        #    ]
        #self.cbo_anomalias.update()
        self.cbo_sector.value = ""
        self.cbo_estado.value = ""

        #self.anomalia_seleccionada = 0
        self.sector_seleccionado = 0
        self.estado_seleccionado = 0
        self.page.update()

    def actualizar_registro_jaulas(self):
        sql = f"SELECT jaulas.id, jaulas.jaula, jaulas.jaula_imagen_izq, jaulas.jaula_imagen_der, jaulas.jaula_tipo FROM jaulas WHERE idsolicitud = {self.nIDSolicitud}"
        self.jaulas_rows = ejecutar_sql(sql)
        return self.jaulas_rows

    def crear_jaulas(self):
        self.jaula_buttons = []
        self.jaulas.controls.clear() 

        jaulas = self.actualizar_registro_jaulas()
        if not jaulas:
            return

        for jaula in jaulas:
            sql = f"SELECT id FROM pasos WHERE idsolicitud = {self.nIDSolicitud} and idjaula = {jaula[0]}"
            filas = ejecutar_sql(sql)
            color_texto = ft.Colors.WHITE
            if filas:
                color_texto = ft.Colors.YELLOW_ACCENT_700

            button = ft.ElevatedButton(
                text=jaula[1],
                color=color_texto,
                bgcolor=ft.Colors.GREEN_700,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    side=ft.BorderSide(width=2, color=ft.Colors.TRANSPARENT),
                ),
                scale=1.0,
                on_click=lambda e: self.manejar_click(e),
                data={
                    'id': jaula[0],
                    'numero': jaula[1],
                    'color_texto': color_texto
                }
            )
            self.jaulas.controls.append(button)
            self.jaula_buttons.append(button)  # Asegurarse de agregar el botón a la lista

        if self.page:
            self.jaula_container.visible = True
            self.page.update()

    def manejar_click(self, e):
        if hasattr(self, 'selected_button'):
            if self.selected_button in self.jaula_buttons:
                self.selected_button.bgcolor = ft.Colors.GREEN_700
                #self.selected_button.color = ft.Colors.WHITE
                self.selected_button.color = self.selected_button.data['color_texto']
                self.selected_button.style.side = ft.BorderSide(width=2, color=ft.Colors.TRANSPARENT)
                self.selected_button.scale = 1.0
                self.selected_button.update()

        # Update newly selected button
        self.selected_button = e.control
        self.selected_button.bgcolor = ft.Colors.BLUE_700
        #self.selected_button.color = ft.Colors.WHITE
        self.selected_button.color = e.control.data['color_texto']
        self.selected_button.style.side = ft.BorderSide(width=2, color=ft.Colors.YELLOW)
        self.selected_button.scale = 1.1
        self.selected_button.update()

        self.jaula_seleccionada = e.control.data['numero']
        self.jaula_seleccionada_id = e.control.data['id']

        self.selected_button_text = self.jaula_seleccionada
        self.selected_jaula.value = f"Jaula: {self.selected_button_text}" if hasattr(self, 'selected_button_text') else "Jaula: "
        self.mostrar_imagenes_jaula()
        self.tab_jaula_izq.visible = True
        self.tab_jaula_der.visible = True
        self.page.update()

    def grabar_descripcion(self, e):
        id_jaula = e.control.data
        descripcion = e.control.value
        print(f"id_jaula: {id_jaula}, descripcion: {descripcion}")
        if e.control.label != descripcion:
            sql = f"UPDATE jaulas_detalle SET descripcion = '{descripcion}' WHERE id = {id_jaula}"
            e.control.label = descripcion
            e.control.update()
            ejecutar_sql(sql)

    def inicializar_imagen(self, is_izq: bool):
        jaula = self.jaula_izq if is_izq else self.jaula_der
        imagen_original = self.imagen_original_izq if is_izq else self.imagen_original_der
        image_container = self.image_container_izq if is_izq else self.image_container_der

        jaula.formas.clear()
        jaula.src_64 = imagen_original
        jaula._inicializar_imagen()
        jaula.content = jaula._crear_contenido()
        image_container.content = jaula
        image_container.visible = True
        image_container.update()
        self.mostrar_marcas(is_izq)

    def mostrar_imagenes_jaula(self):
        sql = f"SELECT jaula_izq, jaula_der, jaula_izq_con_separador, jaula_der_con_separador, jaula_izq_sin_separador, jaula_der_sin_separador FROM centros WHERE id = {self.cbo_centros.value}"
        jaula_imagenes = ejecutar_sql(sql)
        
        if not jaula_imagenes:
            self.selected_jaula.update()
            self.image_container_izq.visible = False
            self.image_container_der.visible = False
            self.page.update()
            return
        
        self.color_seleccionado = ""
        self.anomalia_seleccionada = 0
        self.sector_seleccionado = 0
        self.estado_seleccionado = 0

        if jaula_imagenes:
            self.jaulas_rows = self.actualizar_registro_jaulas()
            jaulas_filtradas = [jaula for jaula in self.jaulas_rows if jaula[1] == self.jaula_seleccionada]  # jaula[1] es el segundo elemento (jaula)
            jaula_tipos = [jaula[4] for jaula in jaulas_filtradas]  # jaula[3] es el cuarto elemento (jaula_tipo)
            jaula_tipos = jaula_tipos[0]
            if jaula_tipos == 1:
                izq_index = 0
                der_index = 1
                self.opciones_jaula.value = "tapa"
            elif jaula_tipos == 2:
                izq_index = 2
                der_index = 3
                self.opciones_jaula.value = "separador"
            elif jaula_tipos == 3:
                izq_index = 4
                der_index = 5
                self.opciones_jaula.value = "sin_separador"
            else:
                izq_index = 0
                der_index = 1            
                self.opciones_jaula.value = "tapa"

            self.opciones_jaula.update()
            #if self.tipo_seleccionado == "":
                # Jaula con Tapa (índices 0 y 1)
            #elif self.tipo_seleccionado == "con_separador":
                # Jaula con Separador (índices 2 y 3)
            #elif self.tipo_seleccionado == "sin_separador":
                # Jaula sin Separador (índices 4 y 5)
            #else:
                # Valor por defecto si tipo_seleccionado no coincide con ninguno
            
            if jaula_imagenes[0][izq_index] and jaula_imagenes[0][der_index]:
                print(f" columnas jaula {izq_index}, {der_index}")
                self.imagen_original_izq = jaula_imagenes[0][izq_index]
                self.imagen_original_der = jaula_imagenes[0][der_index]

            self.inicializar_imagen(True)
            self.inicializar_imagen(False)

            # Guardar las imágenes inmediatamente, incluso sin marcas
            self.guardar_imagen(True)  # Guardar imagen izquierda
            self.guardar_imagen(False)  # Guardar imagen derecha

        self.selected_jaula.update()
        self.page.update()

    def crear_interfaz(self):
        async def adjuntar(e):
            if len(self.archivos) < 4:
                # Usar el nuevo SubirArchivoManager - el contenedor se mostrará automáticamente durante la carga
                await self.subir_adjunto.seleccionar_archivo()
                archivo_subido = await self.subir_adjunto.get_archivo_subido()
                if archivo_subido and archivo_subido != ["", None]:
                    # Extraer solo el nombre base del archivo (sin ruta)
                    nombre_archivo = os.path.basename(archivo_subido)
                    archivo_subido_contenido = self.subir_adjunto.get_archivo_contenido()
                    self.archivos.append({
                        "nombre": nombre_archivo,
                        "contenido": archivo_subido_contenido
                    })
                    self.actualizar_lista_adjuntos()
                else:
                    print("No se seleccionó ningún archivo.")

            if len(self.archivos) > 0:
                nArchivo = 1
                for archivo in self.archivos:
                    # Asegurarse de que solo se use el nombre base del archivo
                    sNombre = os.path.basename(archivo['nombre'])
                    sContenido = archivo['contenido']
                    sql = f"UPDATE solicitudes SET archivo_nombre{str(nArchivo)} = '{sNombre}', archivo{str(nArchivo)} = '{sContenido}' WHERE id = {self.nIDSolicitud}"
                    ejecutar_sql(sql)
                    nArchivo += 1

        # Inicializar componentes
        self.date_picker = ft.DatePicker(
            on_change=self.actualizar_fecha,
            first_date=datetime(datetime.now().year - 5, datetime.now().month, 1),
            last_date=datetime.now()
        )

        #self.fecha_button = ft.ElevatedButton(
        #    text="Seleccionar fecha",
        #    icon=ft.Icons.DATE_RANGE,
        #    on_click=lambda _: self.date_picker.pick_date()
        #)
        self.fecha_button = crear_boton_moderno(
            texto="Fecha",
            icono=ft.Icons.DATE_RANGE,
            #on_click=lambda e: self.date_picker.pick_date(),
            on_click=lambda e: self.pedir_fecha(),
            color_fondo=COLORES_MODERNOS["azul_primario"],
            ancho=120,
            alto=40
        )
        self.fecha_caption_input = ft.Text("Fecha:")
        self.fecha_input = ft.Row([
            self.fecha_caption_input,
            self.fecha_button,
        ])

        # TAB 1
        self.Realizo_trabajos.on_change = lambda e: self.on_change_realizo_trabajo()
        self.cbo_empresa.on_change = lambda e: self.grabar_datos_tab1()
        self.cbo_centros.on_change = lambda e: self.on_change_centros(e)

        self.num_jaulas.keyboard_type = ft.KeyboardType.NUMBER, 
        self.num_jaulas.hint_text ="Solo enteros", 
        self.num_jaulas.on_blur = lambda e: self.cambios_jaulas(e)

        #self.desde.on_change = lambda e: self.grabar_datos_tab1()
        self.desde.keyboard_type = ft.KeyboardType.NUMBER, 
        self.num_jaulas.hint_text ="Solo enteros", 
        self.desde.on_blur =lambda e: self.cambios_jaulas(e)

        self.tab1 = ft.Tab(text="Datos Básicos", content=ft.Column([
            ft.Container(expand=1),
            ft.Row([self.fecha_input, self.btn_hora_desde, self.btn_hora_hasta, self.hora_diferencia]),
            self.Urgente,
            self.cbo_empresa,
            self.cbo_centros,
            ft.Row([self.num_jaulas, self.desde])
        ]))

        # TAB 2
        self.para.on_focus = lambda e: self.on_focus_para(e)
        self.para.on_blur = lambda e: self.on_blur_validar_correos(e)
        self.Urgente.on_change = lambda e: self.on_change_urgente()
        self.asunto.on_change = lambda e: self.grabar_datos_tab2()
        self.para.on_change = lambda e: self.grabar_datos_tab2()
        self.cuerpo.on_change = lambda e: self.grabar_datos_tab2()
        self.btn_Subir_Adjunto = crear_boton_moderno(
            texto="Adjuntar archivo", 
            icono=ft.Icons.ATTACH_EMAIL, 
            on_click=adjuntar,
            color_fondo=COLORES_MODERNOS["azul_primario"],
            ancho=160,
            alto=40
        )
        #ft.ElevatedButton("Adjuntar archivo", on_click=adjuntar, icon=ft.Icons.ATTACH_EMAIL, icon_color=ft.Colors.GREEN)

        self.tab2 = ft.Tab(
            text="Enviar correo electrónico",
            content=ft.Column(
                [
                    ft.Container(expand=1),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=self.para,
                                    expand=7
                                ),
                                ft.Container(
                                    content=self.Realizo_trabajos,
                                    expand=3
                                )
                            ],
                            spacing=10
                        ),
                        expand=True
                    ),
                    self.asunto,
                    self.cuerpo,
                    ft.Row([self.btn_Subir_Adjunto, self.lista_archivos]),
                    self.subir_adjunto.get_container()
                ],
                spacing=10,  # Controla el espacio entre elementos
                expand=False
            )
        )

        # TAB 3 - Jaulas
        self.jaula_izq = ImagenDibujable(src_64="", ancho=500, alto=500)
        self.jaula_der = ImagenDibujable(src_64="", ancho=500, alto=500)
        self.faena_realizada.on_change = lambda e: self.grabar_datos_tab3()
        self.selected_jaula = ft.Text("", size=20)

        self.edt_posicion_izq = ft.TextField("", hint_text="Comentario", max_length=10, min_lines=6, multiline=True)
        self.image_container_izq.on_tap_down = lambda e: self.al_tocar_imagen_sync(e, True)
        self.markers_container_izq = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            height=400  # Altura fija para el contenedor de marcadores
        )
        self.marcadores_izq = ft.Text("Marcadores:", size=16, weight=ft.FontWeight.BOLD, visible=False)
        self.markers_section_izq = ft.Column([
            self.marcadores_izq,
            self.markers_container_izq,
        ], 
        width=900, 
        )

        self.edt_posicion_der = ft.TextField("", hint_text="Comentario", max_length=10, min_lines=6, multiline=True)
        self.image_container_der.on_tap_down = lambda e: self.al_tocar_imagen_sync(e, False)
        self.markers_container_der = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            height=400  # Altura fija para el contenedor de marcadores
        )
        self.marcadores_der = ft.Text("Marcadores:", size=16, weight=ft.FontWeight.BOLD, visible=False)
        self.markers_section_der = ft.Column([
            self.marcadores_der,
            self.markers_container_der,
        ], 
        width=900, 
        )

        self.tab_jaula_izq = ft.Tab(
            text="Jaula Izquierda",
            content=ft.Column(
                [
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),  # Corrige aquí
                    ft.Row(
                        [
                            ft.Container(
                                content=self.image_container_izq,
                                width=500,
                                height=500,
                                alignment=ft.alignment.center
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("Marcadores:", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Container(
                                            content=self.markers_container_izq,
                                            expand=True,
                                            # scroll=ft.ScrollMode.AUTO
                                        )
                                    ],
                                    expand=True
                                ),
                                width=900,
                                expand=True
                            ),
                        ],
                        expand=True,
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.START
                    )
                ]
            )
        )

        self.tab_jaula_der = ft.Tab(
            text="Jaula Derecha",
            content=ft.Column(
                [
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),  # Corrige aquí
                    ft.Row(
                        [
                            ft.Container(
                                content=self.image_container_der,
                                width=500,
                                height=500,
                                alignment=ft.alignment.center
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("Marcadores:", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Container(
                                            content=self.markers_container_der,
                                            expand=True,
                                            # scroll=ft.ScrollMode.AUTO
                                        )
                                    ],
                                    expand=True
                                ),
                                width=900,
                                expand=True
                            ),
                        ],
                        expand=True,
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.START
                    )
                ]
            )
        )

        self.tab3_container = ft.Container(
            content=ft.Column([
                ft.Row([self.selected_jaula, ft.Divider(), self.opciones_jaula_container]),
                self.jaula_container,
                ft.Divider(height=10),
                self.faena_realizada,
                ft.Divider(height=10),
                #ft.Row([self.btn_colores, self.cbo_anomalias, self.cbo_sector, self.cbo_estado]),
                ft.ResponsiveRow([
                    ft.Column([
                        self.seleccione_un_color,
                        self.color_buttons_grid,  # Contenedor de colores con scroll
                    ], col={"xs": 12, "sm": 8, "md": 7, "lg": 10}),  # Ancho responsivo
                    
                    ft.Column([  # Controles agrupados
                        #self.cbo_anomalias,
                        self.cbo_sector,
                        self.cbo_estado,
                    ], col={"xs": 12, "sm": 4, "md": 5, "lg": 2}),  # Ancho responsivo
                ]),
                self.imagen_subir.get_container(),
                ft.Divider(height=10),
                ft.Tabs(tabs=[self.tab_jaula_izq, self.tab_jaula_der], animation_duration=300)
            ]),
            expand=True
        )
        self.tab_jaula_izq.visible = True
        self.tab_jaula_izq.visible = True

        self.tab3 = ft.Tab(text="Jaulas", content=ft.Column(
            [self.tab3_container]
        ))

        # Crear el objeto Tabs con las pestañas
        self.tabs = ft.Tabs(tabs=[self.tab1, self.tab2, self.tab3], animation_duration=300)

        if self.page:
            self.page.overlay.append(self.date_picker)

        sql = f"SELECT id FROM solicitudes WHERE id = {self.nIDSolicitud}"
        haydatos = ejecutar_sql(sql)
        if haydatos:
            self.mostrar_datos_tab1()
            self.mostrar_datos_tab2()
            self.crear_jaulas()
        else:
            self.titulo.value = self.caption + ". Nuevo"
        #self.tabs.selected_index = 3
        #self.page.add(self.titulo, self.tabs)

    def build(self):
        btn_enviar_email = ft.ElevatedButton(
            "Enviar Email",
            icon=ft.Icons.EMAIL,
            on_click=lambda _: self.enviar_correo_informe(),
            icon_color="yellow",
            tooltip="Enviar por email el informe",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                elevation=0,
                overlay_color=ft.Colors.with_opacity(0.1, COLORES_MODERNOS["texto_principal"]),
            ),
            bgcolor=COLORES_MODERNOS["azul_primario"],
            color=COLORES_MODERNOS["texto_principal"],
        )
        """Devuelve los controles que se deben agregar a la página."""
        return ft.Column([ft.Row([self.titulo, btn_enviar_email]), self.tabs])

    def limpiar_controles(self):
        #TAB 1
        self.fecha_button.text = "Seleccionar fecha"
        self.hora_diferencia_elegido = ""
        self.hora_desde_elegida = ""
        self.hora_hasta_elegida = ""
        self.fecha_input = "Seleccione Fecha"
        self.btn_hora_desde.text = "Hora desde"
        self.btn_hora_hasta.text = "Hora hasta"
        self.hora_diferencia.value = ""
        self.Urgente.value = False
        self.cbo_empresa.value = ""
        self.cbo_centros.value = ""
        self.num_jaulas.value = ""
        self.desde.value = ""

        #TAB 2
        self.Realizo_trabajos.value = False
        self.para.value = ""
        self.asunto.value = ""
        self.cuerpo.value = ""
        self.archivos = []
        self.archivo1 = ""
        self.archivo2 = ""
        self.archivo3 = ""
        self.archivo4 = ""
        self.archivo_nombre1 = ""
        self.archivo_nombre2 = ""
        self.archivo_nombre3 = ""
        self.archivo_nombre4 = ""

        #TAB 3
        self.selected_jaula.value = ""
        self.jaula_seleccionada = ""
        self.jaula_seleccionada_id = 0
        #self.jaula_izq.actualizar_imagen("")
        #self.jaula_der.actualizar_imagen("")
        self.markers_container_izq.controls.clear()
        self.markers_container_der.controls.clear()
        self.color_seleccionado = ""
        self.anomalia_seleccionada = ""
        self.estado_seleccionado = ""
        self.sector_seleccionado = ""
        self.page.update()

    def actualizar(self, id: int):
        """Actualiza los datos de la interfaz con el nuevo ID."""
        self.nIDSolicitud = id
        
        self.is_edit = self.nIDSolicitud > 0
        self.cbo_empresa.disabled = self.is_edit
        self.cbo_centros.disabled = self.is_edit
        self.num_jaulas.disabled = self.is_edit
        self.desde.disabled = self.is_edit

        sql = f"SELECT id FROM solicitudes WHERE id = {self.nIDSolicitud}"
        haydatos = ejecutar_sql(sql)
        if haydatos:
            self.limpiar_controles()
            self.mostrar_datos_tab1()
            self.mostrar_datos_tab2()
            self.crear_jaulas()
            self.tab_jaula_izq.visible = False
            self.tab_jaula_der.visible = False
            self.titulo.value = f"{self.caption} N° {self.nIDSolicitud}"
            self.tabs.selected_index = 2
        else:
            fecha = datetime.now()
            idusuario = self.page.session.get("idusuario")
            sql = f"INSERT INTO solicitudes (fecha, idcentro, idempresa, idtipo_informe, idoperador) VALUES ('{self.fecha_indicada}', 0, 0, 3, {idusuario})"
            self.nIDSolicitud = ejecutar_sql(sql)
            self.limpiar_controles()
            self.fecha_button.text = datetime.strftime(fecha, "%d/%m/%Y") if fecha != None else ""
            self.fecha_indicada = fecha
            self.titulo.value = self.caption + ". Nuevo"

        self.page.update()  # Update the entire page

def main(page: ft.Page):
    nID = 129
    def Mostrar(e):
        informe_ui.actualizar(nID)
        page.update()

    def Mostrar2(e):
        informe_ui.actualizar(0)
        page.update()
    informe_ui = InformeRedesUI(page, nID)
    informe_controls = informe_ui.build()
    page.scroll = True

    page.add(
        ft.Row([
            ft.ElevatedButton(nID, on_click=lambda e:Mostrar(e)),
            ft.ElevatedButton("0", on_click=lambda e:Mostrar2(e)),
        ]),
        informe_controls)
    page.update()


if __name__ == "__main__":
    ft.app(target=main, assets_dir=assets_dir, upload_dir=upload_dir, view=ft.WEB_BROWSER)

