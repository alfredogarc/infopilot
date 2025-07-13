import flet as ft
from conectarbd import ejecutar_sql
from variables_globales import usuario_logueado, assets_dir, upload_dir, colores
from estilos_modernos import (
    COLORES_MODERNOS,
    crear_dropdown_moderno,
    crear_boton_moderno,
    crear_contenedor_moderno,
    crear_texto_moderno,
    crear_tabla_moderna
)
from datetime import datetime
import mysql.connector

class EstadisticasView:
    def __init__(self, page, open_date_picker=None, date_picker=None):
        self.page = page
        self.open_date_picker = open_date_picker
        self.date_picker = date_picker
        self.page.clean()
        self.caption = "Estadística"
        self.desde_hasta = 0
        self.desde_date = None
        self.hasta_date = None
        self.color_boton_limpiar = COLORES_MODERNOS["amarillo_advertencia"]

        self.titulo = crear_texto_moderno(self.caption, color=COLORES_MODERNOS["texto_principal"], size=24)
        self.mensaje_consulta = ft.Text("Mensaje", visible=False, color=COLORES_MODERNOS["rojo_critico"])
        self.altura_combos = 40
        self.tabla_container = crear_contenedor_moderno()
        self.total_tabla = crear_texto_moderno("Total: ", color=COLORES_MODERNOS["texto_principal"], size=20)
        self.total_grafico = crear_texto_moderno("Total: ", color=COLORES_MODERNOS["texto_principal"], size=20)
        self.filtros_row = None
        
        # Snackbar para mensajes
        self.snackBar = ft.SnackBar(
            content=ft.Text("", color=ft.Colors.YELLOW),
            duration=5000,
            show_close_icon=True,
            close_icon_color=ft.Colors.RED
        )
        self.page.overlay.append(self.snackBar)
        
        self.crear_interfaz()

    def obtener_conexion_segura(self):
        """Crear una nueva conexión MySQL con configuración segura"""
        try:
            # Usar la misma configuración que tu conectarbd.py
            conexion = mysql.connector.connect(
                host='localhost',  # Ajusta según tu configuración
                database='tu_base_datos',  # Ajusta según tu configuración
                user='tu_usuario',  # Ajusta según tu configuración
                password='tu_password',  # Ajusta según tu configuración
                buffered=True,
                autocommit=True,
                charset='utf8mb4',
                use_unicode=True
            )
            return conexion
        except Exception as e:
            print(f"❌ Error creando conexión: {e}")
            return None

    def build(self):
        return self.content

    def crear_interfaz(self):
        # *** CONFIGURAR DATEPICKER ***
        self.date_picker = ft.DatePicker(
            on_change=self.actualizar_fecha,
            first_date=datetime(datetime.now().year - 5, datetime.now().month, 1),
            last_date=datetime.now()
        )
        if self.date_picker not in self.page.overlay:
            self.page.overlay.append(self.date_picker)

        # *** BOTONES DE FECHA ***
        self.desde_button = crear_boton_moderno(
            texto="Desde", 
            icono=ft.Icons.DATE_RANGE, 
            on_click=lambda e: self.pedir_fecha(0),
            color_fondo=COLORES_MODERNOS["azul_primario"],
            ancho=120,
            alto=40
        )
        
        self.hasta_button = crear_boton_moderno(
            texto="Hasta", 
            icono=ft.Icons.DATE_RANGE, 
            on_click=lambda e: self.pedir_fecha(1),
            color_fondo=COLORES_MODERNOS["azul_primario"],
            ancho=120,
            alto=40
        )

        # *** DROPDOWNS ***
        self.cbo_centros = crear_dropdown_moderno(
            label="Centro",
            options_data=[(str(id), centro) for id, centro in ejecutar_sql("SELECT id, centro FROM centros ORDER BY centro")],
            on_change=lambda e: self.cargar_jaulas(e.control.value),
            prefix_icon=ft.Icons.LOCATION_CITY,
            visible=True,
            height=self.altura_combos,
        )
        self.cbo_centro_limpiar = ft.Container(
            content=ft.Icon(ft.Icons.CLEANING_SERVICES, color=self.color_boton_limpiar, size=24),
            on_click=lambda _: self.limpiar("centro"),
            tooltip="Limpiar centro",
            ink=True,
            border_radius=ft.border_radius.all(8),
        )

        self.cbo_jaulas = crear_dropdown_moderno(
            label="Jaula:",
            options_data=[],
            height=self.altura_combos,
            width=100,
            visible=False,
            prefix_icon=ft.Icons.CELL_TOWER,
        )
        self.cbo_jaula_limpiar = ft.Container(
            content=ft.Icon(ft.Icons.CLEANING_SERVICES, color=self.color_boton_limpiar, size=24),
            on_click=lambda _: self.limpiar("jaula"),
            tooltip="Limpiar jaula",
            ink=False,
            visible=False,
            border_radius=ft.border_radius.all(8),
        )

        self.cbo_empresas = crear_dropdown_moderno(
            label="Empresa",
            options_data=[(str(id), nombre) for id, nombre in ejecutar_sql("SELECT id, nombre FROM empresas ORDER BY nombre")],
            height=self.altura_combos,
            prefix_icon=ft.Icons.BUSINESS,
        )
        self.cbo_empresa_limpiar = ft.Container(
            content=ft.Icon(ft.Icons.CLEANING_SERVICES, color=self.color_boton_limpiar, size=24),
            on_click=lambda _: self.limpiar("empresa"),
            tooltip="Limpiar empresa",
            ink=True,
            border_radius=ft.border_radius.all(8),
        )

        self.cbo_operadores = crear_dropdown_moderno(
            label="Operador",
            options_data=[
                (str(id), operador)
                for id, operador in ejecutar_sql(
                    "SELECT distinct sol.idoperador, trim(concat(us.nombre, ' ', us.apellido)) as usuario FROM solicitudes sol LEFT JOIN usuarios us on sol.idoperador = us.id where sol.idoperador > 0 ORDER BY usuario"
                )
            ],
            height=self.altura_combos,
            prefix_icon=ft.Icons.VERIFIED_USER,
        )
        self.cbo_operador_limpiar = ft.Container(
            content=ft.Icon(ft.Icons.CLEANING_SERVICES, color=self.color_boton_limpiar, size=24),
            on_click=lambda _: self.limpiar("operador"),
            tooltip="Limpiar operador",
            ink=True,
            border_radius=ft.border_radius.all(8),
        )

        self.cbo_anomalias = crear_dropdown_moderno(
            label="Anomalías",
            options_data=[
                (str(id), nombre)
                for id, nombre, color in ejecutar_sql("SELECT id, nombre, color FROM anomalias ORDER BY nombre")
            ],
            height=self.altura_combos,
            prefix_icon=ft.Icons.ERROR_OUTLINE,
        )
        self.cbo_anomalia_limpiar = ft.Container(
            content=ft.Icon(ft.Icons.CLEANING_SERVICES, color=self.color_boton_limpiar, size=24),
            on_click=lambda _: self.limpiar("anomalia"),
            tooltip="Limpiar anomalía",
            ink=True,
            border_radius=ft.border_radius.all(8),
        )

        self.cbo_sectores = crear_dropdown_moderno(
            label="Sectores",
            options_data=[(str(id), nombre) for id, nombre in ejecutar_sql("SELECT id, nombre FROM sector ORDER BY nombre")],
            height=self.altura_combos,
            prefix_icon=ft.Icons.PLACE,
        )
        self.cbo_sector_limpiar = ft.Container(
            content=ft.Icon(ft.Icons.CLEANING_SERVICES, color=self.color_boton_limpiar, size=24),
            on_click=lambda _: self.limpiar("sector"),
            tooltip="Limpiar sector",
            ink=True,
            border_radius=ft.border_radius.all(8),
        )

        self.cbo_estados = crear_dropdown_moderno(
            label="Estados",
            options_data=[(str(id), nombre) for id, nombre in ejecutar_sql("SELECT id, nombre FROM estado ORDER BY nombre")],
            height=self.altura_combos,
            prefix_icon=ft.Icons.SIGNAL_WIFI_STATUSBAR_4_BAR,
        )
        self.cbo_estado_limpiar = ft.Container(
            content=ft.Icon(ft.Icons.CLEANING_SERVICES, color=self.color_boton_limpiar, size=24),
            on_click=lambda _: self.limpiar("estado"),
            tooltip="Limpiar estado",
            ink=True,
            border_radius=ft.border_radius.all(8),
        )

        # *** BOTONES DE ACCIÓN ***
        self.btn_consultar = crear_boton_moderno(
            texto="Consultar", icono=ft.Icons.SEARCH, on_click=self.mostrar_tabla,
            tooltip="Consultar datos",
            color_fondo=COLORES_MODERNOS["verde_hover"],
        )
        self.limpiar_button = ft.Container(
            content=ft.Icon(ft.Icons.CLEANING_SERVICES, color=self.color_boton_limpiar, size=24),
            on_click=lambda _: self.limpiar(""),
            tooltip="Limpiar TODO",
            ink=True,
            border_radius=ft.border_radius.all(8),
        )

        # *** LAYOUT DE FILTROS ***
        self.filtros_row = ft.Column(
            controls=[
                ft.Row([
                    crear_texto_moderno("Fechas:", COLORES_MODERNOS["texto_principal"]), 
                    self.desde_button, 
                    self.hasta_button, 
                    self.limpiar_button
                ]),
                ft.Row([
                    self.cbo_centros, self.cbo_centro_limpiar,
                    self.cbo_jaulas, self.cbo_jaula_limpiar,
                    self.cbo_empresas, self.cbo_empresa_limpiar,
                    self.cbo_operadores, self.cbo_operador_limpiar
                ]),
                ft.Row([
                    self.cbo_anomalias, self.cbo_anomalia_limpiar,
                    self.cbo_sectores, self.cbo_sector_limpiar,
                    self.cbo_estados, self.cbo_estado_limpiar,
                    self.btn_consultar
                ])
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )

        # *** TABLA ***
        self.tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Jaula", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Anomalía", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Sector", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Cantidad", color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, colores["primario"]),
            border_radius=8,
            vertical_lines=ft.border.BorderSide(1, colores["primario_claro"]),
            horizontal_lines=ft.border.BorderSide(1, colores["primario_claro"]),
        )

        self.grafico_container = crear_contenedor_moderno(
            content=crear_texto_moderno("Gráfico", size=16, color=colores["texto_oscuro"]),
            expand=True
        )

        self.tabla_container = crear_contenedor_moderno(
            content=self.tabla,
            width="40%",
            padding=10,
            alignment=ft.alignment.top_left,
        )

        self.contenido = crear_contenedor_moderno(
            content=ft.Row([
                ft.Column([self.tabla_container, self.total_tabla]),
                self.grafico_container,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START
            ),
            expand=True,
            visible=False,
        )

        # *** CONTENIDO PRINCIPAL ***
        self.content = ft.Column(
            controls=[
                self.filtros_row,
                ft.Divider(height=1, color=colores["secundario"]),
                self.mensaje_consulta,
                self.contenido,
            ],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return self.content

    def cargar_jaulas(self, idcentro):
        if idcentro:
            sql = f"SELECT DISTINCT jaula FROM jaulas WHERE idsolicitud in(SELECT id FROM solicitudes WHERE idcentro = {idcentro})"
            jaulas = ejecutar_sql(sql)
            self.cbo_jaulas.options = [ft.dropdown.Option(text=str(jaula), key=str(jaula)) for (jaula,) in jaulas]
            self.cbo_jaulas.visible = True
            self.cbo_jaulas.update()
            self.cbo_jaula_limpiar.visible = True
            self.cbo_jaula_limpiar.update()

    def limpiar(self, component=None):
        if not component:
            # Limpiar todos los dropdowns
            self.cbo_centros.value = None
            self.cbo_centros.update()
            self.cbo_empresas.value = None
            self.cbo_empresas.update()
            self.cbo_operadores.value = None
            self.cbo_operadores.update()
            self.cbo_anomalias.value = None
            self.cbo_anomalias.update()
            self.cbo_sectores.value = None
            self.cbo_sectores.update()
            self.cbo_estados.value = None
            self.cbo_estados.update()
            
            # Limpiar fechas
            if hasattr(self.desde_button, 'content') and hasattr(self.desde_button.content, 'controls'):
                self.desde_button.content.controls[1].value = "Desde"
                self.hasta_button.content.controls[1].value = "Hasta"
                self.desde_button.update()
                self.hasta_button.update()
            
            self.desde_date = None
            self.hasta_date = None
            self.tabla.rows = []
            self.tabla.update()
            self.grafico_container.content = crear_texto_moderno("Gráfico", size=16, color=colores["texto_oscuro"])
            self.contenido.visible = False
            
        elif component == "centro":
            self.cbo_centros.value = None
            self.cbo_centros.update()
            self.cbo_jaulas.value = None
            self.cbo_jaulas.visible = False
            self.cbo_jaulas.update()
            self.cbo_jaula_limpiar.visible = False
            self.cbo_jaula_limpiar.update()
        elif component == "empresa":
            self.cbo_empresas.value = None
            self.cbo_empresas.update()
        elif component == "operador":
            self.cbo_operadores.value = None
            self.cbo_operadores.update()
        elif component == "anomalia":
            self.cbo_anomalias.value = None
            self.cbo_anomalias.update()
        elif component == "sector":
            self.cbo_sectores.value = None
            self.cbo_sectores.update()
        elif component == "estado":
            self.cbo_estados.value = None
            self.cbo_estados.update()
        elif component == "jaula":
            self.cbo_jaulas.value = None
            self.cbo_jaulas.update()

        self.page.update()

    def actualizar_fecha(self, e):
        fecha = e.control.value
        fecha_formateada = datetime.strftime(fecha, "%d/%m/%Y")
        
        if self.desde_hasta == 0:
            self.desde_date = fecha
            if hasattr(self.desde_button, 'content') and hasattr(self.desde_button.content, 'controls'):
                self.desde_button.content.controls[1].value = fecha_formateada
                self.desde_button.update()
        else:
            self.hasta_date = fecha
            if hasattr(self.hasta_button, 'content') and hasattr(self.hasta_button.content, 'controls'):
                self.hasta_button.content.controls[1].value = fecha_formateada
                self.hasta_button.update()

    def pedir_fecha(self, desde_hasta):
        print(f"Solicitando fecha para {'Desde' if desde_hasta == 0 else 'Hasta'}") 
        self.desde_hasta = desde_hasta
        self.date_picker.open = True
        self.page.update()

    def color_arreglado(self, color):
        if isinstance(color, str):
            if color.startswith('#') and len(color) == 7:
                return color
        return colores["acento"]

    def limpiar_conexion_bd(self):
        """Método para limpiar posibles conexiones colgadas"""
        try:
            # Ejecutar una consulta simple para verificar la conexión
            test_result = ejecutar_sql("SELECT 1")
            print("✅ Conexión BD verificada")
            return True
        except Exception as e:
            print(f"❌ Error verificando conexión: {e}")
            return False

    # Ejemplo de uso
    def consultar_datos(self):
        desde = self.desde_date.strftime("%Y-%m-%d") if self.desde_date else None
        hasta = self.hasta_date.strftime("%Y-%m-%d") if self.hasta_date else None
        centro = self.cbo_centros.value if self.cbo_centros.value else 0
        empresa = self.cbo_empresas.value if self.cbo_empresas.value else 0
        operador = self.cbo_operadores.value if self.cbo_operadores.value else 0
        anomalia = self.cbo_anomalias.value if self.cbo_anomalias.value else 0
        sector = self.cbo_sectores.value if self.cbo_sectores.value else 0
        estado = self.cbo_estados.value if self.cbo_estados.value else 0
        jaula = self.cbo_jaulas.value if self.cbo_jaulas.value else 0

        sql_solicitudes = "SELECT id FROM solicitudes"
        filtros = []
        where = ""
        if desde:
            where = " WHERE "
            filtros.append(f"fecha >= '{desde}'")
        if hasta:
            where = " WHERE "
            filtros.append(f"fecha <= '{hasta}'")
        if centro:
            where = " WHERE "
            filtros.append(f"idcentro = {centro}")
        if operador:
            where = " WHERE "
            filtros.append(f"idoperador = {operador}")
        if empresa:
            where = " WHERE "
            filtros.append(f"idempresa = {empresa}")
        sql_solicitudes += where
        sql_solicitudes += " AND ".join(filtros)

        bTodos_Solicitud = where == ""
        solicitudes = ejecutar_sql(sql_solicitudes)
        if solicitudes:
            id_solicitudes = tuple(x[0] for x in solicitudes)
            if len(id_solicitudes) == 1:
                ids_str = str(id_solicitudes[0])
            else:
                ids_str = ", ".join(map(str, id_solicitudes))
        else:
            ids_str = None

        pasos_str = None
        filtros_pasos = []
        where = ""
        sql_pasos = "SELECT id FROM pasos "
        if anomalia:
            where = " WHERE "
            filtros_pasos.append(f"idanomalia = {anomalia}")
        if sector:
            where = " WHERE "
            filtros_pasos.append(f"idsector = {sector}")
        if estado:
            where = " WHERE "
            filtros_pasos.append(f"idestado = {estado}")
        if jaula:
            where = " WHERE "
            filtros_pasos.append(f"jaula = {jaula}")
        sql_pasos += where
        sql_pasos += " AND ".join(filtros_pasos)

        bTodos_Pasos = where == ""
        pasos_condicion = ejecutar_sql(sql_pasos)
        NoHayRegistros = False
        if pasos_condicion:
            NoHayRegistros = False
            pasos_condicion = tuple(x[0] for x in pasos_condicion)
            if len(pasos_condicion) == 1:
                pasos_str = str(pasos_condicion[0])
            else:
                pasos_str = ", ".join(map(str, pasos_condicion))
        else:
            NoHayRegistros = True
            pasos_str = None

        sql = "SELECT id FROM pasos "
        where = ""
        where_pasos = []
        if not bTodos_Solicitud:
            where = " WHERE "
            if ids_str is None:
                where_pasos.append(f"pasos.idsolicitud = -1 ")
            else:
                where_pasos.append(f"pasos.idsolicitud in({ids_str}) ")
        if not bTodos_Pasos:
            where = " WHERE "
            if pasos_str is None:
                where_pasos.append("pasos.id = -1 ")
            else:
                where_pasos.append(f"pasos.id in({pasos_str}) ")
        sql += where
        sql += " AND ".join(where_pasos)

        sql = (
            "SELECT jaulas.jaula, anomalias.nombre as anomalia, anomalias.color, sector.nombre as sector, "
            "estado.nombre as estado, count(*) as cantidad "
            "FROM pasos "
            "LEFT JOIN jaulas on pasos.idjaula = jaulas.id "
            "LEFT JOIN anomalias ON pasos.idanomalia = anomalias.id "
            "LEFT JOIN sector on pasos.idsector = sector.id "
            "LEFT JOIN estado ON pasos.idestado = estado.id "
        )
        if where_pasos:
            sql += " WHERE "
            sql += " AND ".join(where_pasos)
        order_by = "GROUP BY pasos.idjaula, pasos.idanomalia, pasos.idsector, pasos.idestado "
        order_by += "ORDER BY jaulas.jaula ASC, anomalias.nombre ASC, sector.nombre ASC, estado.nombre ASC"
        sql += order_by

        resultado = ejecutar_sql(sql)
        if not resultado:
            self.mensaje_consulta.value = "No se encontraron registros"
            self.mensaje_consulta.visible = True
            self.contenido.visible = False
            self.page.update()
            return
        else:
            self.mensaje_consulta.visible = False

        # ← CAMBIO 8: Corregir la actualización de la tabla
        self.tabla.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row[0]), color=COLORES_MODERNOS["texto_principal"])),
                ft.DataCell(ft.Text(str(row[1]), color=self.color_arreglado(row[2]))),
                ft.DataCell(ft.Text(str(row[3]), color=COLORES_MODERNOS["texto_principal"])),
                ft.DataCell(ft.Text(str(row[4]), color=COLORES_MODERNOS["texto_principal"])),
                ft.DataCell(ft.Text(str(row[5]), color=COLORES_MODERNOS["texto_principal"])),
            ]) for row in resultado
        ]
        self.tabla.update()

        total_tabla = sum(row[5] for row in resultado)
        self.total_tabla.value = f"Total: {total_tabla}"

        sql_anomalias = (
            "SELECT anomalias.nombre AS anomalia, anomalias.color, COUNT(*) AS cantidad "
            "FROM pasos "
            "LEFT JOIN anomalias ON pasos.idanomalia = anomalias.id "
        )
        if where_pasos:
            sql_anomalias += " WHERE "
            sql_anomalias += " AND ".join(where_pasos)
        order_by = " GROUP BY anomalias.nombre, anomalias.color ORDER BY cantidad DESC"
        sql_anomalias += order_by
        grupos = ejecutar_sql(sql_anomalias)

        self.mostrar_grafico(grupos)
        self.contenido.visible = True
        self.contenido.update()
        self.page.update()

    def mostrar_tabla(self, e=None):
        print("🔘 Botón Consultar presionado")
        self.consultar_datos()

    def mostrar_grafico(self, datos):
        if not datos:
            # Mostrar mensaje cuando no hay datos
            self.grafico_container.content = ft.Text(
                "No hay datos para mostrar el gráfico",
                size=16,
                color=COLORES_MODERNOS["texto_secundario"]
            )
            self.grafico_container.update()
            return

        normal_radius = 50
        hover_radius = 60
        normal_title_style = ft.TextStyle(
            size=16, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD
        )
        hover_title_style = ft.TextStyle(
            size=22,
            color=ft.Colors.WHITE,
            weight=ft.FontWeight.BOLD,
            shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.BLACK54),
        )
        anomalia_elegida = crear_texto_moderno(
            "",
            size=16,
            color=COLORES_MODERNOS["texto_principal"],
            weight=ft.FontWeight.BOLD
        )

        def on_chart_event(e: ft.PieChartEvent):
            for idx, section in enumerate(chart.sections):
                if idx == e.section_index:
                    section.radius = hover_radius
                    section.title_style = hover_title_style
                    anomalia_elegida.value = f"Anomalía: {section.data} - {section.title}"
                    anomalia_elegida.update()
                else:
                    section.radius = normal_radius
                    section.title_style = normal_title_style
                    #anomalia_elegida.value = ""
                    anomalia_elegida.update()
            chart.update()

        try:
            # Procesar datos para el gráfico
            labels = [f"{row[0]}" for row in datos]
            cantidades = [row[2] for row in datos]
            colors = [self.color_arreglado(row[1]) for row in datos]
            total = sum(cantidades)

            # Configurar estilos
            normal_radius = 50
            hover_radius = 60
            normal_title_style = ft.TextStyle(
                size=12,
                color=COLORES_MODERNOS["texto_principal"],
                weight=ft.FontWeight.BOLD
            )

            # Crear gráfico de pie
            chart = ft.PieChart(
                sections=[
                    ft.PieChartSection(
                        cantidad,
                        title=f"{(cantidad/total)*100:.1f}%",
                        title_style=normal_title_style,
                        color=color,
                        radius=normal_radius,
                        data= f"{label} ({cantidad})"
                    )
                    for cantidad, color, label in zip(cantidades, colors, labels)
                ],
                sections_space=0,
                center_space_radius=40,
                expand=True,
                on_chart_event=on_chart_event,
            )

            # Crear leyenda
            leyenda = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Anomalía",color=COLORES_MODERNOS["texto_principal"])),
                    ft.DataColumn(ft.Text("Cantidad", color=COLORES_MODERNOS["texto_principal"])),
                    ft.DataColumn(ft.Text("Porcentaje", color=COLORES_MODERNOS["texto_principal"]))
                ],
                rows=[
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Container(
                            content=ft.Text(label),
                            bgcolor=color,
                            padding=5,
                            border_radius=5
                        )),
                        ft.DataCell(ft.Text(str(cantidad))),
                        ft.DataCell(ft.Text(f"{(cantidad/total)*100:.2f}%"))
                    ])
                    for label, color, cantidad in zip(labels, colors, cantidades)
                ],
                border=ft.border.all(1, colores["primario"]),
                border_radius=8,
                vertical_lines=ft.border.BorderSide(1, colores["primario_claro"]),
                horizontal_lines=ft.border.BorderSide(1, colores["primario_claro"])
            )

            # Construir contenido final
            contenido_grafico = ft.Column(
                controls=[
                    ft.Text("Distribución de Anomalías", size=18, weight=ft.FontWeight.BOLD),
                    ft.Column(
                        controls=[anomalia_elegida],),
                    ft.Row([chart, leyenda], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Text(f"Total: {total}", size=16, weight=ft.FontWeight.BOLD)
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )

            # Asignar contenido al contenedor
            self.grafico_container.content = contenido_grafico
            self.grafico_container.update()

        except Exception as e:
            print(f"Error al mostrar gráfico: {e}")
            self.grafico_container.content = ft.Text(
                f"Error al generar gráfico: {str(e)}",
                color=COLORES_MODERNOS["rojo_critico"]
            )
            self.grafico_container.update()

def main(page: ft.Page):
    EstadisticasView(page)

if __name__ == "__main__":
    import variables_globales
    ft.app(target=main, assets_dir=variables_globales.assets_dir, upload_dir=variables_globales.upload_dir)
