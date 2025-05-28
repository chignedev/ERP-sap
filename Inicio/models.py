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

from django.db import models
from django.core.validators import MinValueValidator

class Centro(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Material(models.Model):
    TIPO_CHOICES = [
        ('FERT', 'FERT - Producto terminado'),
        ('ROH', 'ROH - Materia prima'),
        ('HALB', 'HALB - Producto semi-terminado'),
        ('SERV', 'SERV - Servicio'),
    ]

    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    unidad_medida = models.CharField(max_length=10, default='UN')
    descripcion = models.TextField(blank=True, null=True)
    
    centro = models.ForeignKey(Centro, on_delete=models.CASCADE, related_name='materiales')
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class ComponenteMaterial(models.Model):
    material_padre = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='componentes')
    componente = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='usado_en')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])

    def __str__(self):
        return f"{self.material_padre.codigo} ← {self.componente.codigo} x {self.cantidad}"

    class Meta:
        verbose_name = "Componente de Material"
        verbose_name_plural = "Componentes de Material"
