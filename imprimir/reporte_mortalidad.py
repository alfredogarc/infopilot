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
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from conectarbd import ejecutar_sql
import os
import base64
from io import BytesIO

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            self.draw_borders()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.drawRightString(defaultPageSize[0] - 40, 40,
                         f"Página {self._pageNumber} de {page_count}")
    
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

class Imprimir_Informe_Mortalidad(BaseDocTemplate):
    def __init__(self, filename, id, **kw):
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kw)
        template = PageTemplate('normal', [Frame(self.leftMargin, self.bottomMargin,
                                                self.width, self.height, id='normal')])
        self.addPageTemplates(template)
        self.story = []
        self.styles = getSampleStyleSheet()
        
        self.idsolicitud = id
        self.solicitud = ejecutar_sql(f"SELECT id, fecha, empresa, centro, sector, usuario, encargado, tipo_informe, hora_inicio, hora_fin, duracion, urgente, realizo_trabajos, asunto, emails, cuerpo, archivo1, archivo_nombre1, archivo2, archivo_nombre2, archivo3, archivo_nombre3, archivo4, archivo_nombre4, jaulas, jaula_desde FROM view_solicitudes WHERE view_solicitudes.id = {self.idsolicitud}")
        self.compania = ejecutar_sql("SELECT nombre, nombrecorto, logo, rut, direccion, telefono, paginaweb, email, contacto, correos_google_drive, telegram_token, telegram_chatid FROM compania")
        
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
        self.story.append(Spacer(1, 20))

        encabezado_datos = [
            ['Piloto:', self.solicitud[0][5], 'Centro:', self.solicitud[0][3]],
            ['Encargado:', self.solicitud[0][6], 'Fecha:', self.solicitud[0][1].strftime('%d de %B de %Y')]
        ]
        encabezado = Table(encabezado_datos, colWidths=[70, 200, 70, 200])
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

    def crear_tabla_jaulas(self):
        jaulas_data = ejecutar_sql(f"SELECT jaula FROM jaulas WHERE idsolicitud = {self.idsolicitud} ORDER BY jaula ASC")
        
        jaulas_impares = []
        jaulas_pares = []
        
        for jaula in jaulas_data:
            if int(jaula[0]) % 2 == 0:
                jaulas_pares.append(jaula[0])
            else:
                jaulas_impares.append(jaula[0])
        
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
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            alignment=1,
            fontSize=12,
            spaceAfter=0
        )
        self.story.append(Paragraph(
            "Informe Centro BAJOS LAMI SERVICIOS SUBMARINOS E-ROV",
            title_style
        ))
        
        self.story.append(Paragraph("Extracción de Mortalidad", title_style))
        self.story.append(Spacer(1, 12))

        jaulas_table = self.crear_tabla_jaulas()
        self.story.append(jaulas_table)
        self.story.append(Spacer(1, 24))

        self.story.append(PageBreak())
        self.crear_encabezado()

        data = ejecutar_sql(f"SELECT jaulas.jaula, COUNT(jaulas_detalle.id) AS cantidad, COALESCE((SELECT GROUP_CONCAT(descripcion SEPARATOR ', ') FROM jaulas_detalle AS jd WHERE jd.idsolicitud = {self.idsolicitud} AND jd.idjaula = jaulas_detalle.idjaula AND jd.descripcion IS NOT NULL AND TRIM(jd.descripcion) <> ''), '') AS descripciones FROM jaulas_detalle LEFT JOIN jaulas ON jaulas_detalle.idjaula = jaulas.id WHERE jaulas_detalle.idsolicitud = {self.idsolicitud} GROUP BY jaulas_detalle.idjaula, jaulas.jaula ORDER BY jaulas.jaula ASC;")
        total = sum(row[1] for row in data)
        data.append(("Total", total, ""))

        obs_style = ParagraphStyle(
            'Observaciones',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=12,
            alignment=TA_LEFT
        )

        processed_data = []
        for row in data:
            jaula, cantidad, observaciones = row
            obs_text = observaciones.replace(", ", "<br/>")
            obs_paragraph = Paragraph(obs_text, obs_style)
            processed_data.append([jaula, cantidad, obs_paragraph])

        table_data = [['N° JAULA', 'CANTIDAD', 'OBSERVACIONES']] + processed_data
        col_widths = ["15%", "15%", "70%"]
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (2, 1), (2, -1), 5),
            ('RIGHTPADDING', (2, 1), (2, -1), 5),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ]))
        self.story.append(table)
        self.story.append(Spacer(1, 24))

        self.story.append(PageBreak())
        self.crear_encabezado()

        bold_centered_style = ParagraphStyle(
            'BoldCentered',
            parent=self.styles['Normal'],
            alignment=1,
            fontName='Helvetica-Bold',
            fontSize=12,
        )

        self.story.append(Paragraph("Registro Fotográfico", title_style))
        sql = f"SELECT jaulas.jaula, jaulas.id FROM jaulas WHERE idsolicitud = {self.idsolicitud}"
        jaulas = ejecutar_sql(sql)
        if not jaulas:
            return

        for jaula in jaulas:
            sql = f"SELECT multimedia, descripcion FROM jaulas_detalle WHERE idsolicitud = {self.idsolicitud} AND idjaula = {jaula[1]}"
            imagenes = ejecutar_sql(sql)
            if not imagenes:
                continue


            bookmark = Paragraph(f'<a name="jaula_{jaula[0]}"/>', self.styles['Normal'])
            self.story.append(bookmark)
            title_with_line = Table([[Paragraph(f"JAULA N°: {jaula[0]}", self.styles['Heading3'])]],
                                  style=TableStyle([
                                      ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                      ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                                      ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                                      ('TOPPADDING', (0, 0), (-1, 0), 10),
                                  ]))
            self.story.append(title_with_line)
            self.story.append(Spacer(1, 10))
            
            sql = f"SELECT multimedia, descripcion FROM jaulas_detalle WHERE idsolicitud = {self.idsolicitud} AND idjaula = {jaula[1]}"
            imagenes = ejecutar_sql(sql)
            if imagenes:
                table_data = [[], []]
                
                for imagen in imagenes:
                    imagen_data = base64.b64decode(imagen[0])
                    img_path = BytesIO(imagen_data)
                    img = Image(img_path, width=100, height=100)
                    table_data[0].append(img)
                    
                    desc = str(imagen[1]) if imagen[1] is not None else ""
                    table_data[1].append(Paragraph(desc, self.styles['Normal']))
                
                table = Table(table_data, colWidths=[120] * len(imagenes))
                table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BOX', (0, 0), (-1, -1), 1, colors.black),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 2), (-1, 2), 10),
                    ('BOTTOMPADDING', (0, 2), (-1, 2), 10),
                ]))
                
                self.story.append(table)
                self.story.append(Spacer(1, 20))

    def generar_reporte(self):
        self.crear_encabezado()
        self.crear_contenido()
        self.build(self.story, canvasmaker=NumberedCanvas)

def main():
    archivo = "reporte_servicios_submarinos.pdf"
    reporte = Imprimir_Informe_Mortalidad(archivo, 
                               id = 94, 
                               pagesize=letter,
                               rightMargin=30,
                               leftMargin=30,
                               topMargin=30,
                               bottomMargin=30)
    reporte.generar_reporte()
    print("Reporte PDF generado exitosamente.")

if __name__ == "__main__":
    main()