# 🛠️ Sistema ERP – Módulo de Administración

Este módulo administra y conecta los procesos clave de gestión logística, planificación y compras en una arquitectura ERP construida con Django. Incluye operaciones desde la solicitud de materiales (SOLPED), hasta las órdenes de compra y control de almacén.

---

## 🧭 Navegación principal

La interfaz de administración incluye un menú organizado por módulos, generado dinámicamente con `context_processors.py`.

### Menú de navegación

| Módulo         | Submódulos                                                  |
|----------------|-------------------------------------------------------------|
| **Centros**     | - Sedes<br>- Almacenes                                     |
| **Materiales**  | - Materiales (ROH)<br>- BOM (FERT)                         |
| **Planificación** | - Planes de Ventas<br>- SOLPED                          |
| **Aprobación**  | - Revisar SOLPED                                           |
| **Compras**     | - Proveedores<br>- Órdenes de Compra                      |
| **Almacén**     | - Entradas de Materiales<br>- Movimientos de Stock        |

Cada entrada del menú se genera con iconos (FontAwesome) y `reverse()` de Django para enlazar a la vista correspondiente.

---

## 🔍 Funcionalidades principales por módulo

### 📍 Centros
- Registrar sedes (ciudades, países).
- Gestionar almacenes físicos y su capacidad.

### 📦 Materiales
- Crear y editar materiales tipo ROH.
- Configurar estructuras BOM (FERT + componentes).

### 📊 Planificación
- Crear planes de venta mensuales.
- Generar planes de producción y SOLPED automáticos.

### ✅ Aprobación
- Verificar y aprobar solicitudes de compra (SOLPED).

### 🛒 Compras
- Registrar proveedores con RUC y contacto.
- Generar órdenes de compra basadas en SOLPEDs aprobadas.

### 🏭 Almacén
- Registrar entradas por OC.
- Transferir stock entre almacenes.
- Ver y controlar movimientos (entradas/salidas).

---

## 🧩 Componentes técnicos

- **Backend**: Django 4+ (con `reverse`, `select_related`, `context_processors`)
- **Frontend**: Bootstrap 5 + FontAwesome + SweetAlert2
- **Protección**: Validaciones CSRF, filtros de usuario autenticado
- **Base de datos**: PostgreSQL o SQLite

---

## 🗂️ Estructura destacada

```bash
/Admin
├── templates/admin/
│   ├── movimientos.html         # Vista de transferencias de stock
│   ├── entradas.html            # Vista de entradas de materiales
│   └── ...                      # Otras plantillas del módulo
├── views/
│   └── almacen.py               # Lógica de stock, movimientos y entradas
├── context_processors.py        # 👈 Genera menú lateral dinámico
└── urls.py                      # Rutas internas del módulo Admin

```

## 📦 Requisitos

- Python
- Django
- Bootstrap
- SweetAlert2
- FontAwesome

---

## 🙋‍♂️ Autor

**Inkabytes**  
🔗 [github.com/inkabytes](https://github.com/inkabytes)  
🎓 Estudiante de Diseño y Desarrollo de Software – Tecsup  


---

> “Tecnologia para todos.”
