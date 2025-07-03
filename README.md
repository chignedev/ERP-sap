# 📦 Módulo de Transferencias de Stock

Este módulo forma parte del sistema ERP desarrollado en Django. Permite registrar, visualizar y controlar transferencias internas de materiales entre almacenes de manera segura y validada.

---

## 🚀 Funcionalidades principales

- 🔍 Visualizar el **stock actual** por almacén y material.
- 🔁 Registrar **movimientos de stock** entre almacenes.
- ✅ Validación automática del stock disponible.
- 📋 Historial de movimientos recientes por almacén.

---

## 🧱 Estructura general

### Modelos utilizados

- `Almacen`: almacenes físicos (ej. Lima, Trujillo).
- `ROH`: materiales tipo materia prima.
- `MovimientoStock`: entradas y salidas con motivo y cantidad.
  
---

## 🖥️ Interfaz (`movimientos.html`)

- Tarjetas por almacén mostrando:
  - Stock actual por ROH
  - Últimos movimientos registrados
- Formulario SweetAlert para nueva transferencia con:
  - Almacén origen/destino
  - Material (filtrado según almacén)
  - Cantidad (limitada al stock real)
  - Motivo (opcional)

---

## 🧪 Validaciones incorporadas

- ❌ No se permite transferir entre el mismo almacén.
- ❌ No se puede transferir más del stock disponible.
- ✅ Los materiales listados dependen del almacén origen.
- ✅ Visualización del stock disponible antes de confirmar.

---

## 📁 Archivos relevantes

- `views/almacen.py`: lógica de la vista `movimientos()`.
- `templates/admin/movimientos.html`: interfaz principal.
- `MovimientoStock`: modelo de control de entradas/salidas.
- `json_script`: transmisión de datos seguros al frontend.

---

## 📈 Mejoras posibles

- [ ] Exportación de reportes en PDF o Excel.
- [ ] Filtros por fecha, material o motivo.
- [ ] Historial detallado por material.
- [ ] Reversión de transferencias o ajustes manuales.

---

## ⚙️ Requisitos técnicos

- Django
- Bootstrap
- SweetAlert2
- CSRF activo en producción

---

## 👨‍💻 Autor

**Inkabytes**  
📍 [github.com/inkabytes](https://github.com/inkabytes)  
🎓 Estudiante de Diseño y Desarrollo de Software – Tecsup  
💡 Enfocado en construir sistemas reales que solucionen problemas reales.

---

> “Tecnologia para todos.”
