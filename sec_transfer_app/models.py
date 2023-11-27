from django.db import models

class ArchivoDesencriptado(models.Model):
    archivo_encriptado = models.FileField(upload_to='archivos_encriptados/')
    clave_desencriptacion = models.CharField(max_length=255)

class CorreoEncriptado(models.Model):
    destinatario = models.EmailField()
    asunto = models.CharField(max_length=255)
    archivo_encriptado = models.FileField(upload_to='archivos_encriptados/')
    clave_encriptacion = models.CharField(max_length=255)