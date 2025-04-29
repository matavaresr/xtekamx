from django import forms
from apps.core.models import Usuario
from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    usuario = forms.CharField(label="Usuario", max_length=100)
    contrasena = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        usuario = cleaned_data.get('usuario')
        contrasena = cleaned_data.get('contrasena')

        try:
            user = Usuario.objects.get(usuario=usuario)
            if user.contrasena != contrasena:  
                raise forms.ValidationError("Contraseña incorrecta")
        except Usuario.DoesNotExist:
            raise forms.ValidationError("Usuario no encontrado")

        return cleaned_data