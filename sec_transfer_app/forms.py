from django import forms
from .models import *

class CorreoEncriptadoForm(forms.ModelForm):
    destinatario = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={'placeholder': 'Destinatario'})
    )

    asunto = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Asunto'})
    )

    archivo_encriptado = forms.FileField(
        label='',
        widget=forms.ClearableFileInput(attrs={'placeholder': 'Archivo Encriptado'})
    )

    clave_encriptacion = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Clave de Encriptación'})
    )
    class Meta:
        model = CorreoEncriptado
        fields = ['destinatario', 'asunto', 'archivo_encriptado', 'clave_encriptacion']

class ArchivoDesencriptadoForm(forms.ModelForm):

    archivo_encriptado = forms.FileField(
        label='',
        widget=forms.ClearableFileInput(attrs={'placeholder': 'Archivo Encriptado'})
    )

    clave_desencriptacion = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Clave de Desencriptación'})
    )

    class Meta:
        model = ArchivoDesencriptado
        fields = ['archivo_encriptado', 'clave_desencriptacion']

