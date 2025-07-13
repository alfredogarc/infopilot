import flet as ft
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.rl_config import defaultPageSize
from reportlab.platypus.doctemplate import BaseDocTemplate, PageTemplate
from reportlab.platypus.frames import Frame
from reportlab.pdfgen import canvas
from reportlab.pdfgen import canvas as cv
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
from conectarbd import ejecutar_sql
import os
import base64
from io import BytesIO
from math import ceil
from PIL import Image as PILImage  # Importar Pillow para redimensionar imágenes
from variables_globales import upload_dir
from PyPDF2 import PdfReader, PdfWriter
import tempfile

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.porcentaje_reduccion_imagenes = 0.1

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Numera las páginas solo después de que se han eliminado las páginas vacías"""
        num_pages = len(self._saved_page_states)
        for i, state in enumerate(self._saved_page_states):
            self.__dict__.update(state)
            self.draw_page_number(i + 1, num_pages)
            self.draw_borders()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_num, total_pages):
        self.setFont("Helvetica", 9)
        self.drawRightString(defaultPageSize[0] - 40, 40,
            f"Página {page_num} de {total_pages}")
    
    def draw_borders(self):
        self.setStrokeColor(colors.black)
        self.setLineWidth(1)
        margin = 30
        page_width = self._pagesize[0]
        page_height = self._pagesize[1]
        self.line(margin, margin, margin, page_height - margin)
        self.line(page_width - margin, margin, page_width - margin, page_height - margin)
        self.line(margin, margin, page_width - margin, margin)
        self.line(margin, page_height - margin, page_width - margin, page_height - margin)

    def draw_horizontal_line(self):
        self.setStrokeColor(colors.black)
        self.setLineWidth(1)
        margin = 30
        self.line(margin, 
                 defaultPageSize[1] - 100, 
                 defaultPageSize[0] - margin, 
                 defaultPageSize[1] - 100)

class Imprimir_Informe_Redes(BaseDocTemplate):
    def __init__(self, filename, id, **kw):
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kw)
        template = PageTemplate('normal', [Frame(self.leftMargin, self.bottomMargin,
                                                self.width, self.height, id='normal')])
        self.addPageTemplates(template)
        self.story = []
        self.styles = getSampleStyleSheet()
        
        self.idsolicitud = id
        self.solicitud = ejecutar_sql(f"SELECT id, fecha, empresa, centro, sector, usuario, encargado, tipo_informe, hora_inicio, hora_fin, duracion, urgente, faena_realizada, realizo_trabajos, asunto, emails, cuerpo, archivo1, archivo_nombre1, archivo2, archivo_nombre2, archivo3, archivo_nombre3, archivo4, archivo_nombre4, jaulas, jaula_desde FROM view_solicitudes WHERE view_solicitudes.id = {self.idsolicitud}")
        self.compania = ejecutar_sql("SELECT nombre, nombrecorto, logo, rut, direccion, telefono, paginaweb, email, contacto, correos_google_drive, telegram_token, telegram_chatid FROM compania")
        self.pasos = ejecutar_sql(f"SELECT pasos.idjaula, pasos.izq, pasos.numero, pasos.pos_y, pasos.pos_x, pasos.color, pasos.descripcion, anomalias.nombre AS anomalia, estado.nombre AS estado, sector.nombre AS sector, pasos.imagen FROM pasos LEFT JOIN anomalias ON pasos.idanomalia = anomalias.id LEFT JOIN estado ON pasos.idestado = estado.id LEFT JOIN sector ON pasos.idsector = sector.id LEFT JOIN jaulas ON pasos.idjaula = jaulas.id WHERE pasos.idsolicitud = {self.idsolicitud} ORDER BY jaulas.jaula ASC, pasos.izq DESC, pasos.numero ASC")
        self.jaulas = ejecutar_sql(f"SELECT id, jaula, jaula_imagen_izq, jaula_imagen_der FROM jaulas WHERE idsolicitud = {self.idsolicitud} ORDER BY jaula ASC")
        #sql = f"SELECT j.id, j.jaula, COALESCE(j.jaula_imagen_izq, c.jaula_izq) as jaula_imagen_izq,COALESCE(j.jaula_imagen_der, c.jaula_der) as jaula_imagen_der FROM jaulas j LEFT JOIN solicitudes s ON s.id = j.idsolicitud LEFT JOIN centros c ON s.idcentro = c.id WHERE j.idsolicitud = {self.idsolicitud} ORDER BY j.jaula ASC"
        #print(sql)
        #self.jaulas = ejecutar_sql(sql)
        self.colores = ejecutar_sql("SELECT DISTINCT color FROM anomalias")
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            alignment=1,
            fontSize=12,
            spaceAfter=0
        )

    def crear_encabezado(self):
        fecha_solicitud = self.solicitud[0][1].strftime('%d/%m/%Y')
        fecha_actual = datetime.now().strftime('%d/%m/%Y')
        hora_actual = datetime.now().strftime('%I:%M:%S %p')
        
        image_data = base64.b64decode(self.compania[0][2])
        image_stream = BytesIO(image_data)
        
        header_data = [
            [
                Image(image_stream, width=150, height=60),
                Table(
                    [
                        ['Fecha:', fecha_solicitud],
                        ['Fecha Imp.:', fecha_actual],
                        ['Hora Imp.:', hora_actual],
                    ],
                    colWidths=[80, 100],
                    style=TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ])
                )
            ],
            [
                Table(
                    [
                        [self.compania[0][0]],
                        [f"RUT: {self.compania[0][3]}"],
                        [f'Teléfono: {self.compania[0][5]} / Email: {self.compania[0][7]}']
                    ],
                    style=TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (0, 0), 12),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ])
                ),
                ''
            ]
        ]

        header_table = Table(header_data, colWidths=[350, 200])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(header_table)
        self.story.append(Spacer(1, 1))

    def Datos_Solicitud(self):
        encabezado_datos = [
            ['Centro:', self.solicitud[0][3]], ['Piloto ROV:', self.solicitud[0][5]],
            ['Empresa:', self.solicitud[0][2], 'Asistente ROV:', ""],
            ['Jefe de Centro o Asistente:', self.solicitud[0][6], 'Equipo ROV:', ""],
            ['Condición de Puerto:', "", 'Serie ROV:', ""],
        ]
        encabezado = Table(encabezado_datos, colWidths=["30%", "20%", "30%", "20%"])
        encabezado.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ]))
        self.story.append(encabezado)
        self.story.append(Spacer(1, 20))

       
    def Fanea_Realizada(self):
        self.story.append(Paragraph("FAENAS REALIZADAS:", self.title_style))
        self.story.append(Spacer(1, 12))
        
        # Verificar si hay texto de faena
        faena_text = self.solicitud[0][12] if self.solicitud[0][12] else "Sin faenas registradas"
        
        # Crear el párrafo con el texto
        faena_paragraph = Paragraph(
            faena_text, 
            ParagraphStyle('Justified', parent=self.styles['Normal'], alignment=TA_JUSTIFY)
        )
        
        # Crear la tabla con el párrafo
        faena_table = Table([[faena_paragraph]], colWidths=[450])
        faena_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        self.story.append(faena_table)
        self.story.append(Spacer(1, 20))

    def colores_anomalias(self):
        self.story.append(Paragraph("Colores de Anomalías:", self.title_style))
        self.story.append(Spacer(1, 12))

        color_data = self.colores
        color_rectangles = []

        for color in color_data:
            color_rectangles.append(
            Table(
                [[Paragraph("", ParagraphStyle('Normal', backColor=color[0]))]],
                colWidths=50,
                rowHeights=50,
                style=TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, -1), color[0]), 
                ])
            )
            )

        color_table = Table([color_rectangles], colWidths=[60] * len(color_rectangles))
        color_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))

        self.story.append(color_table)
        self.story.append(Spacer(1, 20))

    def crear_tabla_jaulas(self):
        jaulas_data = self.jaulas
        
        jaulas_impares = []
        jaulas_pares = []
        
        for jaula in jaulas_data:
            if int(jaula[1]) % 2 == 0:
                jaulas_pares.append(jaula[1])
            else:
                jaulas_impares.append(jaula[1])
        
        max_length = max(len(jaulas_impares), len(jaulas_pares))
        jaulas_impares.extend([''] * (max_length - len(jaulas_impares)))
        jaulas_pares.extend([''] * (max_length - len(jaulas_pares)))
        
        link_style = ParagraphStyle(
            'LinkStyle',
            parent=self.styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            textColor=colors.whitesmoke
        )

        table_data = [
            [Paragraph(f'<link href="jaula_{num}"><font color="white">{num}</font></link>', link_style) if num else '' for num in jaulas_impares],
            [Paragraph(f'<link href="jaula_{num}"><font color="white">{num}</font></link>', link_style) if num else '' for num in jaulas_pares]
        ]
        
        col_width = 50
        colWidths = [col_width] * max_length
        
        jaulas_table = Table(table_data, colWidths=colWidths)
 
        styles = [
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]
        for row in range(2):
            for col in range(max_length):
                if table_data[row][col] != '':
                    styles.extend([
                        ('BACKGROUND', (col, row), (col, row), colors.green),
                        ('TEXTCOLOR', (col, row), (col, row), colors.whitesmoke),
                        ('BOX', (col, row), (col, row), 1, colors.black),
                    ])
        
        jaulas_table.setStyle(TableStyle(styles))
        return jaulas_table

    def crear_contenido(self):
        self.Datos_Solicitud()
        self.Fanea_Realizada()

        self.story.append(Paragraph(
            "ESQUEMA MÓDULOS, UBICACIÓN DE EVENTOS Y AVANCE:",
            self.title_style
        ))
        
        self.story.append(Paragraph("Extracción de Mortalidad", self.title_style))
        self.story.append(Spacer(1, 12))

        jaulas_table = self.crear_tabla_jaulas()
        self.story.append(jaulas_table)
        self.story.append(Spacer(1, 24))

        self.colores_anomalias()
        self.imprimir_jaulas_imagenes()

        self.story.append(PageBreak())

    def mostrar_marcas_der(self):
        # Obtener el siguiente número para este marcador
        sql = f"""SELECT p.id, p.pos_x, p.pos_y, p.numero, p.descripcion, p.color, 
                 a.nombre as anomalia, e.nombre as estado, s.nombre as sector 
                 FROM pasos p
                 LEFT JOIN anomalias a ON p.idanomalia = a.id 
                 LEFT JOIN estado e ON p.idestado = e.id 
                 LEFT JOIN sector s ON p.idsector = s.id 
                 WHERE p.idsolicitud = {self.nIDSolicitud} 
                 AND p.idjaula = {self.jaula_seleccionada_id} 
                 AND p.izq = {0}"""
        pasos = ejecutar_sql(sql)

        self.markers_container_der.controls.clear()
        for paso in pasos:
            # Dibujar el marcador en la imagen
            self.pintura_relleno_der = ft.Paint(
                style=ft.PaintingStyle.FILL, 
                color=paso[5]
            )
            self.jaula_der.agregar_forma(
                cv.Circle(paso[1], paso[2], 10, paint=self.pintura_relleno_der),
                paso[3]  # Pasar el número del marcador
            )

            # Crear el botón del marcador
            btn_posicion_der = ft.ElevatedButton(
                text=str(paso[3]),
                bgcolor=paso[5],
                color=ft.Colors.WHITE,
                width=50,
                height=50,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                ),
                data={
                    'numero': paso[3],
                    'color': paso[5],
                    'x': paso[1],
                    'y': paso[2]
                },
                disabled=True
            )

            tamano_letras_der = 12
            color_letras_der = ft.Colors.BLACK
            anomalia_seleccionada_der = ft.Text(f"A: {paso[6]}", size=tamano_letras_der, color=color_letras_der)
            estado_seleccionado_der = ft.Text(f"E: {paso[7]}", size=tamano_letras_der, color=color_letras_der)
            sector_seleccionado_der = ft.Text(f"S: {paso[8]}", size=tamano_letras_der, color=color_letras_der)
            detalles_paso_der = ft.Column(
                [anomalia_seleccionada_der, sector_seleccionado_der, estado_seleccionado_der], 
                alignment=ft.MainAxisAlignment.START, 
                spacing=2,
            )

            # Crear el campo de comentario
            comment_field_der = ft.TextField(
                value=paso[4],
                hint_text="Introduzca una observación",
                hint_style=ft.TextStyle(color=ft.Colors.GREY_400),
                width=400,
                border_color=ft.Colors.GREY_400,
                multiline=True,
                on_blur=self.save_comment,
                data=paso[0],
                focused_border_color=paso[5]
            )

        self.markers_container_der.update()
        self.jaula_der.update()
        self.page.update()

    def process_image_top(self, image_data, width, height):
        """Procesa y redimensiona la imagen para la vista superior/lateral de la jaula"""
        if image_data:
            try:
                # Decodificar la imagen base64
                image_bytes = base64.b64decode(image_data)
                
                # Crear la imagen directamente sin procesamiento para mantener calidad original
                output = BytesIO(image_bytes)
                img = Image(output)
                
                # Ajustar dimensiones manteniendo proporción
                aspect_ratio = img._width / img._height
                if width/height > aspect_ratio:
                    new_height = height
                    new_width = height * aspect_ratio
                else:
                    new_width = width
                    new_height = width / aspect_ratio
                
                # Establecer dimensiones finales
                img._width = new_width
                img._height = new_height
                
                return img
                
            except Exception as e:
                print(f"Error procesando imagen superior: {str(e)}")
                return None
        return None

    def process_image(self, image_data, scale_factor=0.2):
        """
        Procesa una imagen base64 y retorna un objeto Image de ReportLab
        Args:
            image_data: Imagen en formato base64
            scale_factor: Factor de escala para redimensionar la imagen (0.2 = 20%)
        """
        try:
            # Decodificar la imagen base64
            imagen_data = base64.b64decode(image_data)
            img_stream = BytesIO(imagen_data)
            
            # Abrir la imagen con PIL
            image = PILImage.open(img_stream)
            
            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Calcular el tamaño objetivo manteniendo el aspect ratio
            target_size = 150  # Tamaño objetivo para el lado más largo
            aspect_ratio = image.width / image.height
            
            if aspect_ratio > 1:  # Imagen más ancha que alta
                new_width = target_size
                new_height = int(target_size / aspect_ratio)
            else:  # Imagen más alta que ancha
                new_height = target_size
                new_width = int(target_size * aspect_ratio)
            
            # Redimensionar la imagen usando un algoritmo de alta calidad
            image = image.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
            
            # Comprimir y guardar la imagen con mejor calidad
            output = BytesIO()
            image.save(output, 
                      format='JPEG', 
                      quality=100,  # Máxima calidad
                      optimize=True,
                      subsampling=0  # Mejor calidad de color
            )
            output.seek(0)
            
            # Crear imagen ReportLab con tamaño específico
            img = Image(output)
            img._width = new_width
            img._height = new_height
            
            return img
            
        except Exception as e:
            print(f"Error procesando imagen: {e}")
            return None

    def create_top_images(self, lJaula):
        # Adjust image size
        img_width = 3.2 * inch
        img_height = 3.2 * inch
        lateral_height = 2.2 * inch

        def crear_imagen_lado(imagen_data, lado, texto_lateral):
            if imagen_data:
                img = self.process_image_top(imagen_data, img_width, img_height)
                if img:
                    # Create vertical text
                    vertical_style = ParagraphStyle('Vertical', parent=self.styles['Normal'], 
                                                  alignment=TA_CENTER, textColor=colors.black, fontSize=5)
                    vertical_text = Table([[Paragraph(texto_lateral, vertical_style)]], 
                                        colWidths=0.25*inch, rowHeights=lateral_height)
                    vertical_text.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ]))

                    # Create main table
                    if lado == "IZQUIERDO":
                        data = [[vertical_text, img]]
                        table = Table(data, colWidths=[0.25*inch, img_width])
                    else:
                        data = [[img, vertical_text]]
                        table = Table(data, colWidths=[img_width, 0.25*inch])

                    table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))

                    # Add jaula title
                    self.titulo_propio = ParagraphStyle('CustomTitle', 
                                                      parent=getSampleStyleSheet()['Heading1'], 
                                                      fontSize=10, alignment=1)
                    title = Table([[
                        Paragraph(f"LADO {lado}", self.titulo_propio),
                    ]], colWidths=[img_width])
                    
                    return title, table
            return None, None

        # Verificar si hay pasos para esta jaula
        pasos_izq = [paso for paso in self.pasos if paso[0] == lJaula[0] and paso[1] == 1]
        pasos_der = [paso for paso in self.pasos if paso[0] == lJaula[0] and paso[1] == 0]

        # Procesar lado izquierdo solo si hay pasos
        if pasos_izq and lJaula[2]:
            title, table = crear_imagen_lado(lJaula[2], "IZQUIERDO", "LATERAL WEST")
            if title and table:
                self.story.append(PageBreak())
                self.crear_encabezado()
                self.story.append(Paragraph("INFORME INSPECCIÓN DE REDES RED LOBERA Y PECERAS", self.title_style))
                self.story.append(Spacer(1, 2))
                self.story.append(Paragraph("ESQUEMA LOBERO: 30x30"))
                self.story.append(Spacer(1, 2))
                self.story.append(title)
                self.story.append(table)
                self.story.append(Spacer(1, 5))
                self.mostrar_pasos_grid(lJaula[0], True)

        # Procesar lado derecho solo si hay pasos
        if pasos_der and lJaula[3]:
            title, table = crear_imagen_lado(lJaula[3], "DERECHO", "LATERAL ESTE")
            if title and table:
                self.story.append(PageBreak())
                self.crear_encabezado()
                self.story.append(Paragraph("INFORME INSPECCIÓN DE REDES RED LOBERA Y PECERAS", self.title_style))
                self.story.append(Spacer(1, 2))
                self.story.append(Paragraph("ESQUEMA LOBERO: 30x30"))
                self.story.append(Spacer(1, 2))
                self.story.append(title)
                self.story.append(table)
                self.story.append(Spacer(1, 5))
                self.mostrar_pasos_grid(lJaula[0], False)

    def imprimir_jaulas_imagenes(self):
        for jaula_registro in self.jaulas:
            jaula_id = jaula_registro[0]
            # Verificar si hay pasos para esta jaula
            pasos_jaula = [paso for paso in self.pasos if paso[0] == jaula_id]
            if pasos_jaula:  # Solo procesar si hay pasos
                self.story.append(PageBreak())
                self.crear_encabezado()
                self.story.append(Paragraph("INFORME INSPECCIÓN DE REDES RED LOBERA Y PECERAS", self.title_style))
                self.story.append(Spacer(1, 2))
                self.story.append(Paragraph("ESQUEMA LOBERO: 30x30"))
                self.story.append(Spacer(1, 2))
                self.create_top_images(jaula_registro)
    
    def mostrar_pasos_grid(self, jaula_id, lado_izquierdo):
        # Configuración de estilos
        styles = getSampleStyleSheet()
        style_cell = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontSize=9,
            alignment=0,
            textColor=colors.black
        )
        
        # Obtener información de la jaula
        jaula_info = ejecutar_sql(f"SELECT jaula FROM jaulas WHERE id = {jaula_id}")
        if not jaula_info:
            return

        jaula_numero = jaula_info[0][0]
        
        # Obtener detalles de la jaula solo para el lado especificado
        pasos_jaula = [paso for paso in self.pasos if paso[0] == jaula_id and paso[1] == (1 if lado_izquierdo else 0)]

        if not pasos_jaula:
            return

        table_data = []
        current_row = []
        
        for paso in pasos_jaula:
            try:
                # Crear una celda de tabla con tamaño fijo
                cell_width = 150
                cell_height = 150
                
                # Procesar imagen con resolución reducida
                if paso[10]:
                    imagen = self.process_image(paso[10], scale_factor=0.2)
                    if not imagen:
                        imagen = Table([['']], colWidths=[cell_width], rowHeights=[cell_height])
                        imagen.setStyle(TableStyle([
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ]))
                    else:
                        # Centrar la imagen en la celda
                        padding_h = (cell_width - imagen._width) / 2
                        padding_v = (cell_height - imagen._height) / 2
                        imagen_table = Table([[imagen]], 
                                          colWidths=[cell_width],
                                          rowHeights=[cell_height])
                        imagen_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                        imagen = imagen_table
                else:
                    imagen = Table([['']], colWidths=[cell_width], rowHeights=[cell_height])
                    imagen.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))

                # Crear el estilo para el número de paso
                paso_style = ParagraphStyle(
                    'PasoStyle',
                    parent=style_cell,
                    backColor=colors.lightblue if lado_izquierdo else colors.white,
                    alignment=1
                )

                # Crear los elementos de texto
                paso_numero = Paragraph(f"<b>Paso {paso[2]}</b>", paso_style)
                descripcion = paso[6] if paso[6] else ""
                anomalia = paso[7] if paso[7] else ""
                estado = paso[8] if paso[8] else ""
                sector = paso[9] if paso[9] else ""

                detalles = Paragraph(f"""
{descripcion}<br/><br/>
<b>Anomalía:</b> {anomalia}<br/>
<b>Estado:</b> {estado}<br/>
<b>Sector:</b> {sector}
""", style_cell)

                cell_content = [
                    [imagen],
                    [paso_numero],
                    [detalles]
                ]
                
                current_row.append(cell_content)
                
                if len(current_row) == 3 or paso == pasos_jaula[-1]:
                    while len(current_row) < 3:
                        empty_image = Table([['']], colWidths=[150], rowHeights=[150])
                        empty_image.setStyle(TableStyle([
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        current_row.append([[empty_image], [Paragraph("", style_cell)]])
                    table_data.append(current_row)
                    current_row = []

            except Exception as e:
                print(f"Error procesando paso {paso[2]}: {str(e)}")
                error_image = Table([['']], colWidths=[150], rowHeights=[150])
                error_image.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                error_content = [
                    [error_image],
                    [Paragraph(f"Error en Paso {paso[2]}", style_cell)]
                ]
                current_row.append(error_content)
                
                if len(current_row) == 3 or paso == pasos_jaula[-1]:
                    while len(current_row) < 3:
                        empty_image = Table([['']], colWidths=[150], rowHeights=[150])
                        empty_image.setStyle(TableStyle([
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        current_row.append([[empty_image], [Paragraph("", style_cell)]])
                    table_data.append(current_row)
                    current_row = []

        if current_row:
            while len(current_row) < 3:
                empty_image = Table([['']], colWidths=[150], rowHeights=[150])
                empty_image.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                current_row.append([[empty_image], [Paragraph("", style_cell)]])
            table_data.append(current_row)

        if not table_data:
            return
        
        # Crear la tabla
        col_width = 2.5 * inch
        table = Table(table_data, colWidths=[col_width, col_width, col_width])
        
        # Estilos de la tabla
        table_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ])

        # Aplicar colores de fondo según el paso
        for i, row in enumerate(table_data):
            for j, cell in enumerate(row):
                idx = i * 3 + j
                if idx < len(pasos_jaula):
                    paso = pasos_jaula[idx]
                    if paso[5]:  # Color del estado
                        table_style.add('BACKGROUND', (j, i), (j, i), paso[5])
        
        table.setStyle(table_style)
        self.story.append(table)
        self.story.append(Spacer(1, 20))

    def generar_reporte(self):
        try:
            # Crear un archivo temporal para el PDF inicial
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            
            # Generar el reporte inicial en el archivo temporal
            doc_temp = SimpleDocTemplate(
                temp_file.name,
                pagesize=self.pagesize,
                rightMargin=self.rightMargin,
                leftMargin=self.leftMargin,
                topMargin=self.topMargin,
                bottomMargin=self.bottomMargin
            )
            
            # Generar el contenido
            self.crear_encabezado()
            self.crear_contenido()
            
            if not self.story:
                print("No hay contenido para generar el reporte.")
                return None
            
            # Construir el PDF inicial
            doc_temp.build(self.story, canvasmaker=NumberedCanvas)
            
            # Leer el PDF temporal
            reader = PdfReader(temp_file.name)
            writer = PdfWriter()
            
            # Verificar cada página por contenido significativo
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                resources = page.get("/Resources", {})
                has_images = "/XObject" in resources
                
                print(f"\n--- Analizando página {page_num} ---")
                print(f"Longitud del texto: {len(text)}")
                print(f"Tiene imágenes: {has_images}")
                
                # Verificar si el texto contiene más que solo el encabezado
                texto_sin_encabezado = text
                
                # Palabras clave que indican contenido significativo
                contenido_keywords = [
                    "FAENAS REALIZADAS",
                    "LADO IZQUIERDO",
                    "LADO DERECHO",
                ]
                
                # Verificar contenido significativo
                tiene_contenido_significativo = False

                for keyword in contenido_keywords:
                    if keyword in texto_sin_encabezado:
                        tiene_contenido_significativo = True
                
                if tiene_contenido_significativo:
                    writer.add_page(page)
                    print(f"Página {page_num} AGREGADA al documento final")
                else:
                    print(f"Página {page_num} ELIMINADA por falta de contenido significativo")
                    print("Contenido de la página:")
                    print("-" * 50)
                    print(text[:500])  # Mostrar los primeros 500 caracteres
                    print("-" * 50)
            
            # Si no hay páginas válidas, retornar None
            if len(writer.pages) == 0:
                print("No se encontraron páginas con contenido válido")
                return None
            
            # Escribir el PDF final
            with open(self.filename, 'wb') as output_file:
                writer.write(output_file)
            
            # Leer el archivo final para retornarlo
            with open(self.filename, 'rb') as f:
                pdf_data = f.read()
            
            # Limpiar archivo temporal
            os.unlink(temp_file.name)
            
            print(f"\nReporte generado exitosamente con {len(writer.pages)} páginas válidas")
            return pdf_data
            
        except Exception as e:
            print(f"Error al generar el reporte: {str(e)}")
            return None
        finally:
            if hasattr(self, 'conn'):
                self.conn.close()

def main():
    archivo = "reporte_redes.pdf"
    reporte = Imprimir_Informe_Redes(archivo, 
                               id = 135, 
                               pagesize=letter,
                               rightMargin=30,
                               leftMargin=30,
                               topMargin=30,
                               bottomMargin=30)
    reporte.generar_reporte()
    print("Reporte PDF generado exitosamente.")

if __name__ == "__main__":
    main()