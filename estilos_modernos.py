import flet as ft

# Paleta de colores basada en la imagen del dashboard
COLORES_MODERNOS = {
    # Colores principales del tema oscuro
    "fondo_principal": "#0B1426",  # Azul muy oscuro del fondo
    "fondo_secundario": "#1A2332",  # Azul oscuro para tarjetas
    "fondo_terciario": "#243447",  # Azul medio para elementos elevados
    "fondo_header": "#1E3A5F",  # Azul del header
    "fondo_navbar": "#2C4B6B",  # Azul de la barra de navegación
    
    # Colores de acento y estados
    "azul_primario": "#3B82F6",  # Azul principal
    "azul_activo": "#1D4ED8",  # Azul para elementos activos
    "azul_hover": "#2563EB",  # Azul para hover
    "verde_exito": "#10B981",  # Verde para informes de redes
    "verde_hover": "#059669",  # Verde hover
    "rojo_critico": "#EF4444",  # Rojo para informes críticos
    "rojo_hover": "#DC2626",  # Rojo hover
    "rojo_cerrar": "#DC2626",  # Rojo para botón cerrar sesión
    "amarillo_advertencia": "#F59E0B",  # Amarillo para advertencias
    "morado_info": "#8B5CF6",  # Morado para información
    
    # Colores de texto
    "texto_principal": "#FFFFFF",
    "texto_secundario": "#94A3B8",
    "texto_muted": "#64748B",
    "texto_placeholder": "#475569",
    
    # Colores de estado
    "operativo": "#10B981",
    "mantenimiento": "#F59E0B",
    "critico": "#EF4444",
    "inactivo": "#6B7280",
    
    # Bordes y divisores
    "borde_sutil": "#334155",
    "borde_activo": "#3B82F6",
    "borde_hover": "#475569",
    
    # Gradientes
    "gradiente_inicio": "#1E3A8A",
    "gradiente_fin": "#1E40AF",
}

# Estilos para componentes específicos (SIN color para evitar conflictos)
ESTILOS_COMPONENTES = {
    "page_config": {
        "bgcolor": COLORES_MODERNOS["fondo_principal"],
        "theme_mode": ft.ThemeMode.DARK,
    },
    
    "header_container": {
        "bgcolor": COLORES_MODERNOS["fondo_header"],
        "padding": ft.padding.symmetric(horizontal=20, vertical=15),
        "border_radius": 0,
    },
    
    "navbar_container": {
        "bgcolor": COLORES_MODERNOS["fondo_navbar"],
        "padding": ft.padding.symmetric(horizontal=20, vertical=10),
        "border_radius": 0,
    },
    
    "main_container": {
        "bgcolor": COLORES_MODERNOS["fondo_principal"],
        "padding": ft.padding.all(20),
        "expand": True,
    },
    
    "card_container": {
        "bgcolor": COLORES_MODERNOS["fondo_secundario"],
        "border_radius": 12,
        "padding": ft.padding.all(20),
        "border": ft.border.all(1, COLORES_MODERNOS["borde_sutil"]),
    },
    
    "card_elevated": {
        "bgcolor": COLORES_MODERNOS["fondo_terciario"],
        "border_radius": 12,
        "padding": ft.padding.all(20),
        "border": ft.border.all(1, COLORES_MODERNOS["borde_activo"]),
    },
    
    "input_field": {
        "bgcolor": COLORES_MODERNOS["fondo_principal"],
        "border_color": COLORES_MODERNOS["borde_sutil"],
        "focused_border_color": COLORES_MODERNOS["azul_primario"],
        "cursor_color": COLORES_MODERNOS["azul_primario"],
        "border_radius": 12,
        "height": 55,
    },

    "input_memo": {
        "bgcolor": COLORES_MODERNOS["fondo_principal"],
        "border_color": COLORES_MODERNOS["borde_sutil"],
        "focused_border_color": COLORES_MODERNOS["azul_primario"],
        "cursor_color": COLORES_MODERNOS["azul_primario"],
        "border_radius": 12,
        "min_lines": 3,
        "max_lines": 6, 
        "multiline": True
    },
    
    # Estilos de texto SIN color para evitar conflictos
    "section_title": {
        "size": 24,
        "weight": ft.FontWeight.BOLD,
    },
    
    "card_title": {
        "size": 18,
        "weight": ft.FontWeight.BOLD,
    },
    
    "card_subtitle": {
        "size": 14,
    },
    
    "metric_number": {
        "size": 32,
        "weight": ft.FontWeight.BOLD,
    },
    
    "metric_label": {
        "size": 12,
        "weight": ft.FontWeight.W_500,
    },
    
    "menu_item": {
        "bgcolor": ft.Colors.TRANSPARENT,
        "border_radius": 8,
        "padding": ft.padding.symmetric(horizontal=15, vertical=10),
    },
    
    "menu_item_active": {
        "bgcolor": COLORES_MODERNOS["azul_primario"],
        "border_radius": 8,
        "padding": ft.padding.symmetric(horizontal=15, vertical=10),
    },
}

def crear_boton_moderno(texto = "", color_fondo = COLORES_MODERNOS["azul_primario"], color_texto=None, ancho=None, alto=40, on_click=None, icono=None, tooltip=None, visible=True, icon_color= None):
    """Crea un botón con el estilo moderno de la interfaz"""
    
    # Crear el contenido del botón
    if icono:
        contenido = ft.Row(
            controls=[
                ft.Icon(icono, size=16, color=color_texto or COLORES_MODERNOS["texto_principal"]),
                ft.Text(
                    texto, 
                    size=14, 
                    weight=ft.FontWeight.W_600,
                    color=color_texto or COLORES_MODERNOS["texto_principal"],
                    tooltip=tooltip,
                    visible=visible
                ),
            ],
            tight=True,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        )
    else:
        contenido = ft.Text(
            texto, 
            size=14, 
            weight=ft.FontWeight.W_600,
            color=color_texto or COLORES_MODERNOS["texto_principal"],
            visible=visible
        )
    
    return ft.ElevatedButton(
        content=contenido,
        bgcolor=color_fondo,
        color=color_texto or COLORES_MODERNOS["texto_principal"],
        width=ancho,
        height=alto,
        visible=visible,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            elevation=0,
            overlay_color=ft.Colors.with_opacity(0.1, COLORES_MODERNOS["texto_principal"]),
        ),
        on_click=on_click,
        tooltip = tooltip        
    )

def crear_campo_moderno(label, password=False, prefix_icon=None, width=320, on_submit=None, value="", keyboard_tipo = None, text_accion = None, on_cambio = None, estilo="input_field", tooltip = None):
    """Crea un campo de entrada con estilo moderno"""
    return ft.TextField(
        label=label,
        password=password,
        can_reveal_password=password,
        width=width,
        value=value,
        prefix_icon=prefix_icon,
        tooltip=tooltip,
        label_style=ft.TextStyle(
            color=COLORES_MODERNOS["texto_secundario"],
            weight=ft.FontWeight.W_500,
            size=14,
        ),
        text_style=ft.TextStyle(
            color=COLORES_MODERNOS["texto_principal"],
            size=14,
        ),
        on_submit=on_submit,
        **ESTILOS_COMPONENTES[estilo],
        keyboard_type=keyboard_tipo, 
        hint_text=text_accion,
        on_change=on_cambio
    )

def crear_tarjeta_informe(titulo, subtitulo, icono, numero_activos, numero_secundarios, 
                         label_secundarios, color_boton, color_numeros=None, on_click=None):
    """Crea una tarjeta de informe como las de la imagen"""
    
    # Contenedor del icono
    icono_container = ft.Container(
        content=ft.Icon(icono, size=24, color=COLORES_MODERNOS["azul_primario"]),
        width=40,
        height=40,
        bgcolor=ft.Colors.with_opacity(0.2, COLORES_MODERNOS["azul_primario"]),
        border_radius=8,
        alignment=ft.alignment.center,
    )
    
    # Métricas - CORREGIDO: aplicamos estilos sin conflicto de color
    metricas_row = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Text(
                        str(numero_activos), 
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=color_numeros or COLORES_MODERNOS["azul_primario"]
                    ),
                    ft.Text(
                        "ACTIVOS", 
                        size=12,
                        weight=ft.FontWeight.W_500,
                        color=COLORES_MODERNOS["texto_muted"]
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            ft.Container(width=40),  # Espaciador
            ft.Column(
                controls=[
                    ft.Text(
                        str(numero_secundarios), 
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=color_numeros or COLORES_MODERNOS["texto_secundario"]
                    ),
                    ft.Text(
                        label_secundarios.upper(), 
                        size=12,
                        weight=ft.FontWeight.W_500,
                        color=COLORES_MODERNOS["texto_muted"]
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
    )
    
    # Botón de acción
    boton_crear = crear_boton_moderno(
        "Crear Informes",
        color_fondo=color_boton,
        ancho=200,
        alto=45,
        on_click=on_click
    )
    
    return ft.Container(
        content=ft.Column(
            controls=[
                # Header de la tarjeta
                ft.Row(
                    controls=[
                        icono_container,
                        ft.Column(
                            controls=[
                                ft.Text(
                                    titulo, 
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLORES_MODERNOS["texto_principal"]
                                ),
                                ft.Text(
                                    subtitulo, 
                                    size=14,
                                    color=COLORES_MODERNOS["texto_secundario"]
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    spacing=15,
                ),
                ft.Container(height=20),  # Espaciador
                metricas_row,
                ft.Container(height=20),  # Espaciador
                boton_crear,
            ],
            spacing=0,
        ),
        **ESTILOS_COMPONENTES["card_container"],
        width=350,
        height=280,
    )

def crear_tarjeta_rov(nombre_team, centro, estado, piloto, color_estado, on_click=None):
    """Crea una tarjeta ROV como las de la imagen"""
    
    # Icono del ROV
    icono_rov = ft.Container(
        content=ft.Icon(ft.Icons.PRECISION_MANUFACTURING, size=24, color=COLORES_MODERNOS["texto_principal"]),
        width=40,
        height=40,
        bgcolor=ft.Colors.with_opacity(0.2, COLORES_MODERNOS["texto_principal"]),
        border_radius=8,
        alignment=ft.alignment.center,
    )
    
    # Badge de estado
    estado_badge = ft.Container(
        content=ft.Text(
            estado.upper(), 
            size=10, 
            weight=ft.FontWeight.BOLD,
            color=COLORES_MODERNOS["texto_principal"]
        ),
        bgcolor=color_estado,
        padding=ft.padding.symmetric(horizontal=8, vertical=4),
        border_radius=12,
    )
    
    tarjeta = ft.Container(
        content=ft.Column(
            controls=[
                # Header con icono y nombre
                ft.Row(
                    controls=[
                        icono_rov,
                        ft.Column(
                            controls=[
                                ft.Text(
                                    nombre_team, 
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLORES_MODERNOS["texto_principal"]
                                ),
                                ft.Text(
                                    centro, 
                                    color=COLORES_MODERNOS["azul_primario"], 
                                    size=14
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    spacing=15,
                ),
                ft.Container(height=15),
                # Información de estado y piloto
                ft.Row(
                    controls=[
                        ft.Text(
                            "Estado:", 
                            size=14,
                            color=COLORES_MODERNOS["texto_secundario"]
                        ),
                        estado_badge,
                    ],
                    spacing=10,
                ),
                ft.Container(height=8),
                ft.Row(
                    controls=[
                        ft.Text(
                            "Piloto:", 
                            size=14,
                            color=COLORES_MODERNOS["texto_secundario"]
                        ),
                        ft.Text(
                            piloto, 
                            color=COLORES_MODERNOS["texto_principal"], 
                            size=14, 
                            weight=ft.FontWeight.W_500
                        ),
                    ],
                    spacing=10,
                ),
            ],
            spacing=0,
        ),
        **ESTILOS_COMPONENTES["card_container"],
        width=350,
        height=180,
        on_click=on_click,
        ink=True if on_click else False,
    )
    
    return tarjeta

def crear_header_moderno(usuario_nombre, usuario_rol, titulo_pagina="Menú Principal", on_logout=None, on_home=None):
    """Crea el header moderno como en la imagen - MODIFICADO para título dinámico"""
    
    # Logo y título
    logo_section = ft.Row(
        controls=[
            ft.Container(
                content=ft.Icon(ft.Icons.HOME, size=20, color=COLORES_MODERNOS["texto_principal"]),
                bgcolor=ft.Colors.with_opacity(0.2, COLORES_MODERNOS["texto_principal"]),
                width=35,
                height=35,
                border_radius=8,
                alignment=ft.alignment.center,
                on_click=on_home,
                ink=True if on_home else False,
            ),
            ft.Text("INICIO", size=14, color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.W_500),
            ft.Container(width=20),
            ft.Text("InfoPilot", size=24, color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.BOLD),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.START,
    )
    
    # Sección de usuario
    user_section = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Text(usuario_nombre, size=14, color=COLORES_MODERNOS["texto_principal"], weight=ft.FontWeight.W_500),
                    ft.Text(f"[{usuario_rol}]", size=12, color=COLORES_MODERNOS["texto_secundario"]),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.END,
            ),
            crear_boton_moderno(
                "Cerrar sesión",
                color_fondo=COLORES_MODERNOS["rojo_cerrar"],
                ancho=140,
                icono=ft.Icons.LOGOUT,
                on_click=on_logout
            ),
        ],
        spacing=15,
        alignment=ft.MainAxisAlignment.END,
    )
    
    # *** CAMBIO PRINCIPAL: Título dinámico ***
    titulo = ft.Text(
        titulo_pagina,  # ← Usar el parámetro en lugar de "Título de la Página"
        size=24,
        color=COLORES_MODERNOS["texto_principal"],
        weight=ft.FontWeight.BOLD,
    )
    
    return ft.Container(
        content=ft.Row(
            controls=[logo_section, titulo, user_section],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        **ESTILOS_COMPONENTES["header_container"],
    )

def crear_navbar_moderno(tab_activa="Dashboard", on_tab_change=None):
    """Crea la barra de navegación moderna"""
    
    def crear_tab(texto, icono, key, activa=False):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icono, size=16, color=COLORES_MODERNOS["texto_principal"] if activa else COLORES_MODERNOS["texto_secundario"]),
                    ft.Text(
                        texto,
                        size=14,
                        weight=ft.FontWeight.W_600 if activa else ft.FontWeight.W_400,
                        color=COLORES_MODERNOS["texto_principal"] if activa else COLORES_MODERNOS["texto_secundario"],
                    ),
                ],
                spacing=8,
            ),
            bgcolor=COLORES_MODERNOS["azul_activo"] if activa else ft.Colors.TRANSPARENT,
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
            border_radius=8,
            on_click=lambda _: on_tab_change(key) if on_tab_change else None,
            ink=True if on_tab_change else False,
        )
    
    return ft.Container(
        content=ft.Row(
            controls=[
                crear_tab("Dashboard", ft.Icons.DASHBOARD, "Dashboard", tab_activa == "Dashboard"),
                crear_tab("Datos", ft.Icons.FOLDER, "Datos", tab_activa == "Datos"),
            ],
            spacing=10,
        ),
        **ESTILOS_COMPONENTES["navbar_container"],
    )

def aplicar_tema_moderno_a_pagina(page: ft.Page):
    """Aplica el tema moderno completo a la página"""
    page.bgcolor = COLORES_MODERNOS["fondo_principal"]
    page.theme_mode = ft.ThemeMode.DARK
    
    # Configurar tema personalizado
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=COLORES_MODERNOS["azul_primario"],
            on_primary=COLORES_MODERNOS["texto_principal"],
            surface=COLORES_MODERNOS["fondo_secundario"],
            on_surface=COLORES_MODERNOS["texto_principal"],
            background=COLORES_MODERNOS["fondo_principal"],
            on_background=COLORES_MODERNOS["texto_principal"],
        )
    )

def crear_menu_lateral_moderno(items_menu, item_activo=None, on_item_click=None):
    """Crea un menú lateral moderno"""
    menu_items = []
    
    for item in items_menu:
        es_activo = item.get("key") == item_activo
        
        menu_item = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        item.get("icono", ft.Icons.CIRCLE), 
                        size=20, 
                        color=COLORES_MODERNOS["texto_principal"] if es_activo else COLORES_MODERNOS["texto_secundario"]
                    ),
                    ft.Text(
                        item.get("texto", ""), 
                        size=14,
                        weight=ft.FontWeight.W_600 if es_activo else ft.FontWeight.W_400,
                        color=COLORES_MODERNOS["texto_principal"] if es_activo else COLORES_MODERNOS["texto_secundario"]
                    ),
                ],
                spacing=12,
            ),
            **ESTILOS_COMPONENTES["menu_item_active" if es_activo else "menu_item"],
            on_click=lambda _, key=item.get("key"): on_item_click(key) if on_item_click else None,
            ink=True if on_item_click else False,
        )
        
        menu_items.append(menu_item)
    
    return ft.Column(
        controls=menu_items,
        spacing=5,
    )

def crear_dropdown_moderno(label, options_data, value=None, prefix_icon=None, width=320, on_change=None, hint_text="Seleccionar opción", visible=True, height=55):
    """
    Crea un dropdown con estilo moderno consistente con los otros componentes
    
    Args:
        label (str): Etiqueta del dropdown
        options_data (list): Lista de tuplas (texto, valor) o lista de strings
        value: Valor seleccionado por defecto
        prefix_icon: Icono a mostrar al inicio (opcional)
        width (int): Ancho del dropdown
        on_change: Función callback para cambios
        hint_text (str): Texto de ayuda
    
    Returns:
        ft.Dropdown: Dropdown con estilo moderno
    """
    
    # Procesar las opciones - puede ser lista de tuplas (texto, valor) o lista de strings
    dropdown_options = []
    
    if options_data and len(options_data) > 0:
        # Si el primer elemento es una tupla, asumimos formato (texto, valor)
        if isinstance(options_data[0], (tuple, list)) and len(options_data[0]) >= 2:
            #dropdown_options = [ft.dropdown.Option(text=str(item[0]), key=str(item[1])) for item in options_data]
            dropdown_options = [ft.dropdown.Option(text=str(item[1]), key=str(item[0])) for item in options_data]
        else:
            # Si son strings simples, usar el mismo valor para texto y key
            dropdown_options = [ft.dropdown.Option(text=str(item), key=str(item)) for item in options_data]
    
    return ft.Dropdown(
        label=label,
        hint_text=hint_text,
        options=dropdown_options,
        value=value,
        width=width,
        on_change=on_change,
        
        # Estilos consistentes con crear_campo_moderno
        bgcolor=COLORES_MODERNOS["fondo_principal"],
        border_color=COLORES_MODERNOS["borde_sutil"],
        focused_border_color=COLORES_MODERNOS["azul_primario"],
        border_radius=12,
        height=55,
        
        # Estilos de texto
        label_style=ft.TextStyle(
            color=COLORES_MODERNOS["texto_secundario"],
            weight=ft.FontWeight.W_500,
            size=14,
        ),
        text_style=ft.TextStyle(
            color=COLORES_MODERNOS["texto_principal"],
            size=14,
        ),
        
        # Color del icono de dropdown
        focus_color=COLORES_MODERNOS["texto_secundario"],
        icon_enabled_color=COLORES_MODERNOS["azul_primario"],
        visible = visible,
        
        # Padding interno
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        
        # Estilo de las opciones
        options_fill_horizontally=True,
    )

# Función de conveniencia para crear dropdowns con datos de base de datos
def crear_dropdown_desde_query(label, query_result, text_field_index=1, value_field_index=0, 
                              include_none_option=True, none_text="Ninguno", **kwargs):
    """
    Crea un dropdown moderno a partir de resultados de consulta SQL
    
    Args:
        label (str): Etiqueta del dropdown
        query_result (list): Resultado de ejecutar_sql() - lista de tuplas
        text_field_index (int): Índice del campo que se mostrará como texto
        value_field_index (int): Índice del campo que se usará como valor
        include_none_option (bool): Si incluir opción "Ninguno"
        none_text (str): Texto para la opción "Ninguno"
        **kwargs: Argumentos adicionales para crear_dropdown_moderno
    
    Returns:
        ft.Dropdown: Dropdown con los datos de la consulta
    """
    
    options_data = []
    
    # Agregar opción "Ninguno" si se solicita
    if include_none_option:
        options_data.append((none_text, None))
    
    # Procesar resultados de la consulta
    if query_result:
        for row in query_result:
            if len(row) > max(text_field_index, value_field_index):
                text = str(row[text_field_index]) if row[text_field_index] is not None else ""
                value = row[value_field_index]
                options_data.append((text, value))
    
    return crear_dropdown_moderno(
        label=label,
        options_data=options_data,
        **kwargs
    )

def crear_contenedor_moderno(
    content=None,
    width=None,
    height=None,
    padding=None,
    margin=None,
    bgcolor=None,
    border_radius=None,
    border=None,
    alignment=None,
    expand=False,
    on_click=None,
    ink=False,
    visible=True,
    **kwargs
):
    """
    Crea un contenedor moderno reutilizable con el estilo visual estándar de la app.
    Permite sobreescribir propiedades clave si es necesario.
    """
    return ft.Container(
        content=content,
        width=width,
        height=height,
        padding=padding if padding is not None else ft.padding.all(20),
        margin=margin,
        bgcolor=bgcolor if bgcolor is not None else COLORES_MODERNOS["fondo_secundario"],
        border_radius=border_radius if border_radius is not None else 12,
        border=border if border is not None else ft.border.all(1, COLORES_MODERNOS["borde_sutil"]),
        alignment=alignment,
        expand=expand,
        on_click=on_click,
        ink=ink,
        visible=visible,
        **kwargs
    )

def crear_texto_moderno(
    texto: str,
    color=None,
    size=16,
    weight=ft.FontWeight.NORMAL,
    italic=False,
    align=ft.TextAlign.LEFT,
    max_lines=None,
    overflow=ft.TextOverflow.ELLIPSIS,
    selectable=False,
    **kwargs
):
    """
    Crea un ft.Text con estilos modernos y parámetros personalizables.
    """
    from estilos_modernos import COLORES_MODERNOS  # Asegura acceso a la paleta moderna
    color = color or COLORES_MODERNOS.get("texto_principal", "#222222")
    return ft.Text(
        texto,
        color=color,
        size=size,
        weight=weight,
        italic=italic,
        text_align=align,
        max_lines=max_lines,
        overflow=overflow,
        selectable=selectable,
        **kwargs
    )

def crear_tabla_moderna(
    columns,
    rows=None,
    width=None,
    height=None,
    bgcolor=None,
    border_radius=12,
    border_color=None,
    header_bgcolor=None,
    header_text_color=None,
    cell_text_color=None,
    cell_bgcolor=None,
    divider_color=None,
    show_border=True,
    on_row_tap=None,
    **kwargs
):
    """
    Crea una tabla (DataTable) con estilos modernos y consistentes.
    columns: lista de tuplas (titulo_columna, color_header) o solo strings.
    rows: lista de listas (cada fila).
    """
    import flet as ft

    # Colores por defecto
    bgcolor = bgcolor or COLORES_MODERNOS["fondo_secundario"]
    border_color = border_color or COLORES_MODERNOS["borde_sutil"]
    header_bgcolor = header_bgcolor or COLORES_MODERNOS["fondo_terciario"]
    header_text_color = header_text_color or COLORES_MODERNOS["texto_principal"]
    cell_text_color = cell_text_color or COLORES_MODERNOS["texto_principal"]
    cell_bgcolor = cell_bgcolor or COLORES_MODERNOS["fondo_secundario"]
    divider_color = divider_color or COLORES_MODERNOS["borde_sutil"]

    # Procesar columnas
    data_columns = []
    for col in columns:
        if isinstance(col, (tuple, list)):
            title, col_color = col[0], col[1] if len(col) > 1 else header_text_color
        else:
            title, col_color = str(col), header_text_color
        data_columns.append(
            ft.DataColumn(
                ft.Text(
                    title,
                    color=col_color,
                    size=15,
                    weight=ft.FontWeight.BOLD,
                ),
            )
        )

    # Procesar filas
    data_rows = []
    if rows:
        for row in rows:
            cells = []
            for cell in row:
                # Permitir celdas con color personalizado: (texto, color)
                if isinstance(cell, (tuple, list)) and len(cell) == 2:
                    cell_text, cell_color = cell
                else:
                    cell_text, cell_color = cell, cell_text_color
                cells.append(
                    ft.DataCell(
                        ft.Text(
                            str(cell_text),
                            color=cell_color,
                            size=14,
                        )
                    )
                )
            data_rows.append(ft.DataRow(cells=cells, on_select_changed=on_row_tap))

    return ft.Container(
        content=ft.DataTable(
            columns=data_columns,
            rows=data_rows,
            heading_row_color=header_bgcolor,
            data_row_color={"even": cell_bgcolor, "odd": ft.Colors.with_opacity(0.03, cell_bgcolor)},
            #divider_color=divider_color,
            border=ft.border.all(1, border_color) if show_border else None,
            border_radius=border_radius,
            horizontal_margin=12,
            column_spacing=18,
            show_checkbox_column=False,
            **kwargs
        ),
        bgcolor=bgcolor,
        border_radius=border_radius,
        border=ft.border.all(1, border_color) if show_border else None,
        width=width,
        height=height,
        padding=ft.padding.all(8),
    )