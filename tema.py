# tema.py - Módulo de tema centralizado para la aplicación

# Paleta de colores Aiko
COLORES = {
    "primario": "#2ba5b2",       # Turquesa
    "secundario": "#023e55",     # Azul oscuro
    "terciario": "#3b4e73",      # Azul-púrpura
    "acento": "#f7af02",         # Amarillo/dorado
    
    # Variantes y colores adicionales
    "primario_claro": "#3ec8d7",
    "primario_oscuro": "#1d7a84",
    "secundario_claro": "#0a5b7c",
    "secundario_oscuro": "#012a3a",
    "terciario_claro": "#4e6496",
    "terciario_oscuro": "#2a3854",
    "acento_claro": "#ffc235",
    "acento_oscuro": "#d99500",
    
    # Colores para texto
    "texto_claro": "#ffffff",
    "texto_oscuro": "#333333",
    "texto_desactivado": "#888888",
    
    # Colores de fondo
    "fondo_claro": "#f5f5f5",
    "fondo_oscuro": "#1a1a1a",
    "fondo_gradiente_inicio": "#2ba5b2",
    "fondo_gradiente_fin": "#023e55",
    
    # Colores de estado
    "error": "#e53935",
    "exito": "#43a047",
    "advertencia": "#f7af02",
    "info": "#2196f3",
}

# Estilos comunes para componentes
ESTILOS = {
    # Botones
    "boton_primario": {
        "bgcolor": COLORES["acento"],
        "color": COLORES["texto_claro"],
        "hover_color": COLORES["acento_claro"],
    },
    "boton_secundario": {
        "bgcolor": COLORES["secundario"],
        "color": COLORES["texto_claro"],
        "hover_color": COLORES["secundario_claro"],
    },
    
    # Contenedores
    "contenedor_principal": {
        "bgcolor": COLORES["fondo_claro"],
        "border_radius": 10,
        "padding": 10,
    },
    "contenedor_tarjeta": {
        "bgcolor": COLORES["texto_claro"],
        "border_radius": 10,
        "padding": 5,
        "shadow": "0px 4px 8px rgba(0, 0, 0, 0.1)",
    },
    
    # Textos
    "titulo": {
        "size": 24,
        "weight": "bold",
        "color": COLORES["secundario"],
    },
    "subtitulo": {
        "size": 18,
        "weight": "w500",
        "color": COLORES["terciario"],
    },
    
    # Gradientes
    "gradiente_principal": {
        "begin": {"x": 0, "y": 0},
        "end": {"x": 1, "y": 1},
        "colors": [COLORES["fondo_gradiente_inicio"], COLORES["fondo_gradiente_fin"]],
    },
    
    # Menús
    "menu_cabecera": {
        "bgcolor": COLORES["secundario"],
        "color": COLORES["texto_claro"],
        "padding": 5,
        "border_radius": 8,
    },
    "menu_item": {
        "bgcolor": COLORES["texto_claro"],
        "color": COLORES["secundario"],
        "hover_color": COLORES["primario"],
    },
}

# Función para aplicar estilos a componentes
def aplicar_estilo(componente, estilo):
    """
    Aplica un estilo predefinido a un componente Flet
    
    Args:
        componente: El componente Flet al que aplicar el estilo
        estilo: Diccionario con los atributos de estilo a aplicar
    
    Returns:
        El componente con los estilos aplicados
    """
    for attr, value in estilo.items():
        if hasattr(componente, attr):
            setattr(componente, attr, value)
    return componente

# Función para crear un gradiente lineal
def crear_gradiente_lineal(begin=None, end=None, colors=None):
    """
    Crea un objeto de gradiente lineal para usar en contenedores
    
    Args:
        begin: Punto de inicio del gradiente (dict con x, y)
        end: Punto final del gradiente (dict con x, y)
        colors: Lista de colores para el gradiente
    
    Returns:
        Un objeto LinearGradient de Flet
    """
    import flet as ft
    
    if begin is None:
        begin = ESTILOS["gradiente_principal"]["begin"]
    if end is None:
        end = ESTILOS["gradiente_principal"]["end"]
    if colors is None:
        colors = ESTILOS["gradiente_principal"]["colors"]
    
    return ft.LinearGradient(
        begin=ft.alignment.Alignment(begin["x"], begin["y"]),
        end=ft.alignment.Alignment(end["x"], end["y"]),
        colors=colors,
    )