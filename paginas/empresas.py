import flet as ft
from conectarbd import ejecutar_sql, nuevo_registro, editar_registro, validar_registros_tabla
from subir_archivo import SubirArchivoManager
from variables_globales import assets_dir, upload_dir
import os
import asyncio
from estilos_modernos import (
    COLORES_MODERNOS, 
    crear_boton_moderno,
    crear_campo_moderno,
)

class Pantalla:
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.page.clean()
        self.selected_files = ft.Text("")
        self.entidad = "empresas"
        self.caption = "Empresas"
        self.snackBar = ft.SnackBar(
            content=ft.Text("", color=ft.Colors.YELLOW),
            duration=5000,
            show_close_icon=True,
            close_icon_color=ft.Colors.RED
        )
        self.page.overlay.append(self.snackBar)
        self.titulo = ft.Text(f"{self.caption}. Registros:", size=20)
        self.logo_magen = ft.Image(src=ft.Icons.IMAGE_SEARCH, visible=True, width=20, height=20, tooltip="Logo", border_radius=5)  # Ajustar tamaño y agregar borde
        self.btn_Subir_Archivo = SubirArchivoManager(self.page, allowed_extensions=["png", "jpg", "jpeg", "gif"])
        self.archivo_subido = "/placeholder.svg"
        
        self.dlg = self.crear_dialog_empresa()
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
                ft.DataColumn(ft.Text("Contacto", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Cliente", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Encargado 1", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Encargado 2", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD))
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

        self.boton_agregar = crear_boton_moderno(
            texto=f"Agregar " + self.caption,
            color_fondo=COLORES_MODERNOS["azul_primario"],
            on_click=self.abrir_dialogo,
            icono=ft.Icons.ADD,
        )
        #self.boton_agregar = ft.ElevatedButton(
        #    text="Agregar " + self.caption,
        #    on_click=self.abrir_dialogo,
        #    icon=ft.Icons.ADD
        #)

        self.page.add(self.titulo, self.boton_agregar, self.tabla_container)
        self.actualizar_tabla()

    def abrir_dialogo(self, e, id=None):
        self.current_id = id
        self.actualizar_dialogo(id)
        self.dlg.open = True
        self.page.update()

    def crear_dialog_empresa(self, id=None):
        async def on_click_seleccionar(e):
            await self.btn_Subir_Archivo.seleccionar_archivo()
            self.archivo_subido = await self.btn_Subir_Archivo.get_archivo_subido()
            if self.archivo_subido and self.archivo_subido != ["", None]:
                contenido = self.btn_Subir_Archivo.get_archivo_contenido()
                self.con_Logo.content.src_base64 = contenido
                self.archivo_subido = contenido
                self.con_Logo.update()
            else:
                print("No se seleccionó ningún archivo.")
        
        nAncho = 400
        self.rut_input = crear_campo_moderno(label="RUT",    prefix_icon=ft.Icons.TEXT_FIELDS, width = nAncho)
        self.nombre_input = crear_campo_moderno(label="Nombre",    prefix_icon=ft.Icons.TEXT_FIELDS, width = nAncho)
        self.nombrecorto_input = crear_campo_moderno(label="Nombre corto",    prefix_icon=ft.Icons.TEXT_FIELDS, width = nAncho)
        self.contacto_input = crear_campo_moderno(label="Contacto",    prefix_icon=ft.Icons.TEXT_FIELDS, width = nAncho)
        self.cliente_input = crear_campo_moderno(label="Cliente",    prefix_icon=ft.Icons.TEXT_FIELDS, width = nAncho)
        self.encargado1_input = crear_campo_moderno(label="Encargado 1",    prefix_icon=ft.Icons.TEXT_FIELDS, width = nAncho)
        self.telefono_encargado1_input = crear_campo_moderno(label="Teléfono enc. 1",    prefix_icon=ft.Icons.TEXT_FIELDS, width = nAncho)
        self.encargado2_input = crear_campo_moderno(label="Encargado 2",    prefix_icon=ft.Icons.TEXT_FIELDS, width = nAncho)
        self.telefono_encargado2_input = crear_campo_moderno(label="Teléfono enc. 2",    prefix_icon=ft.Icons.TEXT_FIELDS, width = nAncho)
        self.encargado3_input = crear_campo_moderno(label="Encargado 3",    prefix_icon=ft.Icons.TEXT_FIELDS, width = nAncho)
        self.telefono_encargado3_input = crear_campo_moderno(label="Teléfono enc. 3",    prefix_icon=ft.Icons.TEXT_FIELDS, width = nAncho)
        self.direccion_input = crear_campo_moderno(label="Dirección",    prefix_icon=ft.Icons.TEXT_FIELDS, width = nAncho, multilinea=True)
        #self.rut_input = ft.TextField(label="RUT", border_color=ft.Colors.GREY_400)
        #self.nombre_input = ft.TextField(label="Nombre", border_color=ft.Colors.GREY_400)
        #self.nombrecorto_input = ft.TextField(label="Nombre corto", border_color=ft.Colors.GREY_400)
        #self.contacto_input = ft.TextField(label="Contacto", border_color=ft.Colors.GREY_400)
        #self.cliente_input = ft.TextField(label="Cliente", border_color=ft.Colors.GREY_400)
        #self.encargado1_input = ft.TextField(label="Encargado 1", border_color=ft.Colors.GREY_400)
        #self.telefono_encargado1_input = ft.TextField(label="Teléfono enc. 1", border_color=ft.Colors.GREY_400)
        #self.encargado2_input = ft.TextField(label="Encargado 2", border_color=ft.Colors.GREY_400)
        #self.telefono_encargado2_input = ft.TextField(label="Teléfono enc. 2", border_color=ft.Colors.GREY_400)
        #self.encargado3_input = ft.TextField(label="Encargado 3", border_color=ft.Colors.GREY_400)
        #self.telefono_encargado3_input = ft.TextField(label="Teléfono enc. 3", border_color=ft.Colors.GREY_400)
        #self.direccion_input = ft.TextField(label="Dirección", multiline=True, border_color=ft.Colors.GREY_400)
        #self.btn_Subir_Archivo = SubirArchivo(self.page)  # Pasar self.page en lugar de self

        progress_container = self.btn_Subir_Archivo.get_container()

        self.con_Logo = ft.Container(
            width=350,
            height=200,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            content=ft.Image(
                src=self.archivo_subido,
                width=350,
                height=200,
                fit=ft.ImageFit.CONTAIN,
            ),
        )

        self.btn_Presionar_Subir_Archivo = crear_boton_moderno(
            texto="Seleccionar archivo", 
            color_fondo=COLORES_MODERNOS["verde_exito"],
            on_click=on_click_seleccionar, 
            icono=ft.Icons.UPLOAD_FILE 
        )
        #self.btn_Presionar_Subir_Archivo = ft.ElevatedButton("Seleccionar archivo", on_click=on_click_seleccionar, icon=ft.Icons.UPLOAD_FILE, icon_color=ft.Colors.GREEN)
        self.con_Imagen = ft.Container(
            width=400,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.con_Logo,
                    ft.Container(height=10),  # Espaciador
                    self.btn_Presionar_Subir_Archivo,
                    progress_container
                ],
            ),
        )

        self.dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Agregar Empresas", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=800,
                content=ft.Column(
                    controls=[
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
                                            self.rut_input,
                                            self.nombre_input,
                                            self.nombrecorto_input,
                                            self.contacto_input,
                                            self.cliente_input,
                                            self.encargado1_input,
                                            self.telefono_encargado1_input,
                                            self.encargado2_input,
                                            self.telefono_encargado2_input,
                                            self.encargado3_input,
                                            self.telefono_encargado3_input,
                                            self.direccion_input
                                        ],
                                        spacing=10,
                                    ),
                                ),
                                # Columna derecha - Imagen y botón
                                self.con_Imagen,
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
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )        
        #self.nombre_input.focus()
        return self.dlg
    
    def actualizar_dialogo(self, id):
        if id:
            sql = f"SELECT rut, nombre, nombrecorto, logo, contacto, cliente, encargado1, telefono_encargado1, encargado2, telefono_encargado2, encargado3, telefono_encargado3, direccion FROM empresas WHERE id = {id}"
            row = ejecutar_sql(sql)
            if row:
                for registro in row:
                    rut, nombre, nombrecorto, logo, contacto, cliente, encargado1, telefono_encargado1, encargado2, telefono_encargado2, encargado3, telefono_encargado3, direccion = registro

                    self.rut_input.value = rut
                    self.nombre_input.value = nombre
                    self.nombrecorto_input.value = nombrecorto
                    self.contacto_input.value = contacto
                    self.cliente_input.value = cliente
                    #print(f"Encargado: {encargado1}")
                    self.encargado1_input.value = encargado1
                    self.telefono_encargado1_input.value = telefono_encargado1
                    self.encargado2_input.value = encargado2
                    self.telefono_encargado2_input.value = telefono_encargado2
                    self.encargado3_input.value = encargado3
                    self.telefono_encargado3_input.value = telefono_encargado3
                    self.direccion_input.value = direccion
                    self.archivo_subido = "/placeholder.svg"
                    if logo: 
                        self.archivo_subido = logo

                    self.con_Logo.content.src_base64 = logo
                    self.con_Logo.update()
        else:
            self.rut_input.value = ""
            self.nombre_input.value = ""
            self.nombrecorto_input.value = ""
            self.contacto_input.value = ""
            self.cliente_input.value = ""
            #print(f"Encargado: {encargado1}")
            self.encargado1_input.value = ""
            self.telefono_encargado1_input.value = ""
            self.encargado2_input.value = ""
            self.telefono_encargado2_input.value = ""
            self.encargado3_input.value = ""
            self.telefono_encargado3_input.value = ""
            self.direccion_input.value = ""
            self.archivo_subido = "/placeholder.svg"
            self.con_Logo.content.src_base64 = None
            self.con_Logo.update()


    def cerrar_dialogo(self, e):
        self.dlg.open = False
        self.page.update()

    def guardar_cambios(self, e):
        id = self.current_id
        if not self.rut_input.value:
            self.dlg.title = ft.Text("Debe indicar el RUT", color="yellow")
            self.rut_input.focus()
            self.page.update()
            return
        if not self.nombre_input.value:
            self.dlg.title = ft.Text("Debe indicar el nombre", color="yellow")
            self.nombre_input.focus()
            self.page.update()
            return
        if not self.nombre_input.value:
            self.dlg.title = ft.Text("Debe indicar el nombre corto", color="yellow")
            self.nombrecorto_input.focus()
            self.page.update()
            return
        
        sLogo = self.archivo_subido
        if sLogo == '/placeholder.svg':
            sLogo = ""
        if id:
            editar_registro(self.entidad, 
                "s_rut, s_nombre, s_nombrecorto, s_logo, s_direccion, s_contacto, s_cliente, s_encargado1, s_telefono_encargado1, s_encargado2, s_telefono_encargado2, s_encargado3, s_telefono_encargado3", 
                f"{self.rut_input.value}, {self.nombre_input.value}, {self.nombrecorto_input.value}, {sLogo}, {self.direccion_input.value}, {self.contacto_input.value}, {self.cliente_input.value}, {self.encargado1_input.value}, {self.telefono_encargado1_input.value}, {self.encargado2_input.value}, {self.telefono_encargado2_input.value}, {self.encargado3_input.value}, {self.telefono_encargado3_input.value}", 
                f"id = {id}"
            )
        else:
            nuevo_registro(
                self.entidad, 
                "s_rut, s_nombre, s_nombrecorto, s_logo, s_direccion, s_contacto, s_cliente, s_encargado1, s_telefono_encargado1, s_encargado2, s_telefono_encargado2, s_encargado3, s_telefono_encargado3", 
                f"{self.rut_input.value}, {self.nombre_input.value}, {self.nombrecorto_input.value}, {sLogo}, {self.direccion_input.value}, {self.contacto_input.value}, {self.cliente_input.value}, {self.encargado1_input.value}, {self.telefono_encargado1_input.value}, {self.encargado2_input.value}, {self.telefono_encargado2_input.value}, {self.encargado3_input.value}, {self.telefono_encargado3_input.value}", 
            )
        self.actualizar_tabla()
        self.cerrar_dialogo(e)

    def eliminar_registro(self, id):
        if validar_registros_tabla("solicitudes", "idempresa", id):
            self.show_message("Error: El registro no se puede eliminar porque hay registros asociados en solicitudes.")
            return
        ejecutar_sql(f"DELETE FROM {self.entidad} WHERE id = {id}")
        self.show_message(f"{self.caption} eliminado")
        self.actualizar_tabla()

    def actualizar_tabla(self):
        sql = f"SELECT id, nombre, contacto, cliente, concat(encargado1, '/', telefono_encargado1) as encargado1, concat(encargado2, '/', telefono_encargado2) as encargado2 FROM {self.entidad}"
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
                        ft.DataCell(ft.Text(reg[4] if reg[4] and reg[4] != "/" else "")),
                        ft.DataCell(ft.Text(reg[5] if reg[5] and reg[5] != "/" else "")),
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
    Pantalla(page)

if __name__ == "__main__":
    ft.app(target=main, assets_dir=assets_dir, upload_dir=upload_dir)
