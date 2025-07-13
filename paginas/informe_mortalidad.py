import flet as ft
from conectarbd import ejecutar_sql, delete_record, nuevo_registro, editar_registro, validar_registros_tabla
# Cambiar la importación de SubirArchivo a SubirArchivoManager
from subir_archivo import SubirArchivoManager
from datetime import datetime, time, timedelta
from funciones import calcular_horas_diferencia, validar_enteros, format_timedelta, format_time, parse_time_string, validar_correos, grabar_en_disco, enviar_correo
from variables_globales import assets_dir, upload_dir
import warnings
import os
import pyperclip
import asyncio
from imprimir.reporte_mortalidad import Imprimir_Informe_Mortalidad
from reportlab.lib.pagesizes import letter
from estilos_modernos import (
    COLORES_MODERNOS,
    crear_dropdown_moderno,
    crear_boton_moderno,
    crear_contenedor_moderno,
    crear_texto_moderno,
    crear_tabla_moderna,
    crear_campo_moderno
)

warnings.filterwarnings("ignore", message="remove second argument of ws_handler")


class InformeMortalidadUI(ft.Control):
    def __init__(self, page: ft.Page, nIDSolicitud: int):
        super().__init__()
        self.page = page
        self.nIDSolicitud = nIDSolicitud
        self.initialize_ui()

    #def _get_control_name(self):
    #    return "informe_mortalidad_ui"

    #def build(self):
    #    pass

    def initialize_ui(self):
        #self.page.clean()
        self.selected_files = ft.Text("")
        self.entidad = "solicitudes"
        self.caption = "Informe Mortalidad"
        self.snackBar = ft.SnackBar(
            content=ft.Text("", color=ft.Colors.YELLOW),
            duration=5000,
            show_close_icon=True,
            close_icon_color=ft.Colors.RED
        )
        self.page.overlay.append(self.snackBar)
        self.titulo = ft.Text(f"{self.caption} N° {self.nIDSolicitud}", size=20)
        self.jaula_seleccionada = ""
        self.nRegistros = 0
        self.registros = ft.Text("")
        self.altura_combos = 40
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
        #self.cbo_empresa = ft.Dropdown(label="Empresa", options=[ft.dropdown.Option(str(id), nombre) for id, nombre in ejecutar_sql("SELECT id, nombre FROM empresas")])
        #self.cbo_centros = ft.Dropdown(label="Centro", options=[ft.dropdown.Option(str(id), centro) for id, centro in ejecutar_sql("SELECT id, centro FROM centros")])
        self.num_jaulas = crear_campo_moderno(label = "# Jaulas", prefix_icon = ft.Icons.SQUARE_OUTLINED, width=120 )
        self.desde = crear_campo_moderno(label = "Desde", prefix_icon = ft.Icons.NUMBERS, width=120 )
        #self.num_jaulas = ft.TextField(label="# Jaulas")
        #self.desde = ft.TextField(label="Desde")

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
        self.jaulas = ft.Row(
            scroll=ft.ScrollMode.AUTO,
            expand=1,
            alignment=ft.MainAxisAlignment.START
        )  # Lista para almacenar las jaulas (botones)
        self.jaula_container = ft.Container(
            content=self.jaulas
        )
        # Reemplazar SubirArchivo con SubirArchivoManager
        self.subir_archivo = SubirArchivoManager(self.page, allowed_extensions=["png", "jpg", "jpeg", "gif"])

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
            self.grabar_datos_tab1()
            self.registrar_jaulas_en_tabla_jaulas()
            self.crear_jaulas()
            self.page.update()

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
        if datos_correo[0][12] == 1:
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
        titulo = f"Informe Mortalidad {titulo} {self.nIDSolicitud}.pdf"
        archivo = os.path.join(upload_dir, titulo)
        Reporte = Imprimir_Informe_Mortalidad(
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
            sql = f"UPDATE solicitudes SET archivo1 = '{self.archivo1}', archivo_nombre1 = '{self.archivo_nombre1}', archivo2 = '{self.archivo_nombre2}', archivo3 = '{self.archivo_nombre3}', archivo3 = '{self.archivo3}', archivo_nombre4 = '{self.archivo_nombre4}' where id = {self.nIDSolicitud}"
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

    def registrar_jaulas_en_tabla_jaulas(self):
        solicitud = ejecutar_sql(f"SELECT solicitudes.jaulas, solicitudes.jaula_desde, centros.jaula_izq, centros.jaula_der FROM solicitudes LEFT JOIN centros ON solicitudes.idcentro = centros.id WHERE solicitudes.id = {self.nIDSolicitud}")

        ejecutar_sql(f"DELETE FROM jaulas WHERE idsolicitud = {self.nIDSolicitud}")
        ejecutar_sql(f"DELETE FROM jaulas_detalle WHERE idsolicitud = {self.nIDSolicitud}")
        desde = solicitud[0][1]
        jaulas = solicitud[0][0]
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
            self.num_jaulas.value = centros[0][0]
            self.desde.value = centros[0][1]
            self.grabar_datos_tab1()
            self.registrar_jaulas_en_tabla_jaulas()
            self.crear_jaulas()
            self.page.update()

    def actualizar_fecha(self, e):
        fecha = e.control.value
        fecha_formateada = datetime.strftime(fecha, "%d/%m/%Y")
        self.fecha_button.content.controls[1].value = fecha_formateada
        #self.fecha_button.text = datetime.strftime(e.control.value, "%d/%m/%Y")
        self.fecha_indicada = e.control.value
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
            self.cuerpo.value = ""
            self.cuerpo.update()
            self.grabar_datos_tab1()

    # FUNCIONES TAB 3
    def crear_jaulas(self):
        self.jaula_buttons = []
        self.jaulas.controls.clear() 
        sql = f"SELECT jaulas"
        sql = f"SELECT jaulas.id, jaulas.jaula, jaulas.jaula_imagen_izq, jaulas.jaula_imagen_der FROM jaulas WHERE idsolicitud = {self.nIDSolicitud}"
        jaulas = ejecutar_sql(sql)
        if not jaulas:
            return

        for jaula in jaulas:
            sql = f"SELECT id FROM jaulas_detalle WHERE idsolicitud = {self.nIDSolicitud} and idjaula = {jaula[0]}"
            filas = ejecutar_sql(sql)
            color_texto = ft.Colors.WHITE
            if filas:
                color_texto = ft.Colors.YELLOW_ACCENT_700
            
            button = ft.ElevatedButton(
                text=str(jaula[1]),
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_700,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    side=ft.BorderSide(width=2, color=ft.Colors.TRANSPARENT),
                ),
                scale=1.0,
                on_click=lambda e, j=jaula[0], t=jaula[1]: self.manejar_click(e, j, t),
                data=jaula[0]
            )
            self.jaulas.controls.append(button)
            self.jaula_buttons.append(button)  # Agregar cada botón a la lista dentro del bucle

    def eliminar_registro(self, e):
        if e.control.data:
            sql = f"DELETE FROM jaulas_detalle WHERE id = {e.control.data}"
            ejecutar_sql(sql)
            self.show_message("Imagen eliminada")
            self.mostrar_imagenes_jaula()

    def manejar_click(self, e, jaula_id=None, jaula_text=None):
        if hasattr(self, 'selected_button'):
            self.selected_button.bgcolor = ft.Colors.GREEN_700
            self.selected_button.color = ft.Colors.WHITE
            self.selected_button.style.side = ft.BorderSide(width=2, color=ft.Colors.TRANSPARENT)
            self.selected_button.scale = 1.0
            self.selected_button.update()

        # Update newly selected button
        self.selected_button = e.control
        self.selected_button.bgcolor = ft.Colors.BLUE_700
        self.selected_button.color = ft.Colors.WHITE
        self.selected_button.style.side = ft.BorderSide(width=2, color=ft.Colors.YELLOW)
        self.selected_button.scale = 1.1
        self.selected_button.update()

        # Usar los parámetros pasados o los valores del control
        self.jaula_seleccionada = jaula_id if jaula_id is not None else e.control.data
        self.selected_button_text = jaula_text if jaula_text is not None else e.control.text
        self.mostrar_imagenes_jaula()

    def grabar_descripcion(self, e):
        id_jaula = e.control.data
        descripcion = e.control.value
        if e.control.label != descripcion:
            sql = f"UPDATE jaulas_detalle SET descripcion = '{descripcion}' WHERE id = {id_jaula}"
            e.control.label = descripcion
            e.control.update()
            ejecutar_sql(sql)

    def mostrar_imagenes_jaula(self):
        self.image_list.controls.clear()
        sql = f"SELECT jaulas_detalle.id, jaulas.id AS idjaula, jaulas.jaula, jaulas.jaula_imagen_izq, jaulas.jaula_imagen_der, jaulas_detalle.descripcion, jaulas_detalle.multimedia FROM jaulas_detalle LEFT JOIN jaulas ON jaulas.id = jaulas_detalle.idjaula WHERE jaulas_detalle.idsolicitud = {self.nIDSolicitud} and jaulas_detalle.idjaula = {self.jaula_seleccionada} ORDER BY jaulas_detalle.id DESC"
        sql = f"SELECT jaulas_detalle.id, jaulas.id AS idjaula, jaulas.jaula, jaulas_detalle.descripcion, jaulas_detalle.multimedia FROM jaulas_detalle LEFT JOIN jaulas ON jaulas.id = jaulas_detalle.idjaula WHERE jaulas_detalle.idsolicitud = {self.nIDSolicitud} and jaulas_detalle.idjaula = {self.jaula_seleccionada} ORDER BY jaulas_detalle.id DESC"
        sql = f"SELECT jaulas_detalle.id, jaulas.id AS idjaula, jaulas.jaula, jaulas_detalle.descripcion, jaulas_detalle.multimedia FROM jaulas_detalle LEFT JOIN jaulas ON jaulas.id = jaulas_detalle.idjaula WHERE jaulas_detalle.idsolicitud = {self.nIDSolicitud} and jaulas_detalle.idjaula = {self.jaula_seleccionada} ORDER BY jaulas_detalle.id DESC"
        reg_imagenes = ejecutar_sql(sql)
        self.image_list.controls.clear()

        nI = 0
        for imagen in reg_imagenes:
            nI += 1
            image_item = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Image(
                            src_base64=imagen[4],
                            width=200,
                            height=150,
                            fit=ft.ImageFit.COVER
                        ),
                        ft.TextField(
                            value=imagen[3],
                            label=imagen[3],
                            multiline=True,
                            min_lines=3,
                            max_lines=3,
                            expand=2,
                            on_blur=lambda e: self.grabar_descripcion(e),
                            data=imagen[0],
                            border_color=ft.Colors.GREEN_400
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            on_click=lambda e: self.eliminar_registro(e),
                            icon_color="red",
                            tooltip="Eliminar",
                            data=imagen[0]
                        ),
                    ])
                ]),
                padding=10,
                border_radius=10,
                margin=5
            )
            self.image_list.controls.append(image_item)

        self.nRegistros = nI
        self.selected_jaula.value = f"Jaula: {self.selected_button_text}" if hasattr(self, 'selected_button_text') else "Jaula: "
        self.selected_jaula.update()
        if nI == 0:
            self.image_container.visible = False
        else:
            self.image_container.visible = True
        self.registros.value = f"Imágenes: {self.nRegistros}"
        self.page.update()

    def crear_interfaz(self):
        async def adjuntar(e):
            self.btn_Subir_Adjunto.disabled = len(self.archivos) == 3
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
            else:
                self.show_message("No se pueden adjuntar más de 4 archivos.")

            if len(self.archivos) > 0:
                nArchivo = 1
                for archivo in self.archivos:
                    sNombre = os.path.basename(archivo['nombre'])
                    sContenido = archivo['contenido']
                    sql = f"UPDATE solicitudes SET archivo_nombre{str(nArchivo)} = '{sNombre}', archivo{str(nArchivo)} = '{sContenido}' WHERE id = {self.nIDSolicitud}"
                    ejecutar_sql(sql)
                    nArchivo += 1

        async def on_click_subir_archivo(e):
            if self.jaula_seleccionada:
                # Usar el nuevo SubirArchivoManager - el contenedor se mostrará automáticamente durante la carga
                await self.subir_archivo.seleccionar_archivo()
                archivo_subido_jaula = await self.subir_archivo.get_archivo_subido()
                await asyncio.sleep(2)
                if archivo_subido_jaula and archivo_subido_jaula != ["", None]:
                    # Extraer solo el nombre base del archivo (sin ruta)
                    nombre_archivo = os.path.basename(archivo_subido_jaula)
                    archivo_subido_jaula_contenido = self.subir_archivo.get_archivo_contenido()
                    sql = f"INSERT INTO jaulas_detalle (idsolicitud, idjaula, multimedia, descripcion) VALUES ({self.nIDSolicitud}, {self.jaula_seleccionada}, '{archivo_subido_jaula_contenido}', '')"
                    ejecutar_sql(sql)
                    self.mostrar_imagenes_jaula()
                else:
                    print("No se seleccionó ningún archivo.")
            else:
                self.selected_jaula.value = "No ha seleccionado ninguna jaula"
                self.selected_jaula.update()
            self.subir_adjunto.container.visible = False
            self.subir_adjunto.container.update()

        # Inicializar componentes
        self.date_picker = ft.DatePicker(
            on_change=self.actualizar_fecha,
            first_date=datetime(datetime.now().year - 5, datetime.now().month, 1),
            last_date=datetime.now()
        )

        self.fecha_button = crear_boton_moderno(
            texto="Fecha",
            icono=ft.Icons.DATE_RANGE,
            #on_click=lambda e: self.date_picker.pick_date(),
            on_click=lambda e: self.pedir_fecha(),
            color_fondo=COLORES_MODERNOS["azul_primario"],
            ancho=120,
            alto=40
        )
        #self.fecha_button = ft.ElevatedButton(
        #    text="Seleccionar fecha",
        #    icon=ft.Icons.DATE_RANGE,
        #    on_click=lambda _: self.date_picker.pick_date()
        #)
        self.fecha_caption_input = ft.Text("Fecha:")
        self.fecha_input = ft.Row([
            self.fecha_caption_input,
            self.fecha_button,
        ])

        # TAB 1
        self.Realizo_trabajos.on_change = lambda e: self.on_change_realizo_trabajo()
        self.cbo_empresa.on_change = lambda e: self.grabar_datos_tab1()
        self.cbo_centros.on_change = lambda e: self.on_change_centros(e)
        self.num_jaulas.on_change = lambda e: self.grabar_datos_tab1()

        self.num_jaulas.keyboard_type = ft.KeyboardType.NUMBER, 
        self.num_jaulas.hint_text ="Solo enteros", 
        self.num_jaulas.on_change=lambda e: self.cambios_jaulas(e)

        self.desde.on_change = lambda e: self.grabar_datos_tab1()
        self.desde.keyboard_type = ft.KeyboardType.NUMBER, 
        self.num_jaulas.hint_text ="Solo enteros", 
        self.desde.on_change=lambda e: self.cambios_jaulas(e)

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
        self.btn_Subir_Adjunto = self.btn_Subir_Adjunto = crear_boton_moderno(
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
                    ft.Row([
                        ft.Column([
                            self.btn_Subir_Adjunto,
                            # Agregar el contenedor de progreso aquí
                            self.subir_adjunto.get_container()
                        ]), 
                        self.lista_archivos
                    ])
                ],
                spacing=10,  # Controla el espacio entre elementos
                expand=False
            )
        )

        
        # TAB 3
        self.selected_jaula = ft.Text("", size=20)

        self.image_list = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

        self.image_container = ft.Container(
            content=self.image_list,
            height=2000,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            padding=10,
            expand=True,
            visible=False
        )

        self.btn_Subir_Imagen = crear_boton_moderno(
            texto="Subir imagen", 
            color_fondo = COLORES_MODERNOS["azul_primario"], 
            on_click = on_click_subir_archivo, 
            icono = ft.Icons.UPLOAD_FILE,
            icon_color="green"
        )
        #ft.ElevatedButton(
        #    "Subir imagen", 
        #    on_click=on_click_subir_archivo, 
        #    icon=ft.Icons.UPLOAD_FILE, 
        #    icon_color=ft.Colors.GREEN
        #)

        self.tab3_container = ft.Container(
            content=ft.Column([
                ft.Container(expand=1),
                ft.Row([
                    self.btn_Subir_Imagen, 
                    self.selected_jaula,
                    # Agregar el contenedor de progreso aquí
                    self.subir_archivo.get_container(), 
                ]),
                self.jaula_container,
                self.registros,
                self.image_container
            ]),
            expand=True
        )

        self.tab3 = ft.Tab(text="Cargar Imágenes", content=ft.Column(
            [self.tab3_container]
        ))

        # Crear el objeto Tabs con las pestañas
        self.tabs = ft.Tabs(tabs=[self.tab1, self.tab2, self.tab3], animation_duration=300)

        if self.page:
            self.page.overlay.append(self.date_picker)

        sql = f"SELECT id FROM solicitudes WHERE id = {self.nIDSolicitud}"
        haydatos = ejecutar_sql(sql)
        if haydatos:
            self.crear_jaulas()
            self.mostrar_datos_tab1()
            self.mostrar_datos_tab2()
        else:
            self.titulo.value = self.caption + ". Nuevo"

        #self.page.add(self.titulo, self.tabs)

    #def abrir_dialogo(self, e, id=None):
    #    self.current_id = id
    
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
        self.archivos = ""
        self.archivos1 = ""
        self.archivos2 = ""
        self.archivos3 = ""
        self.archivos4 = ""
        self.archivo_nombre1 = ""
        self.archivo_nombre2 = ""
        self.archivo_nombre3 = ""
        self.archivo_nombre4 = ""

        #TAB 3
        self.limpiar_jaulas()
        self.page.update()
    
    def limpiar_jaulas(self):
        self.nRegistros = 0
        self.jaulas.controls.clear()
        self.jaula_buttons = []
        self.image_list.controls.clear()
        self.selected_jaula.value = ""
        self.registros.value = "Imágenes: 0"
        self.image_container.visible = False
        if hasattr(self, 'selected_button'):
            del self.selected_button
        self.jaula_seleccionada = ""

        # Agrega más condiciones según el tipo 
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
            self.crear_jaulas()
            self.mostrar_datos_tab1()
            self.mostrar_datos_tab2()
            self.titulo.value = f"{self.caption} N° {self.nIDSolicitud}"
            self.tabs.selected_index = 2
        else:
            fecha = datetime.now()
            idusuario = self.page.session.get("idusuario")
            #print("id usuario", idusuario)
            sql = f"INSERT INTO solicitudes (fecha, idcentro, idempresa, idtipo_informe, idoperador) VALUES ('{self.fecha_indicada}', 0, 0, 1, {idusuario})"
            self.nIDSolicitud = ejecutar_sql(sql)
            #print(f"SQL: {sql}")
            self.limpiar_controles()
            self.fecha_button.text = datetime.strftime(fecha, "%d/%m/%Y") if fecha != None else ""
            self.fecha_indicada = fecha
            self.titulo.value = self.caption + ". Nuevo"
        self.page.update()  # Update the entire page


def main(page: ft.Page):
    def Mostrar(e):
        informe_ui.actualizar(2)
        page.update()

    def Mostrar2(e):
        informe_ui.actualizar(0)
        page.update()

    informe_ui = InformeMortalidadUI(page, 0)
    informe_controls = informe_ui.build()

    page.add(
        ft.ElevatedButton("2", on_click=lambda e:Mostrar(e)),
        ft.ElevatedButton("0", on_click=lambda e:Mostrar2(e)),
        informe_controls)
    page.update()


if __name__ == "__main__":
    ft.app(target=main, assets_dir=assets_dir, upload_dir=upload_dir)

