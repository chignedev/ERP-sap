from django.apps import apps
from datetime import datetime

def menu_context(request):
    """
    Añade los modelos de acceso y recibos al contexto de todas las vistas, 
    filtrados por grupo y usuario.
    """
    # Si no está autenticado, devolver menús vacíos
    if not request.user.is_authenticated:
        return {
            'menu_ingresos': [],
            'menu_deudas': [],
            'menu_egresos':[],
            'menu_reportes':[],
            'menu_acceso': [],
            'menu_admin': [],
            'menu_mantenimiento': [],
        }

    # DATOS BASE
    # ------------------------------------------------------------------
    menu_ingresos_data = [
        {'name': 'Saldos Bancarios', 'icon': 'fas fa-university', 'url': 'Admin:listar_saldos'},
        {'name': 'Ver Recibos', 'icon': 'fas fa-file-invoice-dollar', 'url': 'Admin:inicio'},
        {'name': 'Crear Recibo', 'icon': 'fas fa-file-signature', 'url': 'Admin:crear_recibo'},
    ]

    menu_deudas_data = [
        {'name': 'Registro de Deudas', 'icon': 'fas fa-receipt', 'url': 'Admin:deudas'},
        {'name': 'Cuentas por Cobrar', 'icon': 'fas fa-money-check-alt', 'url': 'Admin:cuentas'},
    ]
    
    menu_egresos_data = [
        {'name': 'Gastos Bancarios', 'icon': 'fas fa-university', 'url': 'Admin:listar_gastos_financieros'},
        {'name': 'Egresos', 'icon': 'fas fa-receipt', 'url': 'Admin:vista_egresos'},
        {'name': 'Reportes', 'icon': 'fas fa-receipt', 'url': 'Admin:reporte_eecc'},
    ]
    
    menu_reportes_data = [
        {'name': 'Ingresos', 'icon': 'fas fa-coins', 'url': 'Admin:reportes_ingresos'},
        {'name': 'Egresos', 'icon': 'fas fa-file-invoice-dollar', 'url': 'Admin:reportes_egresos'},
        {'name': 'Balance', 'icon': 'fas fa-scale-balanced', 'url': 'Admin:reportes_balance'},
        {'name': 'Cuentas por Cobrar', 'icon': 'fas fa-hand-holding-usd', 'url': 'Admin:reportes_cuentas_cobrar'},
    ]

    menu_acceso_data = [
        {'name': 'Mi Edificio', 'icon': 'fas fa-building', 'url': 'Admin:listar_edificio'},
        {'name': 'Departamentos', 'icon': 'fas fa-door-open', 'url': 'Admin:listar_departamentos'},
        {'name': 'Grupos', 'icon': 'fas fa-users-cog', 'url': 'Admin:listar_grupos'},
        {'name': 'Usuarios', 'icon': 'fas fa-user-circle', 'url': 'Admin:listar_customusers'},
    ]
    
    menu_admin_data = [
        {'name': 'Plantilla de Correo', 'url': 'Admin:editar_plantilla', 'icon': 'fas fa-envelope'},
        {'name': 'Importar', 'url': 'Admin:importarData', 'icon': 'fas fa-file-import'},
        {'name': 'Exportar', 'url': 'Admin:exportarData', 'icon': 'fas fa-file-export'},
        {'name': 'Eliminar', 'url': 'Admin:eliminar_recibos_por_año', 'icon': 'fas fa-trash-alt'},
    ]
          
    menu_mantenimiento_data = [
        {'name': 'Conceptos', 'icon': 'fas fa-tags', 'url': 'Admin:listar_conceptos'},
        {'name': 'Bancos', 'icon': 'fas fa-university', 'url': 'Admin:listar_bancos'},
        {'name': 'Medios de Pago', 'icon': 'fas fa-credit-card', 'url': 'Admin:listar_medios_pago'},
        {'name': 'Tipos de Pago', 'icon': 'fas fa-receipt', 'url': 'Admin:listar_tipos_pago'},
        {'name': 'Periodos', 'icon': 'fas fa-calendar-alt', 'url': 'Admin:listar_periodos'},
        {'name': 'Recibos', 'icon': 'fas fa-receipt', 'url': 'Admin:vista_recibos'},
        {'name': 'Cuotas Mantenimiento', 'icon': 'fas fa-coins', 'url': 'Admin:listar_cuotas_mantenimiento'},
        {'name': 'Conceptos de Gastos Extra', 'icon': 'fas fa-plus-circle', 'url': 'Admin:listar_conceptos_egresos_extras'},
    ]

    # DETECTAR PERMISOS
    # ------------------------------------------------------------------
    is_superuser = request.user.is_superuser
    is_group_1 = request.user.groups.filter(id=1).exists()
    is_usercustom_1 = (request.user.id == 1)
    is_group_2 = request.user.groups.filter(id=2).exists()
    is_group_5 = request.user.groups.filter(id=5).exists()

    # Definición de la lógica según el tipo de usuario
    # ------------------------------------------------------------------
    # Si es superadmin, user=1, o group=1 => ACCESO TOTAL
    if is_superuser or is_group_1 or is_usercustom_1:
        pass

    # El grupo 2 => solo enlaces_rapidos, acceso_modelos y recibos_modelos
    elif is_group_2:
        menu_deudas_data = [
            item for item in menu_deudas_data 
        ]
        menu_recibos_data = []
        menu_admin_data = []

    # El grupo 5 => solo enlaces_rapidos
    elif is_group_5:
        menu_deudas_data = []
        menu_recibos_data = []
        menu_acceso_data = []
        menu_admin_data = []
        menu_mantenimiento_data = []

    # Cualquier otro grupo => devolver menús vacíos
    else:
        menu_ingresos_data = []
        menu_deudas_data = []
        menu_egresos_data = []
        menu_reportes_data = []
        menu_acceso_data = []
        menu_admin_data = []
        menu_mantenimiento_data = []

    # RETORNAR EL CONTEXTO
    # ------------------------------------------------------------------
    ahora = datetime.now()
    meses_nombre = [
        "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
        "JULIO", "AGOSTO", "SETIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
    ]
    mes_sistema = meses_nombre[ahora.month - 1]
    año_actual = ahora.year
    
    return {        
        'menu_ingresos': menu_ingresos_data,
        'menu_deudas': menu_deudas_data,
        'menu_egresos': menu_egresos_data,
        'menu_reportes': menu_reportes_data,
        'menu_acceso': menu_acceso_data,
        'menu_admin': menu_admin_data,
        'menu_mantenimiento': menu_mantenimiento_data,
        
        'mes_sistema': mes_sistema,
        'año_actual': año_actual,
    }
