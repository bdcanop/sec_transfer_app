from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .forms import CorreoEncriptadoForm, ArchivoDesencriptadoForm
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os
from io import BytesIO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from cryptography.hazmat.primitives import hashes

def generate_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return key


def encrypt_file_data(file_data, password):
    salt = os.urandom(16)
    key = generate_key(password, salt)
    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(file_data) + encryptor.finalize()

    encrypted_data = salt + iv + ciphertext
    return encrypted_data

def decrypt_file_data(file_data, password):
    # Leer los bytes del archivo
    data = file_data.read()

    # Separar el salt, iv y ciphertext
    salt = data[:16]
    iv = data[16:32]
    ciphertext = data[32:]

    # Generar la clave
    key = generate_key(password, salt)

    # Configurar el cifrado y descifrar los datos
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    return plaintext


def enviar_correo_view(request):
    if request.method == 'POST':
        form = CorreoEncriptadoForm(request.POST, request.FILES)
        if form.is_valid():
            destinatario = form.cleaned_data['destinatario']
            asunto = form.cleaned_data['asunto']
            archivo_encriptado = form.cleaned_data['archivo_encriptado']
            clave_encriptacion = form.cleaned_data['clave_encriptacion']
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            smtp_username = 'bryandaniel1507@gmail.com'
            smtp_password = os.environ.get('EMAIL_BRYAN1507_PASSWORD')
            from_email = 'bryandaniel1507@gmail.com'
            file_data = archivo_encriptado.read()
            encrypted_data = encrypt_file_data(file_data, clave_encriptacion)

            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = destinatario
            msg['Subject'] = asunto
            # msg.attach(MIMEText(clave_encriptacion, 'plain'))

            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(encrypted_data)
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', f'attachment; filename={archivo_encriptado.name}')
            msg.attach(attachment)

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)

            msg2 = MIMEMultipart()
            msg2['From'] = from_email
            msg2['To'] = destinatario
            msg2['Subject'] = 'Clave de desencriptación'
            mensaje_clave = f"""Para desencriptar el archivo que se le envió debe visitar la página http://127.0.0.1:8000/
            En ella debe ingresar el archivo encriptado junto con la clave: -> {clave_encriptacion} <- en los campos correspondientes"""
            msg2.attach(MIMEText(mensaje_clave, 'plain'))

            with smtplib.SMTP(smtp_server, smtp_port) as server2:
                server2.starttls()
                server2.login(smtp_username, smtp_password)
                server2.send_message(msg2)
            
            messages.success(request, 'Correo encriptado y enviado con éxito.')
            return redirect('enviar_correo') 
        
    else:
        form = CorreoEncriptadoForm()
    
    return render(request, 'enviar_correo.html', {'form': form})



def desencriptar_archivo_view(request):
    if request.method == 'POST':
        form = ArchivoDesencriptadoForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_encriptado = form.cleaned_data['archivo_encriptado']
            clave_desencriptacion = form.cleaned_data['clave_desencriptacion']

            # decrypted_content = desencriptar_archivo(archivo_encriptado, clave_desencriptacion)
            decrypted_data = decrypt_file_data(archivo_encriptado, clave_desencriptacion)

            # Crear una respuesta de archivo y configurar su contenido
            response = HttpResponse(decrypted_data, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{archivo_encriptado.name}"'

            # Envío de LOGS
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            smtp_username = 'bryandaniel1507@gmail.com'
            smtp_password = os.environ.get('EMAIL_BRYAN1507_PASSWORD')

            msg = MIMEMultipart()
            msg['From'] = 'bryandaniel1507@gmail.com'
            msg['To'] = 'bryandaniel1507@gmail.com'
            msg['Subject'] = 'Un arhivo ha sido desencriptado'
            mensaje = f"el arhivo {archivo_encriptado.name} ha sido desencriptado con clave {clave_desencriptacion}"
            msg.attach(MIMEText(mensaje, 'plain'))

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)

            return response
    else:
        form = ArchivoDesencriptadoForm()

    return render(request, 'desencriptar_archivo.html', {'form': form})