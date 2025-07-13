import random
from ftplib import FTP
from twilio.rest import Client
import os
import shutil
from variables_globales import assets_dir, upload_dir, ruta_actual
from datetime import datetime, time, timedelta
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication  # Añadido para MIMEApplication
import email.utils  # Añadido para email.utils
from email import encoders
import base64
import os
import io
from PIL import Image as PILImage, ImageDraw
import flet.canvas as cv
import flet as ft
import socket

def obtener_ip_local():
    hostname = socket.gethostname()
    ip_local = socket.gethostbyname(hostname)
    return ip_local

def grabar_en_disco(nombre_archivo, contenido_binario):
    # Decodificar el contenido base64 a binario
    print("antes......")
    try:
        contenido_decodificado = base64.b64decode(contenido_binario)
        # Construir ruta completa usando assets_upload_dir
        ruta_completa = os.path.join(upload_dir, nombre_archivo)
        ruta_completa = os.path.join(ruta_actual, ruta_completa)
        print("grabar_disco : ", ruta_completa)
        #if not os.path.isabs(ruta_completa):
        #    ruta_completa = os.path.abspath(ruta_completa)
        #    print("Ruta en disco: ", ruta_completa)
        # Asegurar que el directorio existe
        #os.makedirs(os.path.dirname(ruta_completa), exist_ok=True)
        # Escribir el contenido decodificado al archivo
        with open(ruta_completa, 'wb') as archivo:
            archivo.write(contenido_decodificado)
        return ruta_completa
    except Exception as e:
        print(f"Error al grabar archivo {nombre_archivo}: {str(e)}")
        return None

def enviar_correo(destinatarios, asunto, cuerpo, archivos_adjuntos=None, borrar_temporales=False):
    # Configuración del servidor SMTP
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    correo_emisor = 'alfredogarc@gmail.com'
    contraseña = 'tjej pzey apjm ylkv'
    
    # Crear el objeto del mensaje
    mensaje = MIMEMultipart()
    mensaje['From'] = correo_emisor
    lista_destinatarios = [dest.strip() for dest in destinatarios.split(',')]
    mensaje['To'] = ', '.join(lista_destinatarios)
    mensaje['Subject'] = asunto
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    # Adjuntar archivos si existen
    if archivos_adjuntos:
        for archivo in archivos_adjuntos:
            archivo = archivo.strip()  # Asegúrate de que no haya espacios en blanco
            print(f"Procesando archivo: {archivo}")
            
            # Corregir la ruta del archivo si es necesario
            archivo = os.path.normpath(archivo)
            print(f"Ruta normalizada: {archivo}")
            
            # Verificar si el archivo existe
            if not os.path.isfile(archivo):
                print(f"El archivo {archivo} no existe")
                continue
                
            # Obtener el nombre y la extensión correctamente
            nombre_archivo = os.path.basename(archivo)
            print(f"Nombre del archivo extraído: {nombre_archivo}")
            
            # Si el nombre del archivo contiene "assetsuploads", extraer solo lo que está después
            if "assetsuploads" in archivo:
                # Buscar la posición de "assetsuploads" en la ruta
                pos = archivo.find("assetsuploads")
                if pos != -1:
                    # Obtener la parte después de "assetsuploads/"
                    pos_final = pos + len("assetsuploads")  # +1 para incluir el separador
                    if pos_final < len(archivo):
                        nombre_archivo = archivo[pos_final:]
                        print(f"Nombre del archivo limpiado: {nombre_archivo}")
            
            # Verificar la extensión del archivo
            extension = os.path.splitext(nombre_archivo)[1].lower()
            
            # Asignar el tipo MIME correcto
            if extension == '.jpg' or extension == '.jpeg':
                tipo_mime = 'image/jpeg'
            elif extension == '.png':
                tipo_mime = 'image/png'
            elif extension in ['.mp4', '.avi', '.mov']:
                tipo_mime = 'video/mp4'
            elif extension in ['.xlsx', '.xls']:
                tipo_mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif extension in ['.docx', '.doc']:
                tipo_mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif extension == '.pdf':
                tipo_mime = 'application/pdf'
            else:
                tipo_mime = 'application/octet-stream'
            
            print(f"Tipo MIME: {tipo_mime}")
            
            try:
                with open(archivo, 'rb') as adjunto:
                    # Para archivos PDF, usamos un enfoque diferente
                    if extension == '.pdf':
                        parte = MIMEApplication(adjunto.read(), _subtype='pdf')
                    else:
                        parte = MIMEBase(*tipo_mime.split('/', 1))
                        parte.set_payload(adjunto.read())
                        encoders.encode_base64(parte)
                    
                    # Establecer los encabezados correctamente
                    parte.add_header('Content-Disposition', 'attachment', filename=nombre_archivo)
                    
                    # Añadir encabezados adicionales para mejorar la compatibilidad
                    parte.add_header('Content-ID', f'<{nombre_archivo}>')
                    parte.add_header('X-Attachment-Id', nombre_archivo)
                    
                    mensaje.attach(parte)
                    print(f"Archivo {nombre_archivo} adjuntado correctamente")
            except FileNotFoundError:
                print(f"El archivo {archivo} no fue encontrado y no se adjuntará.")
            except Exception as e:
                print(f"Error al adjuntar el archivo {archivo}: {e}")
    
    # Enviar el correo
    try:
        servidor = smtplib.SMTP(smtp_server, smtp_port)
        servidor.starttls()
        servidor.login(correo_emisor, contraseña)
        texto = mensaje.as_string()
        servidor.sendmail(correo_emisor, lista_destinatarios, texto)
        servidor.quit()
        print("Correo enviado correctamente")
        
        # Borrar archivos temporales si se solicita
        if borrar_temporales and archivos_adjuntos:
            for archivo in archivos_adjuntos:
                try:
                    if os.path.exists(archivo):
                        os.remove(archivo)
                        print(f"Archivo temporal eliminado: {archivo}")
                except Exception as e:
                    print(f"Error al eliminar archivo temporal {archivo}: {e}")
                    
        return True
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False

def enviar_correo_anterior(destinatarios, asunto, cuerpo, archivos_adjuntos=None, borrar_temporales=False):
    # Configuración del servidor SMTP
    smtp_server = 'smtp.gmail.com'  # Cambia esto según tu proveedor de correo
    smtp_port = 587  # Puerto para TLS
    correo_emisor = 'alfredogarc@gmail.com'  # Cambia esto por tu correo
    contraseña = 'tjej pzey apjm ylkv'  # Cambia esto por tu contraseña

    # Crear el objeto del mensaje
    mensaje = MIMEMultipart()
    mensaje['From'] = correo_emisor
    # Separar los destinatarios por coma y eliminar espacios en blanco
    lista_destinatarios = [dest.strip() for dest in destinatarios.split(',')]

    mensaje['To'] = ', '.join(lista_destinatarios)
    mensaje['Subject'] = asunto
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    # Adjuntar archivos si existen
    print(f"Archivos adjuntos {archivos_adjuntos}")
    if archivos_adjuntos:
        for archivo in archivos_adjuntos:
            print(f"1- archivo: {archivo}")
            nombre, extension = archivo.rsplit('.', 1)
            archivo = f"{nombre.rstrip()}." + extension.strip()
            try:
                # Verificar la extensión del archivo
                nombre_archivo = os.path.basename(archivo)
                nombre_archivo = nombre_archivo.strip()
                print(f"Nombre Archivo: {nombre_archivo}")
                extension = os.path.splitext(nombre_archivo)[1].lower()
                
                # Establecer el tipo MIME correcto según la extensión
                if extension == '.jpg' or extension == '.jpeg':
                    tipo_mime = 'image/jpeg'
                elif extension == '.png':
                    tipo_mime = 'image/png'
                elif extension == '.mp4' or extension == '.avi' or extension == '.mov':
                    tipo_mime = 'video/mp4'
                elif extension == '.xlsx' or extension == '.xls':
                    tipo_mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                elif extension == '.docx' or extension == '.doc':
                    tipo_mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                elif extension == '.pdf':
                    tipo_mime = 'application/pdf'
                else:
                    tipo_mime = 'application/octet-stream'
                # Construir la ruta completa del archivo usando assets_upload_dir
                ruta_completa = archivo
                print(" PDF: ", ruta_completa, "  ", extension)
                
                with open(ruta_completa, 'rb') as adjunto:
                    parte = MIMEBase('application', tipo_mime)
                    parte.set_payload(adjunto.read())
                encoders.encode_base64(parte)
                parte.add_header(
                    'Content-Disposition',
                    f'attachment; filename={nombre_archivo}'
                )
                mensaje.attach(parte)
            #except OSError:
            #    # Si hay error al abrir el archivo, intentar borrarlo
            #    try:
            #        os.remove(archivo)
            #        print(f"Archivo {archivo} eliminado exitosamente")
            #    except OSError as e:
            #        print(f"Error al eliminar el archivo {archivo}: {e}")
            except FileNotFoundError:
                print(f"El archivo {archivo} no fue encontrado y no se adjuntará.")
    # Enviar el correo
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as servidor:
            servidor.starttls()
            servidor.login(correo_emisor, contraseña)
            servidor.sendmail(correo_emisor, lista_destinatarios, mensaje.as_string())
        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
    
    if borrar_temporales and archivos_adjuntos:
        for adjunto in archivos_adjuntos:
            if os.path.exists(adjunto):
                os.remove(adjunto)


def validar_correos(correos):
    # Expresión regular para validar correos electrónicos
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    correos_invalidos = []

    # Separar los correos por coma y eliminar espacios
    lista_correos = [correo.strip() for correo in correos.split(',')]

    # Validar cada correo
    for correo in lista_correos:
        if not re.match(patron, correo):
            correos_invalidos.append(correo)

    return correos_invalidos

def validar_enteros(e):
    valido = False
    try:
        # Try to convert to integer
        if e.control.value:
            int(e.control.value)
        # Clear error message if conversion successful
        e.control.error_text = None
        valido = True
    except ValueError:
        # Show error message and remove non-numeric characters
        e.control.error_text = "Solo se permiten números enteros"
        # Keep only digits
        e.control.value = ''.join(char for char in e.control.value if char.isdigit())
    
    # Update the TextField
    e.control.update()
    return valido

def validar_vacio(e):
    # Check if the control value is empty
    if not e.control.value:
        e.control.error_text = "Este campo no puede estar vacío"
        e.focus()
    else:
        # Clear error message if the field is not empty
        e.control.error_text = None
    e.control.update()

def mover_uploads_a_anterior(origen, destino):
    directorio_destino = os.path.dirname(destino)
    directorio_destino = os.path.join(ruta_actual,directorio_destino).replace("/","\\")
    origen = os.path.join(ruta_actual,upload_dir,origen).replace("\\","/")
    destino = os.path.join(ruta_actual,destino).replace("\\","/")
    print(f"Origen: {origen}, Destino: {destino}")
    if not os.path.exists(directorio_destino):
        os.makedirs(directorio_destino)
    shutil.copy(src=origen, dst=destino)
    shutil.delete(origen)

def mover_uploads_a(origen, destino):
    origen_a = origen
    origen = os.path.join(upload_dir,origen)
    #origen = os.path.join(ruta_actual,origen)
    #destino = os.path.join(ruta_actual,destino)
    directorio_destino = os.path.dirname(os.path.join(ruta_actual,destino))
    print(f"Origen: {origen}, Destino: {destino}")
    print("directorio destino: ", directorio_destino, " Ruta actual: ", ruta_actual)
    shutil.move(src=origen, dst=destino)
    #shutil.unlink(origen)


def generar_color_aleatorio():
    r = random.randint(0, 255)  # Componente rojo
    g = random.randint(0, 255)  # Componente verde
    b = random.randint(0, 255)  # Componente azul
    color = f'#{r:02x}{g:02x}{b:02x}'.upper()
    return color  # Retorna el color como una tupla RGB


def ftp_transfer(host, username, password, bSubir, local_file, remote_file):
    """
    Conectar a un servidor FTP y enviar o recibir un archivo.

    :param host: Dirección del servidor FTP.
    :param username: Nombre de usuario para autenticación.
    :param password: Contraseña para autenticación.
    :param operation: 'upload' para enviar un archivo o 'download' para recibir un archivo.
    :param local_file: Ruta del archivo local.
    :param remote_file: Ruta del archivo en el servidor FTP.
    """
    print("hola")
    try:
        # Conectar al servidor FTP
        ftp = FTP()
        ftp.connect(host)
        print(f"user: {username}, clave: {password}")
        ftp.login(user=username, passwd=password)
        print(f"Conectado a {host}")

        if local_file:
            if bSubir:
                with open(local_file, 'rb') as file:
                    ftp.storbinary(f'STOR {remote_file}', file)
                print(f"Archivo {local_file} enviado como {remote_file}")

            else:
                with open(local_file, 'wb') as file:
                    ftp.retrbinary(f'RETR {remote_file}', file.write)
                print(f"Archivo {remote_file} recibido como {local_file}")

    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        ftp.quit()


def ftp_transfer_2(host, username, password, bSubir, local_file, remote_file):
    import paramiko
    """
    Conectar a un servidor SFTP y enviar o recibir un archivo.

    :param host: Dirección del servidor SFTP.
    :param username: Nombre de usuario para autenticación.
    :param password: Contraseña para autenticación.
    :param operation: 'upload' para enviar un archivo o 'download' para recibir un archivo.
    :param local_file: Ruta del archivo local.
    :param remote_file: Ruta del archivo en el servidor SFTP.
    """
    try:
        # Crear un cliente SSH
        transport = paramiko.Transport((host, 22))
        transport.connect(username=username, password=password)
        
        # Crear un cliente SFTP
        sftp = paramiko.SFTPClient.from_transport(transport)
        print(f"Conectado a {host}")

        if local_file:
            if bSubir:
                sftp.put(local_file, remote_file)
                print(f"Archivo {local_file} enviado como {remote_file}")

            else:
                sftp.get(remote_file, local_file)
                print(f"Archivo {remote_file} recibido como {local_file}")

    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        sftp.close()
        transport.close()

def whatsapp_inicializar():
    whatsapp_enviar("+584123122996")
    whatsapp_enviar("+56973039525")
    print(" nuevo 1")

def whatsapp_enviar(telefono):
    
    account_sid = 'AC3188cd349603ac55df1118e60fcaf8b5'
    auth_token = '6a9accbab966bc89446c98ec9bb0b5ce'
    
    #body = "*¡Hola Cesar!*\n\nEsto es una prueba para enviar un mensaje a whatsapp desde python.\npara implementarlo en el sistema de control de flotas\n\n```Alfredo García```",

    client = Client(account_sid, auth_token)
    message = client.messages.create(
    from_='whatsapp:+14155238886',
    body = "*Se registró un control de flota trabajo ```'Descuento Total'```*",
    to=f'whatsapp:{telefono}'
    )

    print(" nuevo 2")
    print(message.sid)


def format_time(time_obj):
    """
    Formatea un objeto time o timedelta en una cadena "HH:MM".
    """
    if isinstance(time_obj, time):
        return time_obj.strftime("%H:%M")
    elif isinstance(time_obj, timedelta):
        total_minutes = int(time_obj.total_seconds() / 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"
    else:
        return "00:00"

def format_timedelta(timedelta_obj):
    """
    Formatea un objeto timedelta en una cadena "HH:MM".
    """
    if not isinstance(timedelta_obj, timedelta):
        return "00:00"
    
    total_minutes = int(timedelta_obj.total_seconds() / 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}"

def parse_time_string(time_str):
    """
    Convierte una cadena de tiempo "HH:MM" en un objeto time.
    """
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except (ValueError, TypeError):
        return time(0, 0)

def calcular_horas_diferencia(hora_desde, hora_hasta):
    """
    Calcula la diferencia entre dos horas y retorna las horas, minutos y un mensaje formateado.
    
    Args:
        hora_desde: objeto time o string en formato "HH:MM"
        hora_hasta: objeto time o string en formato "HH:MM"
    
    Returns:
        tuple: (horas, minutos, mensaje_formateado)
    """
    # Convertir strings a objetos time si es necesario
    if isinstance(hora_desde, str):
        hora_desde = parse_time_string(hora_desde)
    if isinstance(hora_hasta, str):
        hora_hasta = parse_time_string(hora_hasta)
    
    # Validar que ambas horas sean objetos time válidos
    if not isinstance(hora_desde, time) or not isinstance(hora_hasta, time):
        return 0, 0, "Error: formato de hora inválido"

    # Convertir las horas a minutos
    minutos_desde = hora_desde.hour * 60 + hora_desde.minute
    minutos_hasta = hora_hasta.hour * 60 + hora_hasta.minute

    # Si la hora hasta es menor que la hora desde, asumimos que cruza la medianoche
    if minutos_hasta < minutos_desde:
        minutos_hasta += 24 * 60  # Añadir 24 horas

    # Calcular la diferencia
    diferencia_minutos = minutos_hasta - minutos_desde
    horas = diferencia_minutos // 60
    minutos = diferencia_minutos % 60
    
    mensaje = f"Diferencia: {horas} horas y {minutos} minutos"
    return horas, minutos, mensaje


def main():
    print("IP , ", obtener_ip_local())

if __name__ == "__main__":
  main()

