from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UsuarioManager  # 👈 nuevo

class Usuario(AbstractUser):
    ROLES = [
        ('solicitante', 'Solicitante'),
        ('aprobador', 'Aprobador'),
        ('comprador', 'Comprador'),
        ('admin', 'Administrador'),
    ]

    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    rol = models.CharField(max_length=20, choices=ROLES)
    foto = models.ImageField(upload_to='usuarios/fotos/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'rol']

    objects = UsuarioManager()  # 👈 el manager personalizado

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
