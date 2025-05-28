from django import forms

class CustomLoginForm(forms.Form):
    TIPO_USUARIO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('PROPIETARIO', 'Propietario'),
    ]
    tipo_usuario = forms.ChoiceField(
        choices=TIPO_USUARIO_CHOICES,
        label="Tipo de Usuario:",
        widget=forms.Select(attrs={
            'class': 'form-select text-uppercase',
            'id': 'id_tipo_usuario'
        })
    )
    username = forms.CharField(
        max_length=150,
        label="Usuario:",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su usuario',
            'autocomplete': 'username',
            'id': 'id_username'  
        })
    )
    password = forms.CharField(
        max_length=128,
        label="Contraseña:",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña',
            'autocomplete': 'current-password',
            'id': 'id_password'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_remember_me'
        }),
        label="Recordar Contraseña",
    )
