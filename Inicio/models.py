from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UsuarioManager  # 👈 nuevo
from django.db.models import Max

class Usuario(AbstractUser):
    ROLES = [
        ('materiales', 'Materiales'),
        ('planificacion', 'Planificacion'),
        ('aprobador', 'Aprobador'),
        ('compras', 'Compras'),
        ('almacen', 'Almacen'),
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



# ========================
# 📌 Centros y Almacenes
# ========================

class Sede(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    ciudad = models.CharField(max_length=50)
    pais = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class Almacen(models.Model):
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='almacenes')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    cantidad = models.IntegerField()

    def __str__(self):
        return f"{self.nombre} - {self.sede.nombre}"



# ======================================================================================
# 📌 ROH (Materia Prima), 📌 FERT (Producto Terminado), 📌 BOM (Lista de Materiales)
# ======================================================================================

class ROH(models.Model):
    codigo = models.CharField(max_length=8, unique=True)
    nombre = models.CharField(max_length=100)
    unidad_base = models.CharField(max_length=10, default='KG')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    centro = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='materiales_roh')
    almacen = models.ForeignKey('Almacen', on_delete=models.SET_NULL, null=True, blank=True, related_name='materiales_roh')

    def __str__(self):
        return f"{self.codigo} - {self.nombre} (ROH)"


class FERT(models.Model):
    codigo = models.CharField(max_length=8, unique=True)
    nombre = models.CharField(max_length=100)
    unidad_base = models.CharField(max_length=10, default='KG')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    centro = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='materiales_fert')
    almacen = models.ForeignKey('Almacen', on_delete=models.SET_NULL, null=True, blank=True, related_name='materiales_fert')  # ✅

    def __str__(self):
        return f"{self.codigo} - {self.nombre} (FERT)"


class BOM(models.Model):
    fert = models.ForeignKey(FERT, on_delete=models.CASCADE, related_name='componentes')
    roh = models.ForeignKey(ROH, on_delete=models.CASCADE, related_name='usado_en')
    cantidad = models.IntegerField()

    class Meta:
        unique_together = ('fert', 'roh')

    def __str__(self):
        return f"{self.fert.codigo} usa {self.cantidad} {self.roh.unidad_base} de {self.roh.codigo}"


# ========================
# 📌 Planificación
# ========================
class PlanVenta(models.Model):
    fert = models.ForeignKey(FERT, on_delete=models.CASCADE, related_name='planes_venta')
    cantidad_total = models.IntegerField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

class PlanVentaDetalle(models.Model):
    plan = models.ForeignKey(PlanVenta, on_delete=models.CASCADE, related_name='detalles')
    mes = models.IntegerField()
    año = models.IntegerField()
    cantidad = models.IntegerField()

class PlanProduccion(models.Model):
    venta = models.ForeignKey(PlanVenta, on_delete=models.CASCADE, related_name='planes_produccion')
    fert = models.ForeignKey(FERT, on_delete=models.CASCADE)
    cantidad_fert = models.IntegerField() 
    cantidad_fert_con_extra = models.IntegerField()
    costo_insumos = models.DecimalField(max_digits=10, decimal_places=2)
    costo_total_estimado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

class PlanProduccionDetalle(models.Model):
    plan = models.ForeignKey(PlanProduccion, on_delete=models.CASCADE, related_name='detalles')
    mes = models.IntegerField()
    año = models.IntegerField()
    cantidad_en_mes = models.IntegerField()
    
class PlanCompra(models.Model):
    produccion = models.ForeignKey(PlanProduccion, on_delete=models.CASCADE, related_name='planes_compra')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

class PlanCompraItem(models.Model):
    plan = models.ForeignKey(PlanCompra, on_delete=models.CASCADE, related_name='items')
    roh = models.ForeignKey(ROH, on_delete=models.CASCADE)
    cantidad_comprar = models.IntegerField()
    costo_total = models.DecimalField(max_digits=10, decimal_places=2)



class SOLPED(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    solicitante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solpeds')
    centro = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='solpeds')
    plan_produccion = models.ForeignKey(
        PlanProduccion, on_delete=models.SET_NULL, null=True, blank=True, related_name='solpeds'
    )
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('aprobado', 'Aprobado'),
            ('rechazado', 'Rechazado'),
            ('ordenado', 'Ordenado'),
        ],
        default='pendiente'
    )
    total_estimado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    comentario = models.TextField(blank=True, null=True)

    def __str__(self):
        ref = f"(Plan #{self.plan_produccion.id})" if self.plan_produccion else ""
        return f"SOLPED #{self.id} - {self.centro.nombre} {ref} - {self.get_estado_display()}"


class SOLPEDItem(models.Model):
    solped = models.ForeignKey(SOLPED, on_delete=models.CASCADE, related_name='items')
    material = models.ForeignKey(ROH, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    unidad = models.CharField(max_length=10)
    costo_estimado = models.DecimalField(max_digits=12, decimal_places=2)
    observacion = models.TextField(blank=True, null=True)

    # 🔑 Clave: referencia al insumo original del Plan de Ventas
    plan_insumo = models.ForeignKey(
        PlanCompraItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solped_items'
    )

    def __str__(self):
        return f"{self.material.nombre} x {self.cantidad} {self.unidad}"


# ========================
# 📌 Compras
# ========================
class Proveedor(models.Model):
    nombre = models.CharField(max_length=150)
    ruc = models.CharField(max_length=20, unique=True, help_text="Número de RUC o identificación fiscal")
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    estado = models.BooleanField(default=True, help_text="Activo o inactivo")

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.ruc})"

from django.db import models
from Inicio.models import SOLPED, SOLPEDItem, Proveedor, Usuario

class OrdenCompra(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    solicitante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='ordenes_compra')
    solped = models.ForeignKey(SOLPED, on_delete=models.CASCADE, related_name='ordenes_compra')
    comentario = models.TextField(blank=True, null=True)
    total_estimado = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"OC #{self.id} - de SOLPED #{self.solped.id}"


class OCItem(models.Model):
    orden = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name='items')
    solped_item = models.ForeignKey(SOLPEDItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='oc_items')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='oc_items')

    descripcion = models.CharField(max_length=200)
    cantidad = models.IntegerField()
    unidad = models.CharField(max_length=10)
    costo_estimado = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.descripcion} ({self.cantidad} {self.unidad}) - Proveedor: {self.proveedor.nombre}"


class OCEntregaProgramada(models.Model):
    item = models.ForeignKey(OCItem, on_delete=models.CASCADE, related_name='entregas_programadas')
    fecha_entrega = models.DateField()
    cantidad = models.IntegerField()

    def __str__(self):
        return f"Entrega {self.fecha_entrega} - {self.cantidad} unidades"



# ========================
# 📌 Almacen
# ========================

class EntradaMaterial(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    orden_compra = models.ForeignKey(OrdenCompra, on_delete=models.SET_NULL, null=True, blank=True)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name='entradas')
    comentario = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Entrada #{self.id} - {self.almacen.nombre}"


class EntradaItem(models.Model):
    entrada = models.ForeignKey(EntradaMaterial, on_delete=models.CASCADE, related_name='items')
    material = models.ForeignKey(ROH, on_delete=models.CASCADE)  # o FERT si quieres permitir ambos tipos
    cantidad = models.IntegerField()
    oc_item = models.ForeignKey(OCItem, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.material.nombre} x {self.cantidad}"


class MovimientoStock(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name='movimientos')
    material = models.ForeignKey(ROH, on_delete=models.CASCADE)  # o FERT si aplicara
    cantidad = models.IntegerField(help_text="Positivo: entrada, Negativo: salida")
    motivo = models.CharField(max_length=200, help_text="Ejemplo: 'Entrada OC', 'Consumo Producción', 'Ajuste'")
    referencia = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.material.nombre} ({self.cantidad}) - {self.almacen.nombre}"
