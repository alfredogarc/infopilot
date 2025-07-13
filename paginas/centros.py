import flet as ft
from conectarbd import ejecutar_sql, nuevo_registro, editar_registro, validar_registros_tabla
from subir_archivo import SubirArchivoManager
#from funciones import mover_uploads_a
import asyncio
import os
from variables_globales import assets_dir, upload_dir
from funciones import validar_vacio, validar_enteros
import base64
from estilos_modernos import (
    COLORES_MODERNOS, 
    crear_boton_moderno,
    crear_campo_moderno,
    crear_dropdown_moderno
)


class Pantalla:
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.page.clean()
        self.selected_files = ft.Text("")
        self.entidad = "centros"
        self.caption = "Centros"
        self.snackBar = ft.SnackBar(
            content=ft.Text("", color=ft.Colors.YELLOW),
            duration=5000,
            show_close_icon=True,
            close_icon_color=ft.Colors.RED
        )
        self.page.overlay.append(self.snackBar)
        self.titulo = ft.Text(f"{self.caption}. Registros:", size=20)
        self.archivo_subido_jaula = "/placeholder.svg"
        self.archivo_subido_jaula_izq = "/placeholder.svg"
        self.archivo_subido_jaula_der = "/placeholder.svg"
        self.archivo_subido_jaula_izq_con_separador = "/placeholder.svg"
        self.archivo_subido_jaula_der_con_separador = "/placeholder.svg"
        self.archivo_subido_jaula_izq_sin_separador = "/placeholder.svg"
        self.archivo_subido_jaula_der_sin_separador = "/placeholder.svg"
        
        self.dlg = self.crear_dialog_centros()
        self.page.overlay.append(self.dlg)
        self.current_id = None
        self.crear_interfaz()

    def show_dialog(self, e):
        self.dlg.open = True
        self.page.update()

    def show_message(self, message):
        self.snackBar.content = ft.Text(message)
        self.snackBar.open = True
        self.page.update()

    def crear_interfaz(self):
        self.tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", color="green", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nombre", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Encargado", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Operador 1", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Operador 2", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("# Jaulas", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Desde", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
            ],
            rows=[]
        )

        self.record_list = ft.ListView(
            width="100%",
            height=400,
            auto_scroll=True
        )
        self.record_list.controls.append(self.tabla)

        self.tabla_container = ft.Container(
            content=self.record_list,
            height=400,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=ft.border_radius.all(5),
            padding=ft.padding.all(1),
            expand=True,
        )

        #self.boton_agregar = ft.ElevatedButton(
        #    text="Agregar " + self.caption,
        #    on_click=self.abrir_dialogo,
        #    icon=ft.Icons.ADD
        #)

        self.boton_agregar = crear_boton_moderno(
            texto=f"Agregar " + self.caption,
            color_fondo=COLORES_MODERNOS["azul_primario"],
            on_click=self.abrir_dialogo,
            icono=ft.Icons.ADD,
        )

        self.page.add(self.titulo, self.boton_agregar, self.tabla_container)
        self.actualizar_tabla()

    def abrir_dialogo(self, e, id=None):
        self.current_id = id
        self.actualizar_dialogo(id)
        self.dlg.open = True
        self.page.update()

    def crear_dialog_centros(self, id=None):
        async def on_click_seleccionar_Jaula(e):
            await self.btn_jaula.seleccionar_archivo()
            self.archivo_subido_jaula = await self.btn_jaula.get_archivo_subido()
            if self.archivo_subido_jaula and self.archivo_subido_jaula != ["", None]:
                contenido = self.btn_jaula.get_archivo_contenido()
                self.con_jaula.content.src_base64 = contenido
                self.archivo_subido_jaula = contenido
                self.con_jaula.update()
            else:
                print("No se seleccionó ningún archivo.")

        # Con tapas
        async def on_click_seleccionar_Izq(e):
            await self.btn_jaula_izq.seleccionar_archivo()
            self.archivo_subido_jaula_izq = await self.btn_jaula_izq.get_archivo_subido()
            if self.archivo_subido_jaula_izq and self.archivo_subido_jaula_izq != ["", None]:
                contenido = self.btn_jaula_izq.get_archivo_contenido()
                self.con_jaula_izq.content.src_base64 = contenido
                self.archivo_subido_jaula_izq = contenido
                self.con_jaula_izq.update()
            else:
                print("No se seleccionó ningún archivo.")

        async def on_click_seleccionar_Der(e):
            await self.btn_jaula_der.seleccionar_archivo()
            self.archivo_subido_jaula_der = await self.btn_jaula_der.get_archivo_subido()
            if self.archivo_subido_jaula_der and self.archivo_subido_jaula_der != ["", None]:
                contenido = self.btn_jaula_der.get_archivo_contenido()
                self.con_jaula_der.content.src_base64 = contenido
                self.archivo_subido_jaula_der = contenido
                self.con_jaula_der.update()
            else:
                print("No se seleccionó ningún archivo.")
        
        # Con SEPARADOR
        async def on_click_seleccionar_Izq_con_separador(e):
            await self.btn_jaula_izq_con_separador.seleccionar_archivo()
            self.archivo_subido_jaula_izq_con_separador = await self.btn_jaula_izq_con_separador.get_archivo_subido()
            if self.archivo_subido_jaula_izq_con_separador and self.archivo_subido_jaula_izq_con_separador != ["", None]:
                contenido = self.btn_jaula_izq_con_separador.get_archivo_contenido()
                self.con_jaula_izq_con_separador.content.src_base64 = contenido
                self.archivo_subido_jaula_izq_con_separador = contenido
                self.con_jaula_izq_con_separador.update()
            else:
                print("No se seleccionó ningún archivo.")
        
        async def on_click_seleccionar_Der_con_separador(e):
            await self.btn_jaula_der_con_separador.seleccionar_archivo()
            self.archivo_subido_jaula_der_con_separador = await self.btn_jaula_der_con_separador.get_archivo_subido()
            if self.archivo_subido_jaula_der_con_separador and self.archivo_subido_jaula_der_con_separador != ["", None]:
                contenido = self.btn_jaula_der_con_separador.get_archivo_contenido()
                self.con_jaula_der_con_separador.content.src_base64 = contenido
                self.archivo_subido_jaula_der_con_separador = contenido
                self.con_jaula_der_con_separador.update()
            else:
                print("No se seleccionó ningún archivo.")

       # Sin SEPARADOR
        async def on_click_seleccionar_Izq_sin_separador(e):
            await self.btn_jaula_izq_sin_separador.seleccionar_archivo()
            self.archivo_subido_jaula_izq_sin_separador = await self.btn_jaula_izq_sin_separador.get_archivo_subido()
            if self.archivo_subido_jaula_izq_sin_separador and self.archivo_subido_jaula_izq_sin_separador != ["", None]:
                contenido = self.btn_jaula_izq_sin_separador.get_archivo_contenido()
                self.con_jaula_izq_sin_separador.content.src_base64 = contenido
                self.archivo_subido_jaula_izq_sin_separador = contenido
                self.con_jaula_izq_sin_separador.update()
            else:
                print("No se seleccionó ningún archivo.")
        
        async def on_click_seleccionar_Der_sin_separador(e):
            await self.btn_jaula_der_sin_separador.seleccionar_archivo()
            self.archivo_subido_jaula_der_sin_separador = await self.btn_jaula_der_sin_separador.get_archivo_subido()
            if self.archivo_subido_jaula_der_sin_separador and self.archivo_subido_jaula_der_sin_separador != ["", None]:
                contenido = self.btn_jaula_der_sin_separador.get_archivo_contenido()
                self.con_jaula_der_sin_separador.content.src_base64 = contenido
                self.archivo_subido_jaula_der_sin_separador = contenido
                self.con_jaula_der_sin_separador.update()
            else:
                print("No se seleccionó ningún archivo.")

        nAncho = 400
        self.nombre_input = crear_campo_moderno(label="Nombre",    prefix_icon=ft.Icons.TEXT_FIELDS, width = nAncho)
        self.encargado    = crear_campo_moderno(label="Encargado", prefix_icon=ft.Icons.TEXT_FIELDS, width = nAncho)
        self.num_jaulas   = crear_campo_moderno(label="# Jaulas",  prefix_icon=ft.Icons.NUMBERS, keyboard_tipo=ft.KeyboardType.NUMBER, text_accion="Solo enteros",on_cambio=validar_enteros, width = nAncho)
        #ft.TextField(label="# Jaulas", border_color=ft.Colors.GREY_400, keyboard_type=ft.KeyboardType.NUMBER, hint_text="Solo enteros",on_change=validar_enteros)
        self.desde = crear_campo_moderno(label="Desde", prefix_icon=ft.Icons.NUMBERS, keyboard_tipo=ft.KeyboardType.NUMBER, text_accion="Solo enteros",on_cambio=validar_enteros, width = nAncho)
        #ft.TextField(label="Desde", border_color=ft.Colors.GREY_400, keyboard_type=ft.KeyboardType.NUMBER, hint_text="Solo enteros",on_change=validar_enteros)

        self.operadores1 = ejecutar_sql("select id, trim(concat(nombre, ' ', apellido)) as nombre from usuarios where idgrupo = 2")
        self.operadores2 = self.operadores1
        #self.combo_operador1 = ft.Dropdown(
        #    options=[ft.dropdown.Option("Ninguno", data=None)] + 
        #            [ft.dropdown.Option(operador[1], data=operador[0]) for operador in self.operadores1],
        #    label="Operador 1",
        #    border_color=ft.Colors.GREY_400
        #)
        #self.combo_operador2 = ft.Dropdown(
        #    options=[ft.dropdown.Option("Ninguno", data=None)] + 
        #            [ft.dropdown.Option(operador[1], data=operador[0]) for operador in self.operadores2],
        #    label="Operador 2",
        #    border_color=ft.Colors.GREY_400
        #)
        self.combo_operador1 = crear_dropdown_moderno(
            label="Operador 2",
            options_data=[("Ninguno", None)] + [(operador[1], operador[0]) for operador in self.operadores1],
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            width=400,
            #on_change=self.on_operador_change
        )
        self.combo_operador2 = crear_dropdown_moderno(
            label="Operador 1",
            options_data=[("Ninguno", None)] + [(operador[1], operador[0]) for operador in self.operadores2],
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            width=400,
            #on_change=self.on_operador_change
        )

        self.btn_jaula = SubirArchivoManager(self.page, allowed_extensions=["png", "jpg", "jpeg", "gif"])
        self.btn_jaula_izq = SubirArchivoManager(self.page, allowed_extensions=["png", "jpg", "jpeg", "gif"])
        self.btn_jaula_der = SubirArchivoManager(self.page, allowed_extensions=["png", "jpg", "jpeg", "gif"])
        self.btn_jaula_izq_con_separador = SubirArchivoManager(self.page, allowed_extensions=["png", "jpg", "jpeg", "gif"])
        self.btn_jaula_der_con_separador = SubirArchivoManager(self.page, allowed_extensions=["png", "jpg", "jpeg", "gif"])
        self.btn_jaula_izq_sin_separador = SubirArchivoManager(self.page, allowed_extensions=["png", "jpg", "jpeg", "gif"])
        self.btn_jaula_der_sin_separador = SubirArchivoManager(self.page, allowed_extensions=["png", "jpg", "jpeg", "gif"])

        self.btn_Presionar_Subir_Jaula = crear_boton_moderno(
            texto="Jaula", 
            color_fondo=COLORES_MODERNOS["verde_exito"],
            on_click=on_click_seleccionar_Jaula, 
            icono=ft.Icons.UPLOAD_FILE,
            ancho = 200
        )
        #ft.ElevatedButton("Jaula", on_click=on_click_seleccionar_Jaula, icon=ft.Icons.UPLOAD_FILE, icon_color=ft.Colors.GREEN)
        self.btn_Presionar_Subir_Jaula_Izq = crear_boton_moderno(
            texto="Jaula Izq. con Tapa", 
            color_fondo=COLORES_MODERNOS["verde_exito"],
            on_click=on_click_seleccionar_Izq, 
            icono=ft.Icons.UPLOAD_FILE 
        )
        #ft.ElevatedButton("Jaula Izq. con Tapa", on_click=on_click_seleccionar_Izq, icon=ft.Icons.UPLOAD_FILE, icon_color=ft.Colors.GREEN)
        self.btn_Presionar_Subir_Jaula_Der = crear_boton_moderno(
            texto="Jaula Der. con Tapa", 
            color_fondo=COLORES_MODERNOS["verde_exito"],
            on_click=on_click_seleccionar_Der, 
            icono=ft.Icons.UPLOAD_FILE 
        )
        #ft.ElevatedButton("Jaula Der. con Tapa", on_click=on_click_seleccionar_Der, icon=ft.Icons.UPLOAD_FILE, icon_color=ft.Colors.GREEN)
        self.btn_Presionar_Subir_Jaula_Izq_con_separador = crear_boton_moderno(
            texto="Jaula Izq. con separador", 
            color_fondo=COLORES_MODERNOS["verde_exito"],
            on_click=on_click_seleccionar_Izq_con_separador, 
            icono=ft.Icons.UPLOAD_FILE 
        )
        #ft.ElevatedButton("Jaula Izq. con separador", on_click=on_click_seleccionar_Izq_con_separador, icon=ft.Icons.UPLOAD_FILE, icon_color=ft.Colors.GREEN)
        self.btn_Presionar_Subir_Jaula_Der_con_separador = crear_boton_moderno(
            texto="Jaula Der. con separador", 
            color_fondo=COLORES_MODERNOS["verde_exito"],
            on_click=on_click_seleccionar_Der_con_separador, 
            icono=ft.Icons.UPLOAD_FILE 
        )
        #ft.ElevatedButton("Jaula Der. con separador", on_click=on_click_seleccionar_Der_con_separador, icon=ft.Icons.UPLOAD_FILE, icon_color=ft.Colors.GREEN)
        self.btn_Presionar_Subir_Jaula_Izq_sin_separador = crear_boton_moderno(
            texto="Jaula Izq. sin separador", 
            color_fondo=COLORES_MODERNOS["verde_exito"],
            on_click=on_click_seleccionar_Izq_sin_separador, 
            icono=ft.Icons.UPLOAD_FILE 
        )
        #ft.ElevatedButton("Jaula Izq. sin separador", on_click=on_click_seleccionar_Izq_sin_separador, icon=ft.Icons.UPLOAD_FILE, icon_color=ft.Colors.GREEN)
        self.btn_Presionar_Subir_Jaula_Der_sin_separador = crear_boton_moderno(
            texto="Jaula Der. sin separador", 
            color_fondo=COLORES_MODERNOS["verde_exito"],
            on_click=on_click_seleccionar_Der_sin_separador, 
            icono=ft.Icons.UPLOAD_FILE 
        )
        #ft.ElevatedButton("Jaula Der. sin separador", on_click=on_click_seleccionar_Der_sin_separador, icon=ft.Icons.UPLOAD_FILE, icon_color=ft.Colors.GREEN)

        progress_container_btn_jaula = self.btn_jaula.get_container()
        progress_container_btn_jaula_izq = self.btn_jaula_izq.get_container()
        progress_container_btn_jaula_der = self.btn_jaula_der.get_container()
        progress_container_btn_jaula_izq_con_separador = self.btn_jaula_izq_con_separador.get_container()
        progress_container_btn_jaula_der_con_separador = self.btn_jaula_der_con_separador.get_container()
        progress_container_btn_jaula_izq_sin_separador = self.btn_jaula_izq_sin_separador.get_container()
        progress_container_btn_jaula_der_sin_separador = self.btn_jaula_der_sin_separador.get_container()
        
        self.con_jaula = ft.Container(
            width=300,
            height=300,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            content=ft.Image(
                src=self.archivo_subido_jaula,
                #width=600,
                height=250,
                fit=ft.ImageFit.CONTAIN,
            ),
        )

        self.con_Imagen_Jaula = ft.Container(
            #width=300,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.con_jaula,
                    ft.Container(height=10),  # Espaciador
                    self.btn_Presionar_Subir_Jaula,
                    progress_container_btn_jaula
                ],
            ),
        )


        # Con Tapas
        # IZQ
        self.con_jaula_izq = ft.Container(
            width=600,
            height=300,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            content=ft.Image(
                src=self.archivo_subido_jaula_izq,
                width=550,
                height=250,
                fit=ft.ImageFit.CONTAIN,
            ),
        )
        self.con_Imagen_Jaula_Izq = ft.Container(
            width=300,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.con_jaula_izq,
                    ft.Container(height=10),  # Espaciador
                    self.btn_Presionar_Subir_Jaula_Izq,
                    progress_container_btn_jaula_izq
                ],
            ),
        )

        # DER
        self.con_jaula_der = ft.Container(
            width=600,
            height=300,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            content=ft.Image(
                src=self.archivo_subido_jaula_der,
                width=550,
                height=250,
                fit=ft.ImageFit.CONTAIN,
            ),
        )
        self.con_Imagen_Jaula_Der = ft.Container(
            width=300,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.con_jaula_der,
                    ft.Container(height=10),  # Espaciador
                    self.btn_Presionar_Subir_Jaula_Der,
                    progress_container_btn_jaula_der
                ],
            ),
        )


        # Con Separadores
        # IZQ
        self.con_jaula_izq_con_separador = ft.Container(
            width=600,
            height=300,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            content=ft.Image(
                src=self.archivo_subido_jaula_izq_con_separador,
                width=550,
                height=250,
                fit=ft.ImageFit.CONTAIN,
            ),
        )
        self.con_Imagen_Jaula_Izq_con_separador = ft.Container(
            width=300,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.con_jaula_izq_con_separador,
                    ft.Container(height=10),  # Espaciador
                    self.btn_Presionar_Subir_Jaula_Izq_con_separador,
                    progress_container_btn_jaula_izq_con_separador
                ],
            ),
        )

        # DER
        self.con_jaula_der_con_separador = ft.Container(
            width=600,
            height=300,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            content=ft.Image(
                src=self.archivo_subido_jaula_der_con_separador,
                width=550,
                height=250,
                fit=ft.ImageFit.CONTAIN,
            ),
        )
        self.con_Imagen_Jaula_Der_con_separador = ft.Container(
            width=300,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.con_jaula_der_con_separador,
                    ft.Container(height=10),  # Espaciador
                    self.btn_Presionar_Subir_Jaula_Der_con_separador,
                    progress_container_btn_jaula_der_con_separador
                ],
            ),
        )


        # Sin Separadores
        # IZQ
        self.con_jaula_izq_sin_separador = ft.Container(
            width=600,
            height=300,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            content=ft.Image(
                src=self.archivo_subido_jaula_izq_sin_separador,
                width=550,
                height=250,
                fit=ft.ImageFit.CONTAIN,
            ),
        )
        self.con_Imagen_Jaula_Izq_sin_separador = ft.Container(
            width=300,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.con_jaula_izq_sin_separador,
                    ft.Container(height=10),  # Espaciador
                    self.btn_Presionar_Subir_Jaula_Izq_sin_separador,
                    progress_container_btn_jaula_izq_sin_separador
                ],
            ),
        )

        # DER
        self.con_jaula_der_sin_separador = ft.Container(
            width=600,
            height=300,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            content=ft.Image(
                src=self.archivo_subido_jaula_der_sin_separador,
                width=550,
                height=250,
                fit=ft.ImageFit.CONTAIN,
            ),
        )
        self.con_Imagen_Jaula_Der_sin_separador = ft.Container(
            width=300,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.con_jaula_der_sin_separador,
                    ft.Container(height=10),  # Espaciador
                    self.btn_Presionar_Subir_Jaula_Der_sin_separador,
                    progress_container_btn_jaula_der_sin_separador
                ],
            ),
        )

        tab_jaula_completa = ft.Tab(
            text="Jaula completa",
            content=ft.Container(
                height=600,  # Altura fija para el contenido
                content=self.con_Imagen_Jaula
            )
        )

        tab_jaula = ft.Tab(
            text="Jaula con Tapa",
            content=ft.Row(
                controls=[
                    self.con_Imagen_Jaula_Izq,
                    self.con_Imagen_Jaula_Der,
                ],
            )
        )

        tab_jaula_con_separador = ft.Tab(
            text="Jaula con Separador",
            content=ft.Row(
                controls=[
                    self.con_Imagen_Jaula_Izq_con_separador,
                    self.con_Imagen_Jaula_Der_con_separador,
                ],
            )
        )

        tab_jaula_sin_separador = ft.Tab(
            text="Jaula sin Separador",
            content=ft.Row(
                controls=[
                    self.con_Imagen_Jaula_Izq_sin_separador,
                    self.con_Imagen_Jaula_Der_sin_separador,
                ],
            )
        )

        tab_view = ft.Tabs(
            tabs=[tab_jaula_completa, tab_jaula, tab_jaula_con_separador, tab_jaula_sin_separador], 
            animation_duration=40,
            expand=True,
            selected_index=0
        )

        self.dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Agregar {self.caption}", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=1050,
                height=1050,
                content=ft.Column(
                    controls=[
                        ft.Divider(height=20, color=ft.Colors.GREY_300),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                # Columna izquierda - Campos de texto
                                ft.Container(
                                    width=400,
                                    padding=ft.padding.only(right=20),
                                    content=ft.Column(
                                        controls=[
                                            self.nombre_input,
                                            self.encargado,
                                            self.combo_operador1,
                                            self.combo_operador2,
                                            self.num_jaulas,
                                            self.desde
                                        ],
                                        spacing=10,
                                    ),
                                ),
                                ft.Container(
                                    width=800,
                                    height=600,
                                    content=tab_view,
                                ),
                            ],
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
            actions=[
                crear_boton_moderno(
                    texto="Cancelar",
                    color_fondo=COLORES_MODERNOS["rojo_cerrar"],
                    on_click=self.cerrar_dialogo,
                    icono=ft.Icons.CANCEL
                ),
                crear_boton_moderno(
                    texto="Guardar",
                    color_fondo=COLORES_MODERNOS["azul_primario"],
                    on_click=lambda e: self.guardar_cambios(e),
                    icono=ft.Icons.SAVE
                ),
                #ft.TextButton("Guardar", on_click=lambda _: print("Guardando...")),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )        
        #self.nombre_input.focus()
        return self.dlg

    def actualizar_dialogo(self, id):
        if id:
            sql = f"SELECT centro, encargado, idoperador1, idoperador2, jaula_imagen, jaula_izq, jaula_der, jaula_izq_con_separador, jaula_der_con_separador, jaula_izq_sin_separador, jaula_der_sin_separador, jaulas, jaula_desde FROM centros WHERE id = {id}"
            row = ejecutar_sql(sql)
            if row:
                for registro in row:
                    centro, encargado, operador1, operador2, jaula_imagen, jaula_izq, jaula_der, jaula_izq_con_separador, jaula_der_con_separador, jaula_izq_sin_separador, jaula_der_sin_separador, jaulas, jaula_desde = registro

                    self.nombre_input.value = centro
                    self.encargado.value = encargado
                
                    self.combo_operador1.value = next((option.key for option in self.combo_operador1.options if option.data == operador1), None)
                    self.combo_operador2.value = next((option.key for option in self.combo_operador2.options if option.data == operador2), None)

                    self.archivo_subido_jaula = "/placeholder.svg"
                    self.archivo_subido_jaula_izq = "/placeholder.svg"
                    self.archivo_subido_jaula_der = "/placeholder.svg"
                    self.archivo_subido_jaula_izq_con_separador = "/placeholder.svg"
                    self.archivo_subido_jaula_der_con_separador = "/placeholder.svg"
                    self.archivo_subido_jaula_izq_sin_separador = "/placeholder.svg"
                    self.archivo_subido_jaula_der_sin_separador = "/placeholder.svg"
                    if jaula_imagen: 
                        self.archivo_subido_jaula = jaula_imagen
                    if jaula_izq: 
                        self.archivo_subido_jaula_izq = jaula_izq
                    if jaula_der: 
                        self.archivo_subido_jaula_der = jaula_der
                    if jaula_izq_con_separador: 
                        self.archivo_subido_jaula_izq_con_separador = jaula_izq_con_separador
                    if jaula_der_con_separador: 
                        self.archivo_subido_jaula_der_con_separador = jaula_der_con_separador
                    if jaula_izq_sin_separador: 
                        self.archivo_subido_jaula_izq_sin_separador = jaula_izq_sin_separador
                    if jaula_der_sin_separador: 
                        self.archivo_subido_jaula_der_sin_separador = jaula_der_sin_separador
                    self.con_jaula.content.src_base64 = jaula_imagen
                    self.con_jaula_izq.content.src_base64 = self.archivo_subido_jaula_izq
                    self.con_jaula_der.content.src_base64 = self.archivo_subido_jaula_der
                    self.con_jaula_izq_con_separador.content.src_base64 = self.archivo_subido_jaula_izq_con_separador
                    self.con_jaula_der_con_separador.content.src_base64 = self.archivo_subido_jaula_der_con_separador
                    self.con_jaula_izq_sin_separador.content.src_base64 = self.archivo_subido_jaula_izq_sin_separador
                    self.con_jaula_der_sin_separador.content.src_base64 = self.archivo_subido_jaula_der_sin_separador
                    self.con_jaula.update()
                    self.con_jaula_izq.update()
                    self.con_jaula_der.update()
                    self.con_jaula_izq_con_separador.update()
                    self.con_jaula_der_con_separador.update()
                    self.con_jaula_izq_sin_separador.update()
                    self.con_jaula_der_sin_separador.update()
                    self.num_jaulas.value = jaulas
                    self.desde.value = jaula_desde
        else:
            self.nombre_input.value = ""
            self.encargado.value = ""
            self.desde.value = ""
            self.num_jaulas.value = ""
        
            self.combo_operador1.value = ""
            self.combo_operador2.value = ""

            self.archivo_subido_jaula = "/placeholder.svg"
            self.archivo_subido_jaula_izq = "/placeholder.svg"
            self.archivo_subido_jaula_der = "/placeholder.svg"
            self.archivo_subido_jaula_izq_con_separador = "/placeholder.svg"
            self.archivo_subido_jaula_der_con_separador = "/placeholder.svg"
            self.archivo_subido_jaula_izq_sin_separador = "/placeholder.svg"
            self.archivo_subido_jaula_der_sin_separador = "/placeholder.svg"
            self.con_jaula.content.src_base64 = None
            self.con_jaula_izq.content.src_base64 = None
            self.con_jaula_der.content.src_base64 = None
            self.con_jaula_izq_con_separador.content.src_base64 = None
            self.con_jaula_der_con_separador.content.src_base64 = None
            self.con_jaula_izq_sin_separador.content.src_base64 = None
            self.con_jaula_der_sin_separador.content.src_base64 = None
            self.con_jaula.update()
            self.con_jaula_izq.update()
            self.con_jaula_der.update()
            self.con_jaula_izq_con_separador.update()
            self.con_jaula_der_con_separador.update()
            self.con_jaula_izq_sin_separador.update()
            self.con_jaula_der_sin_separador.update()

    def cerrar_dialogo(self, e):
        self.dlg.open = False
        self.page.update()

    def guardar_cambios(self, e):
        id = self.current_id
        if not self.nombre_input.value:
            self.dlg.title = ft.Text("Debe indicar el nombre", color="yellow")
            self.nombre_input.focus()
            self.page.update()
            return
        idOpe1 = next((option.data for option in self.combo_operador1.options if option.key == self.combo_operador1.value), 0)
        idOpe2 = next((option.data for option in self.combo_operador2.options if option.key == self.combo_operador2.value), 0)

        if idOpe1 is None:
            idOpe1 = 0
        if idOpe2 is None:
            idOpe2 = 0
        sJaula = self.archivo_subido_jaula
        if sJaula == '/placeholder.svg':
            sJaula = ""
        
        sJaula_Izq = self.archivo_subido_jaula_izq
        if sJaula_Izq == '/placeholder.svg':
            sJaula_Izq = ""
        
        sJaula_Der = self.archivo_subido_jaula_der
        if sJaula_Der == '/placeholder.svg':
            sJaula_Der = ""

        sJaula_Izq_con_separador = self.archivo_subido_jaula_izq_con_separador
        if sJaula_Izq_con_separador == '/placeholder.svg':
            sJaula_Izq_con_separador = ""
        
        sJaula_Der_con_separador = self.archivo_subido_jaula_der_con_separador
        if sJaula_Der_con_separador == '/placeholder.svg':
            sJaula_Der_con_separador = ""

        sJaula_Izq_sin_separador = self.archivo_subido_jaula_izq_sin_separador
        if sJaula_Izq_sin_separador == '/placeholder.svg':
            sJaula_Izq_sin_separador = ""
        
        sJaula_Der_sin_separador = self.archivo_subido_jaula_der_sin_separador
        if sJaula_Der_sin_separador == '/placeholder.svg':
            sJaula_Der_sin_separador = ""

        nNum_Jaula = self.num_jaulas.value
        if nNum_Jaula is None:
            nNum_Jaula = 0
        nDesde = self.desde.value
        if nDesde is None:
            nDesde = 0
        sJaula64 = self.archivo_subido_jaula
        sJaula64_Izq = self.archivo_subido_jaula_izq
        sJaula64_Der = self.archivo_subido_jaula_der
        sJaula64_Izq_con_separador = self.archivo_subido_jaula_izq_con_separador
        sJaula64_Der_con_separador = self.archivo_subido_jaula_der_con_separador
        sJaula64_Izq_sin_separador = self.archivo_subido_jaula_izq_sin_separador
        sJaula64_Der_sin_separador = self.archivo_subido_jaula_der_sin_separador
        if id:
            editar_registro(
                self.entidad, 
                "s_centro, s_encargado, s_idoperador1, s_idoperador2, s_jaula_imagen, s_jaula_izq, s_jaula_der, s_jaula_izq_con_separador, s_jaula_der_con_separador, s_jaula_izq_sin_separador, s_jaula_der_sin_separador, s_jaulas, s_jaula_desde", 
                f"{self.nombre_input.value}, {self.encargado.value}, {idOpe1}, {idOpe2}, {sJaula64}, {sJaula64_Izq}, {sJaula64_Der}, {sJaula64_Izq_con_separador}, {sJaula64_Der_con_separador}, {sJaula64_Izq_sin_separador}, {sJaula64_Der_sin_separador}, {nNum_Jaula}, {nDesde}", 
                f"id = {id}"
            )
        else:
            nuevo_registro(
                self.entidad, 
                "s_centro, s_encargado, s_idoperador1, s_idoperador2, s_jaula_imagen, s_jaula_izq, s_jaula_der, s_jaula_izq_con_separador, s_jaula_der_con_separador, s_jaula_izq_sin_separador, s_jaula_der_sin_separador, s_jaulas, s_jaula_desde", 
                f"{self.nombre_input.value}, {self.encargado.value}, {idOpe1}, {idOpe2}, {sJaula64}, {sJaula64_Izq}, {sJaula64_Der}, {sJaula64_Izq_con_separador}, {sJaula64_Der_con_separador}, {sJaula64_Izq_sin_separador}, {sJaula64_Der_sin_separador}, {nNum_Jaula}, {nDesde}", 
            )
        self.actualizar_tabla()
        self.cerrar_dialogo(e)

    def eliminar_registro(self, id):
        if validar_registros_tabla("solicitudes", "idcentro", id):
            self.show_message("Error: El registro no se puede eliminar porque hay registros asociados en solicitudes.")
            return
        ejecutar_sql(f"DELETE FROM {self.entidad} WHERE id = {id}")
        self.show_message(f"{self.caption} eliminado")
        self.actualizar_tabla()

    def actualizar_tabla(self):
        sql = f"SELECT centros.id, centros.centro, centros.encargado, trim(concat(op1.nombre, ' ', op1.apellido)) as operador1, trim(concat(op2.nombre, ' ', op2.apellido)) as operador2, centros.jaula_imagen, centros.jaula_izq, centros.jaula_der, centros.jaulas, centros.jaula_desde FROM {self.entidad} left join usuarios op1 on centros.idoperador1 = op1.id left join usuarios op2 on centros.idoperador2 = op2.id"
        registros = ejecutar_sql(sql)
        self.tabla.rows.clear()
        self.titulo.value = f"Registros: {len(registros)}"
        for reg in registros:
            self.tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(reg[0]))),
                        ft.DataCell(ft.Text(reg[1])),
                        ft.DataCell(ft.Text(reg[2])),
                        ft.DataCell(ft.Text(reg[3])),
                        ft.DataCell(ft.Text(reg[4] if reg[4] else "")),
                        ft.DataCell(ft.Text(reg[8] if reg[8] else "")),
                        ft.DataCell(ft.Text(reg[9] if reg[9] else "")),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    on_click=lambda e, id=reg[0]: self.abrir_dialogo(e, id),
                                    icon_color="blue",
                                    tooltip="Editar"
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    on_click=lambda _, id=reg[0]: self.eliminar_registro(id),
                                    icon_color="red",
                                    tooltip="Eliminar"
                                )
                            ])
                        )
                    ]
                )
            )

        self.page.update()
    

def main(page: ft.Page):
    centros = Pantalla(page)
    page.update()

if __name__ == "__main__":
    ft.app(target=main, assets_dir=assets_dir, upload_dir=upload_dir)