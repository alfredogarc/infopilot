import flet as ft

def crear_widget_imagen(page, verImagen, verRuta):
    image_path = ft.Text(visible=verRuta)
                         
    # Función para manejar la carga de la imagen
    def on_file_upload(e):
        if e.files:
            # Obtiene el primer archivo subido
            file = e.files[0]
            # Muestra la imagen en la pantalla usando la ruta del archivo
            image_view.src = file.path
            image_view.visible = verImagen
            image_path.value = f"Ruta de la imagen: {file.path}"
            page.update()

    # Componente para subir archivos
    file_picker = ft.FilePicker(on_result=on_file_upload)
    
    # Botón para abrir el selector de archivos
    upload_button = ft.ElevatedButton("Subir Foto", on_click=lambda e: file_picker.pick_files(), icon=ft.icons.PICTURE_IN_PICTURE)
    
    # Componente para mostrar la imagen
    image_view = ft.Image(visible=verImagen, width=300, height=300)

    # Contenedor con bordes redondeados
    image_container = ft.Container(
        content=image_view,
        padding=10,
        border_radius=20,  # Radio de los bordes redondeados
        bgcolor="lightgray",  # Color de fondo del contenedor
        alignment=ft.alignment.center
    )

    # Retornar un Row que contiene el botón y el contenedor de imagen
    return ft.Row([upload_button, file_picker, image_container, image_path])

#def main(page):
#    page.title = "Subir y Mostrar Foto"
    
#    # Crear el widget de imagen, pasando True para mostrar la imagen
#    widget_imagen = crear_widget_imagen(page, verImagen=True)
    
#    # Agregar el widget a la página
#    page.add(widget_imagen)

#ft.app(target=main)
