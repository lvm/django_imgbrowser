from django.forms import ModelForm
from django.forms import CharField
from django.forms import Form
from django.forms import HiddenInput
from django.forms import ValidationError

from django.contrib.auth.models import Group
from django.contrib import messages

from models import Directorios
from models import Imagenes

class BuscarImagenesForm(Form):
    keyword = CharField(label="Filtrar por", required=True)

class ImagenesForm(ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(ImagenesForm, self).__init__(*args, **kwargs)
        if not request.user.is_superuser:
            self.fields['directorio'].queryset = Directorios.objects.not_deleted(grupo__in=request.user.groups.all())

            if not self.instance.id:
                if not request.GET.get('did'):
                    self.fields['directorio'].queryset = self.fields['directorio'].queryset.filter(padre=None)
                else:
                    self.fields['directorio'].queryset = Directorios.objects.filter(id=request.GET.get('did')) | Directorios.objects.filter(padre__id=request.GET.get('did'))

    class Meta:
        model = Imagenes

class DirectoriosForm(ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(DirectoriosForm, self).__init__(*args, **kwargs)
        if not request.user.is_superuser:
            
            user_groups = request.user.groups

            if user_groups.count()<1:
                messages.add_message(request, messages.INFO,
                                     "No Pertenece a ningun grupo")

            self.fields['grupo'].queryset = user_groups.all()
            if user_groups.count() == 1:
                self.fields['grupo'].initial = user_groups.all()[0]

            directorios_qs = Directorios.objects.not_deleted(grupo__in=request.user.groups.all())

            # FIXME.REVIEWME.THINKME.BRAINSTORME.
            # posibles posibilidades:
            # - uno deberia poder mover al directorio a cualquier lado.
            # - uno no deberia poder editar al top-dir si ya tiene uno.
            # 
            # en demientras:

            if self.instance.id:
                if self.instance.padre:
                    self.fields['padre'].queryset = directorios_qs.filter(padre=self.instance.padre)
                else:
                    self.fields['padre'].queryset = directorios_qs.none()
            else:
                if request.GET.get('did'):
                    self.fields['padre'].queryset = directorios_qs.filter(id=request.GET.get('did'))
                else:
                    self.fields['padre'].queryset = directorios_qs.filter(padre=None)

    def clean(self):
        cleaned_data = super(DirectoriosForm, self).clean()
        nombre = cleaned_data.get("nombre")
        padre = cleaned_data.get("padre")
        
        if padre:
            dir_list = padre.directorios_set.not_deleted().values_list('nombre')
        else:
            dir_list = Directorios.objects.not_deleted(padre=None).values_list('nombre')

        if len(dir_list)>0:
            dir_list = (d[0] for d in dir_list)

        if nombre in dir_list:
            self._errors["nombre"] = self.error_class(["Nombre de directorio duplicado."])

        return cleaned_data

    class Meta:
        model = Directorios
