import flet as ft
from conectarbd import ejecutar_sql, conectarBD, nuevo_registro, editar_registro, validar_registros_tabla
#import clases as clases
from variables_globales import usuario_logueado, upload_dir
from estilos_modernos import (
    COLORES_MODERNOS, 
    crear_boton_moderno,
    crear_campo_moderno,
)

class Pantalla:
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.page.clean()
        self.entidad = "sector"
        self.caption = "Sector"
        self.snackBar = ft.SnackBar(
            content=ft.Text("",color=ft.Colors.YELLOW),
            duration=5000,
            show_close_icon=True,
            close_icon_color=ft.Colors.RED
        )
        self.nombre_input = crear_campo_moderno(label="Nombre",    prefix_icon=ft.Icons.TEXT_FIELDS, width = 400) #ft.TextField(label="Nombre")
        self.dlg = ft.AlertDialog(
            title=ft.Text("Editar " + self.caption if id else "Agregar " + self.caption),
            content=ft.Column([self.nombre_input], tight=True),
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
        self.page.overlay.append(self.dlg)
        self.current_id = None
        self.page.overlay.append(self.snackBar)
        self.titulo = ft.Text(f"{self.caption}. Registros:", size=20)
        self.crear_interfaz()

    def show_message(self, message):
        self.snack_bar.content = ft.Text(message)
        self.snack_bar.open = True
        self.page.update()

    def crear_interfaz(self):
        self.tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", color="green", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nombre", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
            ],
            rows=[]
        )

        self.record_list = ft.ListView(
            width="100%",
            height=400,
            auto_scroll=False
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

    def abrir_dialogo(self, e, id=0):
        self.current_id = id

        if id:
            row = next((row for row in self.tabla.rows if row.cells[0].content.value == str(id)), None)
            if row:
                self.nombre_input.value = row.cells[1].content.value
        else:
            self.nombre_input.value = ""

        self.dlg.title = ft.Text("Editar " + self.caption if id else "Agregar " + self.caption)

        self.page.dialog = self.dlg
        self.dlg.open = True
        self.page.update()

    def cerrar_dialogo(self, e):
        self.dlg.open = False
        self.page.update()

    def guardar_cambios(self, e):
        id = self.current_id
        nuevo_nombre = self.nombre_input.value
        if not self.nombre_input.value:
            self.dlg.title = ft.Text("Debe inicar el nombre", color="yellow")
            self.nombre_input.focus()
            self.page.update()
            return
        if id:
            editar_registro(self.entidad, "s_nombre", f"{nuevo_nombre}", f"id = {id}")
        else:
            nuevo_registro(self.entidad, "s_nombre", f"{nuevo_nombre}")
        self.actualizar_tabla()
        self.cerrar_dialogo(e)

    def eliminar_registro(self, id):
        if validar_registros_tabla("solicitudes", "idsector", id):
            self.show_message("Error: El registro no se puede eliminar porque hay registros asociados en solicitudes.")
            return
        ejecutar_sql(f"DELETE FROM {self.entidad} WHERE id = {id}")
        self.show_message(f"{self.caption} eliminado")
        self.actualizar_tabla()

    def actualizar_tabla(self):
        sql = f"SELECT * FROM {self.entidad}"
        registros = ejecutar_sql(sql)
        self.tabla.rows.clear()
        self.titulo.value = f"Registros: {len(registros)}"
        for reg in registros:
            self.tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(reg[0]))),
                        ft.DataCell(ft.Text(reg[1])),
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
    ft.app(target=main)