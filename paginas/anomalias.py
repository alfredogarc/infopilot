import flet as ft
from conectarbd import ejecutar_sql, conectarBD, nuevo_registro, editar_registro, validar_registros_tabla
from estilos_modernos import (
    COLORES_MODERNOS, 
    crear_boton_moderno,
    crear_campo_moderno,
)

class Pantalla:
    def __init__(self, page):
        super().__init__()
        self.page = page
        #self.page.clean()
        self.entidad = "anomalias"
        self.caption = "Anomalías"
        self.snack_bar = ft.SnackBar(
            content=ft.Text("",color=ft.Colors.YELLOW),
            duration=5000,
            show_close_icon=True,
            close_icon_color=ft.Colors.RED
        )
        self.page.overlay.append(self.snack_bar)
        self.titulo = ft.Text(f"{self.caption}. Registros:", size=20)
        self.colors = [
            ("red", "rojo"), ("blue", "azul"), ("green", "verde"), ("yellow", "amarillo"), ("purple", "morado"), 
            ("orange", "naranja"), ("pink", "rosa"), ("cyan", "cian"), ("brown", "marron"), ("gray", "gris")
        ]

        self.color_buttons = [ft.ElevatedButton(
            content=ft.Text(color_es),
            bgcolor=color,
            color="white" if color not in ["yellow", "cyan"] else "black",
            on_click=lambda _, c=color, ce=color_es: self.change_color(c, ce)
        ) for color, color_es in self.colors]

        self.color_display = ft.Container(
            width=100,
            height=100,
            bgcolor=self.colors[0][0],
            border_radius=10,
        )
        # Inicializar el diálogo aquí
        self.dlg = ft.AlertDialog(
            title=ft.Text(""),
            content=ft.Column([], tight=True),
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
                #ft.TextButton("Guardar", on_click=lambda e: self.guardar_cambios(e)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(self.dlg)
        self.color_text = ft.Text(f"Color seleccionado: {self.colors[0][1]}")
        self.current_id = None
        self.crear_interfaz()

    def show_message(self, message):
        self.snack_bar.content = ft.Text(message)
        self.snack_bar.open = True
        self.page.update()
        
    def change_color(self, color: str, color_es: str):
        self.color_display.bgcolor = color
        self.color_text.value = f"Color seleccionado: {color_es}"
        self.page.update()

    def crear_interfaz(self):
        self.tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", color="green", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nombre", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Color", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
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
        #    text = f"Agregar " + self.caption,
        #    on_click=self.abrir_dialogo,
        #    icon=ft.Icons.ADD
        #)

        self.page.add(self.titulo, self.boton_agregar, self.tabla_container)
        
        self.actualizar_tabla()

    def actualizar_dialogo(self, id):        
        #self.nombre_input = ft.TextField(label="Nombre")
        self.nombre_input = crear_campo_moderno(
            label="Nombre",
            prefix_icon=ft.Icons.TEXT_FIELDS,
            #width=340
        )

        if id:
            row = next((row for row in self.tabla.rows if row.cells[0].content.value == str(id)), None)
            if row:
                self.nombre_input.value = row.cells[1].content.value
                color_value = row.cells[2].content.bgcolor
                self.color_display.bgcolor = color_value
                color_es = next((color_es for color, color_es in self.colors if color == color_value), color_value)
                self.color_text.value = f"Color seleccionado: {color_es}"
        else:
            self.color_display.bgcolor = self.colors[0][0]
            self.color_text.value = f"Color seleccionado: {self.colors[0][1]}"

        # Dividir los botones de colores en dos filas
        mitad = len(self.color_buttons) // 2
        fila1 = self.color_buttons[:mitad]
        fila2 = self.color_buttons[mitad:]

        # Actualizar el diálogo existente en lugar de crear uno nuevo
        self.dlg.title = ft.Text("Editar " + self.caption if id else "Agregar " + self.caption)
        self.dlg.content = ft.Column([
            self.nombre_input,
            self.color_display,
            self.color_text,
            ft.Row(fila1, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row(fila2, alignment=ft.MainAxisAlignment.CENTER)
        ], tight=True)
        #self.dlg.actions[-1].on_click = lambda _: self.guardar_cambios(id)

    def abrir_dialogo(self, e, id=0):
        self.current_id = id
        self.actualizar_dialogo(id)
        self.dlg.open = True
        self.page.update()

    def cerrar_dialogo(self, e):
        self.dlg.open = False
        self.page.dialog = None
        self.page.update()

    def guardar_cambios(self, e):
        id = self.current_id
        nuevo_nombre = self.nombre_input.value
        nuevo_color = self.color_display.bgcolor
        if not self.nombre_input.value:
            self.dlg.title = ft.Text("Debe inicar el nombre", color="yellow")
            self.nombre_input.focus()
            self.page.update()
            return
        if id:
            sql = f"UPDATE anomalias SET nombre = '{nuevo_nombre}', color = '{nuevo_color}' WHERE id = {id}"
        else:
            sql = f"INSERT INTO anomalias (nombre, color) VALUES ('{nuevo_nombre}', '{nuevo_color}')"
        ejecutar_sql(sql)
        self.actualizar_tabla()
        self.cerrar_dialogo(e)

    def eliminar_registro(self, id):
        if validar_registros_tabla("solicitudes", "idanomalia", id):
            self.show_message("Error: El registro no se puede eliminar porque hay registros asociados en solicitudes.")
            return
        ejecutar_sql(f"DELETE FROM {self.entidad} WHERE id = {id}")
        self.show_message(f"{self.caption} eliminado")
        self.actualizar_tabla()

    def actualizar_tabla(self):
        registros = ejecutar_sql("SELECT * FROM anomalias")
        self.tabla.rows.clear()
        self.titulo.value = f"Registros: {len(registros)}"
        for reg in registros:
            self.tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(reg[0]))),
                        ft.DataCell(ft.Text(reg[1])),
                        ft.DataCell(ft.Container(
                            width=20,
                            height=20,
                            bgcolor=reg[2],
                            border_radius=5
                        )),
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


