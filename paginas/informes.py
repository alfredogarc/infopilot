import flet as ft
from conectarbd import ejecutar_sql, nuevo_registro, editar_registro, validar_registros_tabla
from paginas.informe_mortalidad import InformeMortalidadUI
from paginas.informe_rca import InformeRCAUI
from paginas.informe_redes import InformeRedesUI
from imprimir.reporte_mortalidad import Imprimir_Informe_Mortalidad
from imprimir.reporte_redes import Imprimir_Informe_Redes
from reportlab.lib.pagesizes import letter
from datetime import datetime
from funciones import enviar_correo, grabar_en_disco
from variables_globales import colores, estilos, upload_dir, assets_dir
from tema import aplicar_estilo, crear_gradiente_lineal
import asyncio
import os
from estilos_modernos import (
    COLORES_MODERNOS,
    crear_dropdown_moderno,
    crear_boton_moderno,
    crear_contenedor_moderno,
    crear_texto_moderno,
    crear_tabla_moderna
)
#from urllib.parse import quote


class Pantalla:
    def __init__(self, page: ft.Page):
        super().__init__()
        self.cards_row = None 
        self.page = page
        self.page.clean()
        self.selected_files = ft.Text("")
        self.entidad = "solicitudes"
        self.caption = "Informes"
        self.snackBar = ft.SnackBar(
            content=ft.Text("", color=colores["texto_claro"]),
            bgcolor=colores["acento"],
            action_color=colores["error"],
            duration=5000,
            show_close_icon=True,
            close_icon_color=colores["error"]
        )
        self.page.overlay.append(self.snackBar)
        self.titulo = crear_texto_moderno(
            f"{self.caption} - Registros: 0",
            size=24,
            color=COLORES_MODERNOS["texto_principal"],
            weight="bold"
        )
        #ft.Text(self.caption, size=24, color=colores["secundario"], weight="bold")

        self.informe_ui_Mortalidad = InformeMortalidadUI(self.page, 0)
        self.informe_controls_Mortalidad = self.informe_ui_Mortalidad.build()

        self.informe_ui_RCA = InformeRCAUI(self.page, 0)
        self.informe_controls_RCA = self.informe_ui_RCA.build()

        self.informe_ui_Redes = InformeRedesUI(self.page, 0)
        self.informe_controls_Redes = self.informe_ui_Redes.build()
        self.estados = ejecutar_sql("SELECT id, nombre FROM estado ORDER BY nombre")

        self.current_id = None
        self.tabs = None
        self.tab_dashboard = None
        self.tab_lista = None
        self.tab_mortalidad = None
        self.tab_rca = None
        self.tab_redes = None
        self.nRegistros = 0
        self.dialog_confirmar = ft.AlertDialog(
            title=ft.Text(""),
            content=ft.Text(""),
            actions=[],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(self.dialog_confirmar)
        self.crear_interfaz()

    def cambiar_tab(self, e):
        if self.tabs.selected_index == 0:
            if self.tabs:
                self.tabs.selected_index = 0
                #self.tabs.tabs[1].visible = True
                self.tabs.tabs[2].visible = False
                self.tabs.tabs[3].visible = False
                self.tabs.tabs[4].visible = False
        self.actualizar_tabla()
        self.page.update()

    def EditarInforme(self, id):
        if id >= 0:
            sql = f"SELECT idtipo_informe, id FROM solicitudes WHERE id = {id}"
            solicitud = ejecutar_sql(sql)
            if not solicitud:
                return
                
            tipo_informe = solicitud[0][0]
            if tipo_informe == 1:
                self.InformeMortalidad(id)
            elif tipo_informe == 2:
                self.InformeRCA(id)
            elif tipo_informe == 3:
                self.InformeRedes(id)
            else:
                self.show_message("Error: El tipo de informe no es válido")
            
    def InformeMortalidad(self, id):
        if id >= 0:
            self.tab_mortalidad.visible = True
            self.tab_rca.visible = False
            self.tab_redes.visible = False
            self.tabs.selected_index = 2
            self.informe_ui_Mortalidad.actualizar(id)
            self.tabs.update()
            self.page.update()

    def InformeRCA(self, id):
        if id >= 0:
            self.tab_mortalidad.visible = False
            self.tab_rca.visible = True
            self.tab_redes.visible = False
            self.tabs.selected_index = 2
            self.informe_ui_RCA.actualizar(id)
            self.tabs.update()
            self.page.update()

    def InformeRedes(self, id):
        if id >= 0:
            self.tab_mortalidad.visible = False
            self.tab_rca.visible = False
            self.tab_redes.visible = True
            self.tabs.selected_index = 2
            self.informe_ui_Redes.actualizar(id)
            self.tabs.update()
            self.page.update()

    def show_message(self, message):
        self.snackBar.content = ft.Text(message)
        self.snackBar.open = True
        self.page.update()
    
    async def show_message_anterior(self, message):
        dialog = ft.AlertDialog(content=ft.Text(message))
        await self.page.run_async(self.page.show_dialog(dialog))

    #def build(self):
    #    self.crear_interfaz()
    #    return self.tabs

    def crear_interfaz(self):
        self.cards_row = self.crear_cards_resumen(0, 0, 0)


        # Lista
        self.tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Fecha", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Informe", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Centro", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Empresa", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Operador", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                #ft.DataColumn(ft.Text("Sector", color=colores["secundario"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD))
            ],
            rows=[],
            border=ft.border.all(1, colores["primario"]),
            border_radius=8,
            vertical_lines=ft.border.BorderSide(1, colores["primario_claro"]),
            horizontal_lines=ft.border.BorderSide(1, colores["primario_claro"]),
        )

        self.record_list = ft.ListView(
            width="100%",
            height=10000,
            auto_scroll=False
        )
        self.record_list.controls.append(self.tabla)

        self.tabla_container = ft.Container(
            content=self.record_list,
            height=10000,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=ft.border_radius.all(5),
            padding=ft.padding.all(1),
            expand=True,
        )

        self.boton_actualizar = crear_boton_moderno(
            texto="Actualizar", 
            icono=ft.Icons.UPDATE, 
            on_click=self.actualizar_tabla,
            color_fondo=COLORES_MODERNOS["verde_exito"],
            ancho=120,
            alto=40,
            tooltip = "Actualizar lista de informes"
        )
        
        #ft.ElevatedButton(
        #    text="Actualizar", 
        #    on_click=self.actualizar_tabla,
        #    icon_color="yellow_accent",
        #    icon=ft.Icons.UPDATE
        #)

        #self.boton_agregar_mortalidad = ft.ElevatedButton(
        #    text="Mortalidad", 
        #    on_click=lambda _: self.InformeMortalidad(0),
        #    icon_color="green",
        #    icon=ft.Icons.ADD
        #)
        self.boton_agregar_mortalidad = crear_boton_moderno(
            texto="Mortalidad", 
            icono=ft.Icons.ADD, 
            on_click=lambda e: self.InformeMortalidad(0),
            color_fondo=COLORES_MODERNOS["verde_exito"],
            ancho=150,
            alto=40,
            tooltip = "Crear un nuevo informe de mortalidad"
            
        )
        self.boton_agregar_redes = crear_boton_moderno(
            texto="Redes", 
            icono=ft.Icons.ADD, 
            on_click=lambda e: self.InformeRedes(0),
            color_fondo=COLORES_MODERNOS["rojo_hover"],
            ancho=150,
            alto=40,
            tooltip = "Crear un nuevo informe de redes"
        )
        self.boton_agregar_rca = crear_boton_moderno(
            texto="Redes", 
            icono=ft.Icons.ADD, 
            on_click=lambda e: self.InformeRCA(0),
            color_fondo=COLORES_MODERNOS["morado_info"],
            ancho=150,
            alto=40,
            tooltip = "Crear un nuevo informe RCA"
        )
        
        #ft.ElevatedButton(
        #    text="RCA", 
        #    on_click=lambda _: self.InformeRCA(0), 
        #    icon_color="green",
        #    icon=ft.Icons.ADD
        #)

        self.tab_dashboard = ft.Tab(
            text="Dashboard",
            content=ft.Column([
                self.cards_row
            ]),
        )

        self.tab_lista = ft.Tab(
            text="Lista de Informes",
            content=ft.Column([
                self.titulo,
                ft.Row([self.boton_agregar_redes, self.boton_agregar_mortalidad, self.boton_agregar_rca, ft.Divider(), self.boton_actualizar]), 
                self.tabla_container
            ]),
        )

        self.tab_mortalidad = ft.Tab(
            text="Edicion",
            content=ft.Column([
                self.informe_controls_Mortalidad
            ]),
        )

        self.tab_rca = ft.Tab(
            text="Edicion",
            content=ft.Column([
                self.informe_controls_RCA
            ]),
        )
        self.tab_redes = ft.Tab(
            text="Edicion",
            content=ft.Column([
                self.informe_controls_Redes
            ]),
        )

        self.tab_lista.visible = True
        self.tab_mortalidad.visible = False
        self.tab_rca.visible = False
        self.tab_redes.visible = False

        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[self.tab_dashboard, self.tab_lista, self.tab_mortalidad, self.tab_rca, self.tab_redes],
            expand=1,
            on_change=self.cambiar_tab
        )

        self.page.add(self.tabs)
        self.actualizar_tabla()

    def abrir_dialogo(self, e, id=None):
        self.current_id = id

    def eliminar_registro(self, id):
        # Obtener datos del informe
        sql = f"SELECT tipo_informe.nombre, solicitudes.fecha FROM solicitudes LEFT JOIN tipo_informe ON solicitudes.idtipo_informe = tipo_informe.id WHERE solicitudes.id = {id}"
        #print("consulta de busqueda, ", sql)
        datos = ejecutar_sql(sql)
        if not datos:
            self.show_message("No se encontró el informe.")
            return
        tipo, fecha = datos[0]
        fecha_str = fecha.strftime("%d/%m/%Y") if fecha else "Sin fecha"
        mensaje = f"¿Desea eliminar el informe '{tipo}' de fecha {fecha_str}, id={id}?"

        # Crear el diálogo de confirmación
        def on_confirmar(e):
            self.dialog_confirmar.open = False
            self.page.update()
            # Validar si hay registros asociados antes de eliminar
            if validar_registros_tabla("solicitudes", "idempresa", id):
                self.show_message("Error: El registro no se puede eliminar porque hay registros asociados en solicitudes.")
                return
            ejecutar_sql(f"DELETE FROM jaulas WHERE idsolicitud = {id}")
            ejecutar_sql(f"DELETE FROM jaulas_detalle WHERE idsolicitud = {id}")
            ejecutar_sql(f"DELETE FROM pasos WHERE idsolicitud = {id}")
            ejecutar_sql(f"DELETE FROM solicitudes WHERE id = {id}")
            self.actualizar_tabla()
            self.show_message(f"{self.caption} eliminado {id}")
            self.actualizar_tabla()

        def on_cancelar(e):
            self.dialog_confirmar.open = False
            self.page.update()

        self.dialog_confirmar.title = ft.Text("Confirmar eliminación")
        self.dialog_confirmar.content = ft.Text(mensaje)
        self.dialog_confirmar.actions = [
            ft.TextButton("Cancelar", on_click=on_cancelar),
            ft.TextButton("Eliminar", on_click=on_confirmar),
        ]
        self.dialog_confirmar.open = True
        self.page.update()

    def enviar_correo_informe(self, nID):
        sql = f"SELECT asunto, emails, cuerpo, realizo_trabajos, archivo1, archivo_nombre1, archivo2, archivo_nombre2, archivo3, archivo_nombre3, archivo4, archivo_nombre4, idtipo_informe FROM solicitudes WHERE id = {nID}"    
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
            reporte = self.imprimir_informe(nID, abrir_url=False)
            adjuntos.append(reporte)
        if datos_correo[0][12] == 3:
            reporte = self.imprimir_informe(nID, abrir_url=False)
            adjuntos.append(reporte)
        enviar_correo(destinatarios=datos_correo[0][1], asunto=datos_correo[0][0], cuerpo=datos_correo[0][2], archivos_adjuntos=adjuntos, borrar_temporales=False)
        self.show_message("Correo enviado con éxito")

    def handle_print(self, id):
        self.page.run_async(self.imprimir_informe(id, True))

    def imprimir_informe(self, nID, abrir_url=True):
        sql = f"SELECT centros.centro, idtipo_informe, fecha FROM solicitudes LEFT JOIN centros on solicitudes.idcentro = centros.id WHERE solicitudes.id = {nID}"
        tipo_informe = ejecutar_sql(sql)
        centro, ti, fecha = tipo_informe[0]
        fecha_formateada = fecha.strftime("%d-%m-%Y") if fecha is not None else "Sin fecha"
        titulo = f"{centro} {fecha_formateada}"
        if ti == 1:
            titulo = f"Informe Mortalidad {titulo} {nID}.pdf"
            archivo = os.path.join(upload_dir, titulo)
            Reporte = Imprimir_Informe_Mortalidad(
                archivo, 
                id = nID, 
                pagesize=letter,
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )
            Reporte.generar_reporte()
        elif ti == 3:
            titulo = f"Informe Redes {titulo} {nID}.pdf"
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
                id = nID,
                pagesize=letter,
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )
            Reporte.generar_reporte()
        else:
            self.show_message("Tipo de informe no soportado")
            return None
        if abrir_url:
            pass
            #await self.page.download_async(archivo)
            #await self.show_message("Descarga del informe iniciada")
        print(2, "   ", archivo)
        return archivo

    def crear_columnas_totales(self, cantidad, idtipo_informe):
        columna1 = ft.Column([])
        columna1 = ft.Column([
            ft.Text(str(cantidad), size=24, weight="bold", color="#00e676"),
            ft.Text("TOTAL", size=12, color="#b0b8c9"),
        ])
        columna2 = ft.Column([]); columna3 = ft.Column([]); columna4 = ft.Column([]); columna5 = ft.Column([])
        nC = 1
        for estado in self.estados:
            sql = f"SELECT COUNT(*) as cantidad FROM estadistica_mortalidad WHERE idestado = {estado[0]} and idsolicitud in(SELECT id FROM solicitudes WHERE idtipo_informe = {idtipo_informe})"
            #print(sql)
            count_estado = ejecutar_sql(sql)[0][0]
            if nC == 1:
               columna2 = ft.Column([
                    ft.Text(str(count_estado), size=12, weight="bold", color="#ff5252"),
                    ft.Text(estado[1], size=10, color="#e0b0b0"),
                ])
            elif nC == 2:
                columna3 = ft.Column([
                    ft.Text(str(count_estado), size=12, weight="bold", color="#ff5252"),
                    ft.Text(estado[1], size=10, color="#e0b0b0"),
                ])
            elif nC == 3:
                columna4 = ft.Column([  
                    ft.Text(str(count_estado), size=12, weight="bold", color="#ff5252"),
                    ft.Text(estado[1], size=10, color="#e0b0b0"),
                ])
            elif nC == 4:
                columna5 = ft.Column([  
                    ft.Text(str(count_estado), size=12, weight="bold", color="#ff5252"),
                    ft.Text(estado[1], size=10, color="#e0b0b0"),
                ])
            nC += 1
        columnas = ft.Row([
            columna1,
            columna2,
            columna3,
            columna4, 
            columna5
        ], alignment="spaceBetween", spacing=20)
        return columnas
    
    def crear_cards_resumen(self, count_redes, count_mortalidad, count_rca):
        # Card Redes
        
        card_redes = ft.Card(
            content=ft.Container(
                bgcolor="#19223a",
                border=ft.border.all(1, "#00e676"),  # Verde brillante
                border_radius=10,
                padding=20,
                width=350,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.LAN, color="#00e676", size=32),
                        ft.Column([
                            ft.Text("Redes", weight="bold", size=18, color="white"),
                            ft.Text("Reportes de estado y mantenimiento", size=13, color="white"),
                        ]
                    )
                    ], alignment="start", spacing=10),
                    #ft.Text("Reportes de estado y mantenimiento", size=13, color="white"),
                    ft.Divider(height=10, color="#00e676"),
                    self.crear_columnas_totales(count_redes, 3),
                    ft.Divider(height=10, color="#00e676"),
                    ft.Container(height=10),
                    crear_boton_moderno(
                        texto="Crear Redes", 
                        icono=ft.Icons.ADD, 
                        on_click=lambda e: self.InformeRedes(0),
                        color_fondo=COLORES_MODERNOS["verde_exito"],
                        ancho=150,
                        alto=40,
                        tooltip = "Crear un nuevo informe de redes"
                    )
                    #ft.ElevatedButton("Crear Informes", bgcolor="#00e676", color="white", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)))
                ])
            )
        )
        # Card Mortalidad
        card_mortalidad = ft.Card(
            content=ft.Container(
                bgcolor="#2a1a1a",
                border=ft.border.all(1, "#00e676"),
                border_radius=10,
                padding=20,
                width=350,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.SICK, color="#ff5252", size=32),
                        ft.Column([
                            ft.Text("Mortalidad", weight="bold", size=18, color="white"),
                            ft.Text("Registros de mortalidad y análisis", size=13, color="white"),
                        ])
                    ], alignment="start", spacing=10),
                    ft.Divider(height=10, color="#00e676"),
                    self.crear_columnas_totales(count_mortalidad, 1),
                    ft.Divider(height=10, color="#00e676"),
                    ft.Container(height=10),
                    crear_boton_moderno(
                        texto="Crear Mortalidad", 
                        icono=ft.Icons.ADD, 
                        on_click=lambda e: self.InformeMortalidad(0),
                        color_fondo=COLORES_MODERNOS["rojo_hover"],
                        ancho=150,
                        alto=40,
                        tooltip = "Crear un nuevo informe de mortalidad"
                    )
                    #ft.ElevatedButton("Crear Informes", bgcolor="#ff5252", color="white", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)))
                ])
            )
        )
        # Card RCA
        card_rca = ft.Card(
            content=ft.Container(
                bgcolor="#1a223a",
                border=ft.border.all(1, "#00e676"),
                border_radius=10,
                padding=20,
                width=350,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.DESCRIPTION, color="#448aff", size=32),
                        ft.Column([
                            ft.Text("RCA", weight="bold", size=18, color="white"),
                            ft.Text("Informes generales y procedimientos", size=13, color="white"),
                        ])
                    ], alignment="start", spacing=10),
                    ft.Divider(height=10, color="#00e676"),
                    self.crear_columnas_totales(count_rca, 2),
                    ft.Divider(height=10, color="#00e676"),
                    ft.Container(height=10),
                    crear_boton_moderno(
                        texto="Crear RCA", 
                        icono=ft.Icons.ADD, 
                        on_click=lambda e: self.InformeRCA(0),
                        color_fondo=COLORES_MODERNOS["morado_info"],
                        ancho=150,
                        alto=40,
                        tooltip = "Crear un nuevo informe RCA"
                    )
                    #ft.ElevatedButton("Crear Informes", bgcolor="#448aff", color="white", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)))
                ])
            )
        )
        
        # Header de la carta principal
        header = ft.Row(
            [
                ft.Text("Gestión de Informes", size=22, weight="bold", color="white", expand=True),
                ft.Icon(ft.Icons.ARTICLE, color="#fff", size=32),
            ],
            alignment="spaceBetween",
            vertical_alignment="center"
        )

        # Carta principal que agrupa las 3 cards
        carta_informes = ft.Card(
            content=ft.Container(
                bgcolor="#10182b",
                border=ft.border.all(1, "#00e676"),
                border_radius=15,
                padding=50,
                content=ft.Column(
                    [
                        header,
                        ft.Container(height=10),
                        ft.Row([card_redes, card_mortalidad, card_rca], alignment="center", spacing=20),
                    ]
                )
            )
        )

        return carta_informes

    def actualizar_tabla(self, e=None):
        nReg = self.nRegistros
        sql = "SELECT solicitudes.id, solicitudes.fecha, tipo_informe.nombre as tipo_informe, centros.centro as centro, empresas.nombre as empresa, concat(usuarios.nombre, ' ', usuarios.apellido) as operador, sector.nombre as sector FROM solicitudes LEFT JOIN tipo_informe ON solicitudes.idtipo_informe = tipo_informe.id  LEFT JOIN centros ON solicitudes.idcentro = centros.id  LEFT JOIN usuarios ON solicitudes.idoperador = usuarios.id LEFT JOIN empresas ON solicitudes.idempresa = empresas.id LEFT JOIN sector ON solicitudes.idsector = sector.id ORDER BY solicitudes.fecha DESC, tipo_informe.nombre ASC"
        registros = ejecutar_sql(sql)

        # Consultas para obtener la cantidad de registros por tipo de informe
        sql_redes = "SELECT COUNT(*) FROM solicitudes WHERE idtipo_informe = 3"
        sql_mortalidad = "SELECT COUNT(*) FROM solicitudes WHERE idtipo_informe = 1"
        sql_rca = "SELECT COUNT(*) FROM solicitudes WHERE idtipo_informe = 2"

        count_redes = ejecutar_sql(sql_redes)[0][0]
        count_mortalidad = ejecutar_sql(sql_mortalidad)[0][0]
        count_rca = ejecutar_sql(sql_rca)[0][0]

        # Solo actualiza el contenido de la carta principal
        self.cards_row.content = self.crear_cards_resumen(count_redes, count_mortalidad, count_rca).content

        self.titulo.value = f"Informes: {len(registros)}"
        self.boton_agregar_mortalidad.content.controls[1].value = f"Mortalidad ({count_mortalidad})"
        self.boton_agregar_redes.content.controls[1].value = f"Redes ({count_redes})"
        self.boton_agregar_rca.content.controls[1].value = f"RCA ({count_rca})"
        self.nRegistros = len(registros)

        if self.nRegistros == 0:
            self.show_message("No hay informes")
        elif nReg == self.nRegistros:
            self.show_message("La cantidad de informes no ha cambiado")
        else:
            self.show_message("Informes actualizados")

        nReg = self.nRegistros
        self.tabla.rows.clear()
        for reg in registros:
            fecha_formateada = datetime.strftime(reg[1], "%d/%m/%Y") if reg[1] is not None else "Sin fecha"
            
            self.tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(reg[0]))),
                        ft.DataCell(ft.Text(fecha_formateada)),
                        ft.DataCell(ft.Text(reg[2])),
                        ft.DataCell(ft.Text(reg[3])),
                        ft.DataCell(ft.Text(reg[4])),
                        ft.DataCell(ft.Text(reg[5])),
                        #ft.DataCell(ft.Text(reg[6])),
                        ft.DataCell(
                            ft.Row([
                                #ft.IconButton(
                                #    icon=ft.Icons.PRINT,
                                #    on_click=lambda _, id=reg[0]: asyncio.run(self.imprimir_informe(id, abrir_url=False)),
                                #    icon_color="green",
                                #    tooltip="Imprimir Informe", 
                                #),
                                ft.IconButton(
                                    icon=ft.Icons.EMAIL,
                                    on_click=lambda _, id=reg[0]: self.enviar_correo_informe(id),
                                    icon_color="yellow",
                                    tooltip="Enviar por email el informe"
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    on_click=lambda e, id=reg[0]: self.EditarInforme(id),
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

        self.tabla.update()
        self.page.update()

def main(page: ft.Page):
    #aplicar_tema_moderno_a_pagina(page)
    page.scroll = True
    Pantalla(page)

if __name__ == "__main__":
    ft.app(target=main, assets_dir=assets_dir, upload_dir=upload_dir, view=ft.WEB_BROWSER, port=8501)

