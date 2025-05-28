# forms.py

# 1. Importaciones de Django
from django import forms
from django.contrib.auth.models import Group
from django.forms import modelform_factory
from django.core.exceptions import ValidationError

# 2. Importaciones de Modelos Locales
from Inicio.models import (
    CustomUser, 
    Concepto, 
    Banco, 
    MedioPago, 
    TipoPago, 
    Periodo, 
    Recibo,
    DetalleRecibo, 
    ReciboPDF, 
    Departamento, 
    MiEdificio, 
    Cuentas, 
    CuotaMantenimiento,
    ComprobantePago,
    EmailTemplate,
    PersonalEdificio,
    ConceptoEgresoExtra,
    SaldoBancoMensual ,
    TipoGastoFinanciero,
)

# 3. Definiciones de Formularios
class CustomUserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña', 'autocomplete': 'new-password'}),
        label='Contraseña',
        required=False  # No obligatorio para edición
    )
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label='Grupo',
        widget=forms.Select(attrs={'class': 'form-select'})  # Usar form-select para dropdown
    )
    tipo_usuario = forms.ChoiceField(
        choices=CustomUser.TIPO_USUARIO_CHOICES,
        label='Nivel de Acceso',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    departamento = forms.ModelChoiceField(
        queryset=Departamento.objects.all(),
        required=False,
        empty_label="Seleccione un departamento",
        label="Departamento",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Nuevo campo para seleccionar el departamento de usuario secundario
    departamento_secundario = forms.ModelChoiceField(
        queryset=Departamento.objects.all(),
        required=False,
        empty_label="Seleccione un departamento",
        label="Departamento de Usuario Secundario",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'telefono', 'dni', 'password', 'group', 'tipo_usuario', 'departamento', 'departamento_secundario'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario', 'autocomplete': 'off'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'dni': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'DNI'}),
        }
        labels = {
            'tipo_usuario': 'Nivel de Acceso',
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            # Establecer valores iniciales para grupos y contraseña
            if self.instance.groups.exists():
                self.fields['group'].initial = self.instance.groups.first()
            self.fields['password'].widget.attrs['placeholder'] = 'Dejar en blanco para mantener la misma contraseña'   
                     
            # Mostrar o ocultar campo 'departamento' y 'departamento_secundario' dependiendo del grupo
            if self.instance.groups.filter(name="PROPIETARIO").exists():
                self.fields['departamento'].required = False
                
                # Verificar si el usuario es también usuario secundario de un departamento
                departamentos_secundarios = Departamento.objects.filter(usuarioSecundarios=self.instance)
                
                if departamentos_secundarios.exists():
                    self.fields['departamento_secundario'].required = False
                else:
                    self.fields['departamento_secundario'].widget.attrs['style'] = 'display:none'
                    self.fields['departamento_secundario'].label = ''
                
            elif self.instance.groups.filter(name="ADMINISTRADOR DEL EDIFICIO").exists():
                # Si el usuario es ADMINISTRADOR DEL EDIFICIO, mostrar ambos campos
                self.fields['departamento'].required = False
                self.fields['departamento_secundario'].required = False 
            else:
                # Mostrar el campo 'departamento_secundario' y ocultar 'departamento'
                self.fields['departamento_secundario'].required = False
                self.fields['departamento'].widget.attrs['style'] = 'display:none'
                self.fields['departamento'].label = ''
                
            # Verificar si el usuario está en el campo 'usuarioSecundarios' de algún departamento
            departamentos_con_usuario_secundario = Departamento.objects.filter(usuarioSecundarios=self.instance)
            if departamentos_con_usuario_secundario.exists():
                # Obtener el primer departamento donde el usuario es secundario
                departamento_secundario = departamentos_con_usuario_secundario.first()
                # Establecer el departamento como seleccionado en el campo 'departamento_secundario'
                self.fields['departamento_secundario'].initial = departamento_secundario
                # Asegurarse de que el campo 'departamento_secundario' sea visible
                self.fields['departamento_secundario'].widget.attrs['style'] = 'display:block'
        else:
            # Si es un usuario nuevo, ambos campos deben ser opcionales
            self.fields['departamento'].required = False
            self.fields['departamento_secundario'].required = False
   
    def save(self, commit=True):
        old_password = None
        if self.instance.pk:  # Solo si el usuario ya está en la base de datos
            try:
                userO = CustomUser.objects.get(pk=self.instance.pk)  # Obtener usuario previo
                old_password = userO.password  # Obtener la contraseña anterior
            except CustomUser.DoesNotExist:
                old_password = None  # En caso de que no se encuentre, lo dejamos vacío

        user = super().save(commit=False)
        
        if self.cleaned_data.get('password'):  # Si se ingresó una nueva contraseña
            user.set_password(self.cleaned_data['password'])
        elif old_password:  # Si no se ingresó una nueva, pero el usuario ya tenía una
            user.password = old_password

        user.save()  # Guardar primero para generar el ID
        
        # Asignación de grupo
        if self.cleaned_data.get('group'):
            group = self.cleaned_data['group']
            user.groups.clear()
            user.groups.add(group)
        
        # Asignación lógica de departamentos
        departamento_secundario = self.cleaned_data.get('departamento_secundario')
        departamento_principal = self.cleaned_data.get('departamento')

        if departamento_secundario:
            departamento_secundario.usuarioSecundarios.add(user)
        

        return user


# Formulario para Departamento
class DepartamentoForm(forms.ModelForm):
    # Campo para seleccionar el usuario asociado al departamento (solo PROPIETARIOS)
    usuario = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(),
        required=False,
        empty_label="Seleccione un propietario",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Usuario Asociado'
    )

    # Nuevo campo para usuarios secundarios
    usuarioSecundarios = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Usuarios Secundarios'
    )

    # Campo para seleccionar múltiples correos de usuarios que tienen email registrado
    correos = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.exclude(email__isnull=True).exclude(email=''),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Correos Asociados'
    )
    
    class Meta:
        model = Departamento
        fields = ['numeroDepartamento', 'nombre', 'usuario', 'usuarioSecundarios', 'correos']
        widgets = {
            'numeroDepartamento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de Departamento',
                'readonly': True  # Bloquea edición
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Departamento'
            }),
        }
        labels = {
            'numeroDepartamento': 'Número de Departamento',
            'nombre': 'Nombre del Departamento',
            'usuario': 'Usuario Asociado',
            'correos': 'Correos de Usuarios Asociados',
            'usuarioSecundarios': 'Usuarios Secundarios Asociados'
        }

    def __init__(self, *args, **kwargs):
        super(DepartamentoForm, self).__init__(*args, **kwargs)
        
        # Para los "Usuarios Secundarios", solo mostrar el nombre completo sin tipo de usuario
        if 'usuarioSecundarios' in self.fields:
            self.fields['usuarioSecundarios'].label_from_instance = lambda obj: obj.get_full_name()
        
        if self.instance and self.instance.pk:
            # Obtener el usuario actualmente asociado al departamento
            tipos_permitidos = ['PROPIETARIO', 'ADMIN']
            
            usuario_asociado = CustomUser.objects.filter(departamento=self.instance).first()
            
            # Filtrar solo usuarios de tipo PROPIETARIO para el campo usuario
            self.fields['usuario'].queryset = CustomUser.objects.filter(tipo_usuario__in=tipos_permitidos)

            # Preseleccionar el usuario actualmente asociado
            self.fields['usuario'].initial = usuario_asociado
            
            # Filtrar y mostrar solo los correos de usuarios que tienen email registrado
            self.fields['correos'].queryset = CustomUser.objects.exclude(email__isnull=True).exclude(email='')

            # Preseleccionar los correos electrónicos ya asociados al departamento
            self.fields['correos'].initial = self.instance.correos.all()

            # Modificar las opciones para que se muestren los correos en lugar de los nombres
            self.fields['correos'].label_from_instance = lambda obj: f"{obj.email} ({obj.get_full_name()})" 
                        
            # Usuarios secundarios asociados
            self.fields['usuarioSecundarios'].queryset = CustomUser.objects.filter()
            self.fields['usuarioSecundarios'].initial = self.instance.usuarioSecundarios.all()


    def save(self, commit=True):
        departamento = super().save(commit=False)
        if commit:
            # Primero se guarda el departamento para generar su primary key (numeroDepartamento)
            departamento.save()
            
            # Ahora se puede asignar el departamento al usuario seleccionado
            usuario_seleccionado = self.cleaned_data.get('usuario')
            if usuario_seleccionado:
                # Si hay un usuario anterior asignado, se desasocia
                usuario_anterior = CustomUser.objects.filter(departamento=departamento, tipo_usuario='PROPIETARIO').first()
                if usuario_anterior and usuario_anterior != usuario_seleccionado:
                    usuario_anterior.departamento = None
                    usuario_anterior.save()
                
                usuario_seleccionado.departamento = departamento
                usuario_seleccionado.save()
            
            # Asignar las relaciones many-to-many después de guardar el departamento
            departamento.correos.set(self.cleaned_data['correos'])
            departamento.usuarioSecundarios.set(self.cleaned_data['usuarioSecundarios'])
        
        return departamento
    
    
# Formulario para Banco
class BancoForm(forms.ModelForm):
    class Meta:
        model = Banco
        fields = ['nombre']


# Formulario para Concepto
class ConceptoForm(forms.ModelForm):
    class Meta:
        model = Concepto
        fields = ['nombre', 'tipo']


# Formulario para MedioPago
class MedioPagoForm(forms.ModelForm):
    class Meta:
        model = MedioPago
        fields = ['nombre']


# Formulario para TipoPago
class TipoPagoForm(forms.ModelForm):
    class Meta:
        model = TipoPago
        fields = ['nombre']


# Formulario para Periodo
class PeriodoForm(forms.ModelForm):
    class Meta:
        model = Periodo
        fields = ['nombre']


# Formulario para Recibo
class ReciboForm(forms.ModelForm):
    class Meta:
        model = Recibo
        fields = [
            'departamento', 'banco', 'medio_pago', 'fecha', 'año', 'total', 'total_texto'
        ]


# Formulario para DetalleRecibo
class DetalleReciboForm(forms.ModelForm):
    class Meta:
        model = DetalleRecibo
        fields = ['recibo', 'tipo_pago', 'concepto', 'mes', 'año', 'importe']


# Formulario para ReciboPDF
class ReciboPDFForm(forms.ModelForm):
    class Meta:
        model = ReciboPDF
        fields = ['recibo', 'pdf_url']

# Formulario para MiEdificio
from django import forms
from Inicio.models import MiEdificio

class MiEdificioForm(forms.ModelForm):
    class Meta:
        model = MiEdificio
        fields = [
            'nombre', 'direccion', 'celular', 'nombre_administradora', 
            'email_administradora', 'cargo_administradora', 'firma_url'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del edificio'}),
            'direccion': forms.TextInput(attrs={'placeholder': 'Dirección completa'}),
            'celular': forms.TextInput(attrs={'placeholder': 'Número de contacto'}),
            'nombre_administradora': forms.TextInput(attrs={'placeholder': 'Nombre de la administradora'}),
            'email_administradora': forms.EmailInput(attrs={'placeholder': 'Correo de la administradora'}),
            'cargo_administradora': forms.TextInput(attrs={'placeholder': 'Cargo de la administradora'}),
            'firma_url': forms.FileInput(attrs={'accept': 'image/*'}),
        }

class PersonalEdificioForm(forms.ModelForm):
    class Meta:
        model = PersonalEdificio
        fields = ['nombre', 'correo', 'cargo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nombre completo',
                'id': 'inputNombreReal'  # ID personalizado
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Correo electrónico',
                'id': 'inputCorreoReal'  # ID personalizado
            }),
            'cargo': forms.Select(attrs={'class': 'form-select'}),
        }


#Formulario para comprobande de pago
class ComprobantePagoForm(forms.ModelForm):
    class Meta:
        model = ComprobantePago
        fields = ['pdf_url']
        widgets = {
            'pdf_url': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
        
class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ['encabezado', 'pie']
        
        

class ImportarRecibosForm(forms.Form):
    file = forms.FileField(label="Subir archivo Excel")


class CuotaMantenimientoForm(forms.ModelForm):
    class Meta:
        model = CuotaMantenimiento
        fields = ['año', 'cuota']
        widgets = {
            'año': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Año de la cuota'
            }),
            'cuota': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Monto en soles'
            }),
        }
        labels = {
            'año': 'Año',
            'cuota': 'Monto de la Cuota',
        }



class ConceptoEgresoExtraForm(forms.ModelForm):
    class Meta:
        model = ConceptoEgresoExtra
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del gasto extra'
            }),
        }
        labels = {
            'nombre': 'Nombre del concepto',
        }



class SaldoBancoMensualForm(forms.ModelForm):
    class Meta:
        model = SaldoBancoMensual
        fields = ['banco', 'mes', 'año', 'saldo', 'saldoFinal'] 
        widgets = {
            'banco': forms.Select(attrs={'class': 'form-control'}),
            'mes': forms.Select(attrs={'class': 'form-control text-uppercase'}),
            'año': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2100}),
            'saldo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'saldoFinal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'banco': 'Banco',
            'mes': 'Mes',
            'año': 'Año',
            'saldo': 'Saldo Inicial (S/.)',
            'saldoFinal': 'Saldo Final (S/.)',
        }


from django import forms
from Inicio.models import TipoGastoFinanciero
from datetime import datetime

class TipoGastoFinancieroForm(forms.ModelForm):
    class Meta:
        model = TipoGastoFinanciero
        fields = [
            'nombre', 'año',
            'enero', 'febrero', 'marzo', 'abril',
            'mayo', 'junio', 'julio', 'agosto',
            'setiembre', 'octubre', 'noviembre', 'diciembre'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del gasto'}),
            'año': forms.Select(attrs={'class': 'form-select'}),
            **{mes: forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}) for mes in [
                'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                'julio', 'agosto', 'setiembre', 'octubre', 'noviembre', 'diciembre'
            ]}
        }
        labels = {
            'nombre': 'Nombre del Gasto',
            'año': 'Año',
            'enero': 'Enero',
            'febrero': 'Febrero',
            'marzo': 'Marzo',
            'abril': 'Abril',
            'mayo': 'Mayo',
            'junio': 'Junio',
            'julio': 'Julio',
            'agosto': 'Agosto',
            'setiembre': 'Setiembre',
            'octubre': 'Octubre',
            'noviembre': 'Noviembre',
            'diciembre': 'Diciembre',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        actual = datetime.now().year
        self.fields['año'].choices = [(i, i) for i in range(2023, actual + 2)]

