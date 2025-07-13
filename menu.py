import flet as ft
from estilos_modernos import (COLORES_MODERNOS, ESTILOS_COMPONENTES, crear_boton_moderno, crear_tarjeta_informe, crear_tarjeta_rov, crear_header_moderno, crear_navbar_moderno, aplicar_tema_moderno_a_pagina)
from datetime import datetime

class Menu(ft.Container):
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "InfoPilot"
        self.usuario_logueado = self.page.session.get("usuario_logueado")
        self.usuario_nombre = self.page.session.get("usuario_nombre")
        self.idgrupo = int(self.page.session.get("idgrupo"))
        self.ver_menu_datos = (self.idgrupo == 1)
        self.grupo_usuario = self.page.session.get("grupo")
        self.btn_cerrar_sesion = None
        self.menu_datos = ft.Container()
        
        # *** CONTENEDOR DE CONTENIDO PRINCIPAL ***
        self.contenido_principal = ft.Container(expand=True)
        
        # *** VARIABLE PARA EL TÍTULO ACTUAL ***
        self.titulo_actual = "Menú Principal"
        
        # --- INICIO DE CAMBIOS ---
        # 1. Inicializar DatePicker
        self.date_picker = ft.DatePicker(
            on_change=self.on_date_selected,
            #on_cancel=self.on_date_cancel,
            first_date=datetime(datetime.now().year - 5, datetime.now().month, 1), # Fecha de inicio del calendario
            last_date=datetime.now(), # Fecha de fin del calendario
        )
        # Añadir el DatePicker al overlay de la página
        self.page.overlay.append(self.date_picker)
        self.current_date_button = None # Para saber qué botón activó el DatePicker
        # --- FIN DE CAMBIOS ---

        self.setup_ui()
        
        # Crear el diálogo al inicio
        self.dlg = ft.AlertDialog(
            title=ft.Text("Título del diálogo"),
            content=ft.Text("Contenido del diálogo"),
            actions=[
                ft.TextButton("OK", on_click=self.close_dlg),
                ft.TextButton("Cancelar", on_click=self.close_dlg),
            ],
        )

    def setup_ui(self):
        # Aplicar tema moderno a la página
        aplicar_tema_moderno_a_pagina(self.page)
        
        def toggle_menu(menu):
            menu.visible = not menu.visible
            self.page.update()

        # Menús con estilo moderno
        self.menu_operaciones = ft.Container(
            content=ft.Column([
                self.crear_menu_item("Informes", "informe", ft.Icons.DESCRIPTION, self.idgrupo != 3),
                self.crear_menu_item("Estadísticas", "estadistica", ft.Icons.BAR_CHART, True),
                self.crear_menu_item("Modelo de Predicción", "prediccion", ft.Icons.PSYCHOLOGY, self.idgrupo != 3),
            ], spacing=5),
            **ESTILOS_COMPONENTES["card_container"],
            width=250,
            visible=False
        )

        self.menu_datos = ft.Container(
            content=ft.Column([
                self.crear_menu_item("Anomalías", "anomalia", ft.Icons.WARNING),
                self.crear_menu_item("Centros", "centro", ft.Icons.LOCATION_ON),
                self.crear_menu_item("Compañía", "compania", ft.Icons.BUSINESS),
                self.crear_menu_item("Empresas", "empresa", ft.Icons.CORPORATE_FARE),
                self.crear_menu_item("Estados", "estado", ft.Icons.FLAG),
                self.crear_menu_item("Sectores", "sector", ft.Icons.MAP),
            ], spacing=5),
            **ESTILOS_COMPONENTES["card_container"],
            width=250,
            visible=False
        )

        # Botones principales del menú con estilo moderno
        boton_operaciones = crear_boton_moderno(
            "Operaciones",
            color_fondo=COLORES_MODERNOS["azul_primario"],
            ancho=250,
            alto=50,
            icono=ft.Icons.SETTINGS,
            on_click=lambda _: toggle_menu(self.menu_operaciones)
        )

        boton_datos = crear_boton_moderno(
            "Datos",
            color_fondo=COLORES_MODERNOS["verde_exito"],
            ancho=250,
            alto=50,
            icono=ft.Icons.DATASET,
            on_click=lambda _: toggle_menu(self.menu_datos)
        )

        # Crear el menú principal (contenido inicial)
        self.menu_container = ft.Container(
            content=ft.Row([
                ft.Column([
                    boton_operaciones,
                    self.menu_operaciones
                ], spacing=10),
                ft.Container(width=50),
                ft.Column([
                    boton_datos,
                    self.menu_datos
                ], spacing=10, visible=self.ver_menu_datos)
            ], alignment=ft.MainAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            **ESTILOS_COMPONENTES["main_container"]
        )

        # *** CREAR EL HEADER UNA SOLA VEZ ***
        self.header_moderno = crear_header_moderno(
            usuario_nombre=self.usuario_nombre,
            usuario_rol=self.grupo_usuario,
            titulo_pagina=self.titulo_actual,  # ← Usar la variable del título
            on_logout=self.cerrar_sesion,
            on_home=self.ir_a_menu_principal
        )

        # *** ESTABLECER EL CONTENIDO INICIAL ***
        self.contenido_principal.content = self.menu_container

        # *** LAYOUT PRINCIPAL CON HEADER FIJO ***
        self.content = ft.Column([
            self.header_moderno,  # Header fijo que nunca cambia
            ft.Container(height=20),  # Espaciado
            self.contenido_principal,  # Contenido que cambia según la vista
        ], spacing=0, expand=True)

        # *** IMPORTANTE: NO asignar nada a page.appbar ***
        self.page.appbar = None

        return self.content

    def actualizar_titulo_header(self, nuevo_titulo):
        """Actualiza el título en el header y recrea el header"""
        self.titulo_actual = nuevo_titulo
        
        # Recrear el header con el nuevo título
        self.header_moderno = crear_header_moderno(
            usuario_nombre=self.usuario_nombre,
            usuario_rol=self.grupo_usuario,
            titulo_pagina=nuevo_titulo,  # ← Pasar el nuevo título
            on_logout=self.cerrar_sesion,
            on_home=self.ir_a_menu_principal
        )

    def crear_wrapper_con_header(self, contenido_vista):
        """Crea un wrapper que siempre mantiene el header visible"""
        return ft.Column([
            self.header_moderno,  # Header siempre visible
            ft.Container(height=20),  # Espaciado
            ft.Container(
                content=contenido_vista,  # La vista específica
                expand=True,
                padding=ft.padding.all(20),
                bgcolor=COLORES_MODERNOS["fondo_principal"]
            )
        ], spacing=0, expand=True)

    def crear_vista_temporal(self, nombre_vista, mensaje_adicional=""):
        """Crea una vista temporal mientras se arreglan las páginas individuales"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    f"Vista: {nombre_vista}",
                    size=24,
                    color=COLORES_MODERNOS["texto_principal"],
                    weight=ft.FontWeight.BOLD
                ),
                ft.Container(height=20),
                ft.Text(
                    f"Esta vista está siendo cargada correctamente.",
                    size=16,
                    color=COLORES_MODERNOS["texto_secundario"]
                ),
                ft.Container(height=10),
                ft.Text(
                    mensaje_adicional,
                    size=14,
                    color=COLORES_MODERNOS["texto_muted"]
                ),
                ft.Container(height=30),
                crear_boton_moderno(
                    "Volver al Menú Principal",
                    color_fondo=COLORES_MODERNOS["azul_primario"],
                    ancho=200,
                    on_click=lambda _: self.ir_a_menu_principal()
                )
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )

    def cargar_vista_con_manejo_especial(self, nombre_vista, import_path, class_name):
        """Carga una vista con manejo especial para las clases Pantalla existentes"""
        try:
            print(f"Cargando vista {nombre_vista}...")
            
            # *** ACTUALIZAR EL TÍTULO ANTES DE CARGAR LA VISTA ***
            self.actualizar_titulo_header(nombre_vista)
            
            # Importar dinámicamente el módulo
            module = __import__(import_path, fromlist=[class_name])
            PantallaClass = getattr(module, class_name)
            
            # Crear una página temporal para la instancia
            temp_page = self.page 
            
            # Crear la instancia de la pantalla
            instancia_pantalla = PantallaClass(temp_page)
            
            # Intentar extraer el contenido de diferentes maneras
            if hasattr(instancia_pantalla, 'tabs') and instancia_pantalla.tabs:
                # Para páginas como informes.py que usan tabs
                contenido = instancia_pantalla.tabs
            elif hasattr(instancia_pantalla, 'tabla_container') and instancia_pantalla.tabla_container:
                # Para páginas que tienen tabla_container
                contenido = ft.Column([
                    instancia_pantalla.titulo if hasattr(instancia_pantalla, 'titulo') else ft.Text(nombre_vista),
                    instancia_pantalla.boton_agregar if hasattr(instancia_pantalla, 'boton_agregar') else ft.Container(),
                    instancia_pantalla.tabla_container
                ], spacing=10)
            else:
                # Fallback: crear vista temporal
                contenido = self.crear_vista_temporal(
                    nombre_vista, 
                    f"La vista {nombre_vista} se cargó pero no se pudo extraer su contenido automáticamente."
                )
            
            # Limpiar la página y mostrar con header
            self.page.clean()
            self.page.add(self.crear_wrapper_con_header(contenido))
            self.page.update()
            print(f"Vista {nombre_vista} cargada exitosamente")
            
        except Exception as e:
            print(f"Error cargando {nombre_vista}: {e}")
            import traceback
            traceback.print_exc()
            
            # Mostrar vista de error
            error_content = ft.Container(
                content=ft.Column([
                    ft.Text(f"Error cargando {nombre_vista}", size=20, color=COLORES_MODERNOS["rojo_critico"], weight=ft.FontWeight.BOLD),
                    ft.Text(f"Detalles: {str(e)}", size=14, color=COLORES_MODERNOS["texto_secundario"]),
                    ft.Container(height=20),
                    crear_boton_moderno(
                        "Volver al Menú",
                        color_fondo=COLORES_MODERNOS["azul_primario"],
                        on_click=lambda _: self.ir_a_menu_principal()
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True
            )
            
            self.page.clean()
            self.page.add(self.crear_wrapper_con_header(error_content))
            self.page.update()

    def ir_a_menu_principal(self, e=None):
        """Función específica para el botón INICIO - regresa al menú principal"""
        print("Botón INICIO presionado - Regresando al menú principal")
        
        # *** ACTUALIZAR EL TÍTULO AL VOLVER AL MENÚ ***
        self.actualizar_titulo_header("Menú Principal")
        
        # Limpiar la página y mostrar solo el menú con header
        self.page.clean()
        self.page.add(ft.Column([
            self.header_moderno,
            ft.Container(height=20),
            self.menu_container,
        ], spacing=0, expand=True))
        
        # Ocultar menús desplegables si están abiertos
        self.menu_operaciones.visible = False
        self.menu_datos.visible = False
        self.page.update()

    def crear_menu_item(self, texto, vista, icono, visible=True):
        """Crea un elemento de menú con estilo moderno"""
        if not visible:
            return ft.Container(visible=False)
            
        return ft.Container(
            content=ft.Row([
                ft.Icon(icono, size=18, color=COLORES_MODERNOS["texto_principal"]),
                ft.Text(
                    texto, 
                    size=14, 
                    color=COLORES_MODERNOS["texto_principal"],
                    weight=ft.FontWeight.W_500
                ),
            ], spacing=10),
            padding=ft.padding.symmetric(horizontal=15, vertical=12),
            border_radius=8,
            bgcolor=ft.Colors.TRANSPARENT,
            on_click=lambda _, v=vista: self.cambiar_vista(v),
            ink=True,
            on_hover=self.on_menu_hover,
        )

    def on_menu_hover(self, e):
        """Efecto hover para elementos del menú"""
        if e.data == "true":
            e.control.bgcolor = ft.Colors.with_opacity(0.1, COLORES_MODERNOS["azul_primario"])
        else:
            e.control.bgcolor = ft.Colors.TRANSPARENT
        e.control.update()

    def cerrar_sesion(self, e):
        # Limpiamos la sesión y el usuario logueado
        self.page.session.set("usuario_logueado", "")
        self.page.session.set("idusuario", "")
        self.usuario_logueado = ""
        print("Sesión cerrada")

        # Reiniciamos la aplicación llamando a main
        from __main__ import main
        self.page.clean()
        main(self.page)
        self.page.update()

    def cambiar_vista(self, vista: str):
        """Cambia la vista pero SIEMPRE mantiene el header visible"""
        print(f"Cambiando a vista: {vista}")
        
        if vista == "main":
            self.ir_a_menu_principal()
        elif vista == "anomalia":
            self.vista_Anomalias()
        elif vista == "centro":
            self.vista_Centros()
        elif vista == "compania":
            self.vista_Compania()
        elif vista == "empresa":
            self.vista_Empresas()
        elif vista == "estado":
            self.vista_Estados()
        elif vista == "sector":
            self.vista_Sectores()
        elif vista == "informe":
            self.vista_Informes()
        elif vista == "estadistica":
            self.vista_Estadistica()
        elif vista == "prediccion":
            self.vista_Prediccion()

    def vista_Main(self, bCerrarSesion=False):
        """Vuelve al menú principal"""
        if bCerrarSesion:
            self.page.session.set("usuario_logueado", "")
            print("Cerrando sesión ", self.usuario_logueado)
        else:
            self.ir_a_menu_principal()

    # *** MÉTODOS VISTA CON TÍTULOS DINÁMICOS ***
    def vista_Anomalias(self):
        self.cargar_vista_con_manejo_especial("Anomalías", "paginas.anomalias", "Pantalla")
    
    def vista_Centros(self):
        self.cargar_vista_con_manejo_especial("Centros", "paginas.centros", "Pantalla")
    
    def vista_Compania(self):
        self.cargar_vista_con_manejo_especial("Compañía", "paginas.compania", "Pantalla")

    def vista_Empresas(self):
        self.cargar_vista_con_manejo_especial("Empresas", "paginas.empresas", "Pantalla")

    def vista_Estados(self):
        self.cargar_vista_con_manejo_especial("Estados", "paginas.estados", "Pantalla")

    def vista_Sectores(self):
        self.cargar_vista_con_manejo_especial("Sectores", "paginas.sectores", "Pantalla")
    
    def vista_Informes(self):
        self.cargar_vista_con_manejo_especial("Informes", "paginas.informes", "Pantalla")
    
    def vista_Estadistica(self):
        """*** MÉTODO ESPECÍFICO PARA ESTADÍSTICAS - CORREGIDO ***"""
        try:
            print("Cargando vista Estadísticas...")
            
            # Actualizar el título
            self.actualizar_titulo_header("Estadística")
            
            # Importar la clase EstadisticasView
            from paginas.estadistica import EstadisticasView
            
            # --- INICIO DE CAMBIOS ---
            # Pasar el DatePicker y una función para abrirlo a EstadisticasView
            # Se pasa la instancia de la página, la función para abrir el DatePicker
            # y la instancia del DatePicker mismo.
            estadisticas_view = EstadisticasView(
                self.page, 
                self.open_date_picker, 
                self.date_picker
            )
            # --- FIN DE CAMBIOS ---
            
            # *** OBTENER EL CONTENIDO CONSTRUIDO ***
            contenido_estadisticas = estadisticas_view.build()
            
            # Limpiar la página principal y mostrar el contenido
            self.page.clean()
            self.page.add(self.crear_wrapper_con_header(contenido_estadisticas))
            self.page.update()
            
            print("Vista Estadísticas cargada exitosamente con todos los controles")
            
        except Exception as e:
            print(f"Error cargando Estadísticas: {e}")
            import traceback
            traceback.print_exc()
            
            # Mostrar vista de error
            error_content = ft.Container(
                content=ft.Column([
                    ft.Text("Error cargando Estadísticas", size=20, color=COLORES_MODERNOS["rojo_critico"], weight=ft.FontWeight.BOLD),
                    ft.Text(f"Detalles: {str(e)}", size=14, color=COLORES_MODERNOS["texto_secundario"]),
                    ft.Container(height=20),
                    crear_boton_moderno(
                        "Volver al Menú",
                        color_fondo=COLORES_MODERNOS["azul_primario"],
                        on_click=lambda _: self.ir_a_menu_principal()
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True
            )
            
            self.page.clean()
            self.page.add(self.crear_wrapper_con_header(error_content))
            self.page.update()

    def close_dlg(self, e):
        self.dlg.open = False
        self.page.update()
        
    def vista_Prediccion(self):
        # Para el diálogo, mantener el comportamiento actual
        if self.dlg not in self.page.overlay:
            self.page.overlay.append(self.dlg)
        self.dlg.open = True
        self.page.update()

    # --- INICIO DE NUEVAS FUNCIONES PARA EL DATEPICKER ---
    def open_date_picker(self, e, target_button):
        """
        Abre el DatePicker y guarda una referencia al botón que lo activó.
        `target_button` es el botón que necesita actualizar su texto.
        """
        self.current_date_button = target_button
        self.date_picker.open = True
        self.page.update()

    def on_date_selected(self, e):
        """
        Maneja la selección de una fecha en el DatePicker.
        Actualiza el texto del botón que activó el DatePicker.
        """
        if self.date_picker.value and self.current_date_button:
            selected_date = self.date_picker.value.strftime("%d/%m/%Y")
            # Asumiendo que el texto del botón es el segundo control en el Row
            # (el primero es el icono, si existe)
            self.current_date_button.content.controls[1].value = selected_date 
            self.current_date_button.update() # Actualiza solo el botón
        self.date_picker.open = False
        self.page.update() # Actualiza la página para cerrar el DatePicker

    def on_date_cancel(self, e):
        """Maneja la cancelación del DatePicker."""
        self.date_picker.open = False
        self.page.update()
    # --- FIN DE NUEVAS FUNCIONES PARA EL DATEPICKER ---
