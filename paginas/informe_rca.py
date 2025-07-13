import flet as ft
from conectarbd import ejecutar_sql, delete_record, nuevo_registro, editar_registro, validar_registros_tabla
from subir_archivo import SubirArchivoManager
from datetime import datetime, time, timedelta
from funciones import calcular_horas_diferencia, validar_enteros, format_timedelta, format_time, parse_time_string, validar_correos
from variables_globales import assets_dir, upload_dir
import warnings
import os
import pyperclip
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


class InformeRCAUI(ft.Control):
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
        self.selected_files = ft.Text("")
        self.entidad = "solicitudes"
        self.caption = "Informe RCA"
        self.snackBar = ft.SnackBar(
            content=ft.Text("", color=ft.Colors.YELLOW),
            duration=5000,
            show_close_icon=True,
            close_icon_color=ft.Colors.RED
        )
        self.page.overlay.append(self.snackBar)
        self.titulo = ft.Text(self.caption, size=20)

        #self.realizo_trabajos = ft.Checkbox(label="Realizó trabajos")
        self.puerto_cerrado = ft.ElevatedButton("Puerto cerrado", icon = ft.Icons.CLOSE_SHARP, on_click = lambda e: self.on_change_colocar_cuerpo_mensaje(1))
        self.falla_equpo = ft.ElevatedButton("Falla equipo", icon=ft.Icons.SMS_FAILED, on_click = lambda e: self.on_change_colocar_cuerpo_mensaje(2))
        self.traslado = ft.ElevatedButton("Traslado", icon=ft.Icons.EMOJI_TRANSPORTATION, on_click = lambda e: self.on_change_colocar_cuerpo_mensaje(3))
        self.asunto = crear_campo_moderno(label = "Asunto:", prefix_icon = ft.Icons.SUBJECT, width="100%" )
        self.para = crear_campo_moderno(label = "Para:", prefix_icon = ft.Icons.PERM_CONTACT_CALENDAR_ROUNDED, width="100%" )

        #self.asunto = ft.TextField(label="Asunto:", icon=ft.Icons.SUBJECT, text_size=13, height=30)
        #self.para = ft.TextField(label="Para:", icon=ft.Icons.EMAIL_SHARP, text_size=13, height=30)
        self.para_anterior = ""
        #crear_campo_moderno(label="Cuerpo:", prefix_icon=ft.Icons.DESCRIPTION, multilinea=True, min_l=3, max_l=6, expandir=True, width="100%")
        self.cuerpo = crear_campo_moderno(label="Cuerpo:", prefix_icon=ft.Icons.DESCRIPTION, width="100%", estilo = "input_memo")
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
        self.subir_adjunto = SubirArchivoManager(self.page, allowed_extensions=["*"])
        self.datos_correo = ft.ListView()
        self.contenedor_correo = ft.Container()

        self.crear_interfaz()

    def show_message(self, message):
        self.snackBar.content = ft.Text(message)
        self.snackBar.open = True
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
        sql = f"SELECT id, urgente, asunto, emails, cuerpo, archivo1, archivo_nombre1, archivo2, archivo_nombre2, archivo3, archivo_nombre3, archivo4, archivo_nombre4, fecha FROM solicitudes WHERE id = {self.nIDSolicitud}"
        datos = ejecutar_sql(sql)
        if datos:
            fecha = datos[0][13]
            self.fecha_button.text = datetime.strftime(fecha, "%d/%m/%Y")  if fecha != None  else ""
            self.fecha_indicada = fecha if fecha != None else ""
            #self.realizo_trabajos.value = 1 if datos[0][1] else 0
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
        #rt = 1 if self.realizo_trabajos.value else 0
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

        sql = f"UPDATE solicitudes SET asunto = '{asunto}', emails = '{para}', cuerpo = '{cuerpo}', archivo1 = '{archivo1}', archivo_nombre1 = '{archivo_nombre1}', archivo2 = '{archivo2}', archivo_nombre2 = '{archivo_nombre2}', archivo3 = '{archivo3}', archivo_nombre3 = '{archivo_nombre3}', archivo4 = '{archivo4}', archivo_nombre4 = '{archivo_nombre4}' WHERE id = {self.nIDSolicitud}"
        ejecutar_sql(sql)

    def actualizar_fecha(self, e):
        self.fecha_button.text = datetime.strftime(e.control.value, "%d/%m/%Y")
        self.fecha_indicada = e.control.value
        self.grabar_datos_tab2()
        self.page.update()

    def on_change_colocar_cuerpo_mensaje(self, nMensaje):
        sMensaje = ""
        if nMensaje == 1:       # Puerto cerrado
            sMensaje = """
            Se registra cese de actividades debido a estado de puerto cerrado y malas condiciones climáticas 
Adjunto link 

https://sitport.directemar.cl/#/gener
"""
        elif nMensaje == 2:     # Falla equipo
            sMensaje = "Se registra cese de actividades debido a problemas técnicos con los equipos rovs."
        else:                   # Traslado
            sMensaje = "Se registra cese de actividades debido a traslado logístico"
        
        self.cuerpo.value = f"""
Estimados

    {sMensaje}
Saludos Cordiales 

Giovanni Caripan
    """
        self.cuerpo.update()
        self.grabar_datos_tab2()

    def crear_interfaz(self):
        async def adjuntar(e):
            if len(self.archivos) < 4:
                await self.subir_adjunto.seleccionar_archivo()
                archivo_subido = await self.subir_adjunto.get_archivo_subido()
                if archivo_subido and archivo_subido != ["", None]:
                    archivo_subido_contenido = self.subir_adjunto.get_archivo_contenido()
                    self.archivos.append({
                        "nombre": archivo_subido,
                        "contenido": archivo_subido_contenido
                    })
                    self.actualizar_lista_adjuntos()
                else:
                    print("No se seleccionó ningún archivo.")

            if len(self.archivos) > 0:
                nArchivo = 1
                for archivo in self.archivos:
                    sNombre = archivo['nombre'].replace('uploads/', '')
                    sContenido = archivo['contenido'] #[:20]
                    sql = f"UPDATE solicitudes SET archivo_nombre{str(nArchivo)} = '{sNombre}', archivo{str(nArchivo)} = '{sContenido}' WHERE id = {self.nIDSolicitud}"
                    ejecutar_sql(sql)
                    nArchivo += 1

        # Inicializar componentes
        self.date_picker = ft.DatePicker(
            on_change=self.actualizar_fecha,
            first_date=datetime(datetime.now().year - 5, datetime.now().month, 1),
            last_date=datetime.now()
        )

        self.fecha_button = ft.ElevatedButton(
            text="Seleccionar fecha",
            icon=ft.Icons.DATE_RANGE,
            on_click=lambda _: self.date_picker.pick_date()
        )
        self.fecha_caption_input = ft.Text("Fecha:")
        self.fecha_input = ft.Row([
            self.fecha_caption_input,
            self.fecha_button,
        ])

        self.para.on_focus = lambda e: self.on_focus_para(e)
        self.para.on_blur = lambda e: self.on_blur_validar_correos(e)
        #self.realizo_trabajos.on_change = lambda e: self.on_change_realizo_trabajos()
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

        progress_container = self.subir_adjunto.get_container()
        self.informacion_rca = ft.Column([
            ft.Container(expand=1),
            ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=self.para,
                                    expand=7,
                                    width="60%"
                                ),
                                ft.Container(
                                    #content=self.realizo_trabajos,
                                    content=ft.Row([self.puerto_cerrado, self.falla_equpo, self.traslado]),
                                    expand=3,
                                    width="40%"
                                )
                            ],
                            spacing=10
                        ),
                        expand=True
                    ),
            self.asunto,
            self.cuerpo,
            ft.Row([self.btn_Subir_Adjunto, self.lista_archivos]),
            progress_container
        ])

        sql = f"SELECT id FROM solicitudes WHERE id = {self.nIDSolicitud}"
        haydatos = ejecutar_sql(sql)
        if haydatos:
            self.mostrar_datos_tab2()
        else:
            self.titulo.value = self.caption + ". Nuevo"

    def build(self):
        """Devuelve los controles que se deben agregar a la página."""
        objeto = ft.Column([self.titulo, self.informacion_rca])
        return objeto

    def limpiar_controles(self):
        self.Urgente.value = False
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

        self.page.update()
    

        # Agrega más condiciones según el tipo 
    def actualizar(self, id: int):
        """Actualiza los datos de la interfaz con el nuevo ID."""
        self.nIDSolicitud = id
        sql = f"SELECT id FROM solicitudes WHERE id = {self.nIDSolicitud}"
        haydatos = ejecutar_sql(sql)
        if haydatos:
            self.mostrar_datos_tab2()
            self.titulo.value = self.caption
        else:
            self.fecha_indicada = datetime.now().strftime("%Y-%m-%d")
            self.fecha_button.text = datetime.now().strftime("%Y-%m-%d")
            idusuario = self.page.session.get("idusuario")
            sql = f"INSERT INTO solicitudes (fecha, idcentro, idempresa, idtipo_informe, idoperador) VALUES ('{self.fecha_indicada}', 0, 0, 2, {idusuario})"
            print(sql)
            self.nIDSolicitud = ejecutar_sql(sql)
            self.titulo.value = self.caption + ". Nuevo"
        self.page.update()  # Update the entire page


def main(page: ft.Page):
    def Mostrar(e):
        informe_ui.actualizar(2)
        page.update()

    def Mostrar2(e):
        informe_ui.actualizar(0)
        page.update()

    informe_ui = InformeRCAUI(page, 0)
    informe_controls = informe_ui.build()

    page.add(
        ft.ElevatedButton("2", on_click=lambda e:Mostrar(e)),
        ft.ElevatedButton("0", on_click=lambda e:Mostrar2(e)),
        informe_controls)
    page.update()


if __name__ == "__main__":
    ft.app(target=main, assets_dir=assets_dir, upload_dir=upload_dir)

