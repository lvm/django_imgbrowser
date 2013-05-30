from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import permission_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.contrib import messages

from models import Imagenes
from models import Directorios

from forms import BuscarImagenesForm
from forms import ImagenesForm
from forms import DirectoriosForm

import utils

@login_required
def contenido_no_disponible(request):
    messages.add_message(request, messages.ERROR, "Registro no disponible.")
    return HttpResponseRedirect(reverse('imgbrowser_list'))

@login_required
@permission_required('django_imgbrowser.view_directorios')
def list(request, path=None):
    data = {
        'forms':{
            'buscar': BuscarImagenesForm(initial={'keyword': request.GET.get('keyword')}),
            },
        'directorio': Directorios.objects.with_fullpath(path,
                                                        grupo__in=request.user.groups.all()
                                                        ),
        'directorios': Directorios.objects.children(path,
                                                    grupo__in=request.user.groups.all()
                                                    ),
        'imagenes': Imagenes.objects.none(),
        }

    if request.user.has_perm('django_imgbrowser.view_imagenes'):
        data['imagenes'] = Imagenes.objects.in_fullpath(path, request.GET.get('keyword'))

    return render(request, "django_imgbrowser/list.html", data)

@login_required
def mkdir(request, obj_id=None):
    if obj_id:
        directorio = Directorios.objects.get(id=obj_id,
                                             grupo__in=request.user.groups.all())
        if directorio.deleted:
            contenido_no_disponible()

        directorio_obj = directorio
        directorios_qs = directorio.directorios_set.not_deleted(grupo__in=request.user.groups.all(), padre=directorio_obj)
    else:
        directorio = Directorios()
        directorio_obj = Directorios.objects.none()
        directorios_qs = Directorios.objects.not_deleted(grupo__in=request.user.groups.all(), padre=None)

    if request.GET.get('did'):
        directorio_obj = Directorios.objects.get(id=request.GET.get('did'),
                                             grupo__in=request.user.groups.all())
        directorios_qs = directorio.directorios_set.not_deleted(grupo__in=request.user.groups.all(), padre=directorio_obj)

    data = {
        'forms':{
            'directorios': DirectoriosForm(instance=directorio, request=request),
            },
        'directorio': directorio_obj,
        'directorios': directorios_qs,
        'imagenes': Imagenes.objects.none(),
        }

    if request.method == "POST":
        form = DirectoriosForm(request.POST, instance=directorio,
                               request=request)
        if form.is_valid():
            directorio = form.save(commit=False)
            directorio.save()
            form.save_m2m()

            return HttpResponseRedirect("%s%s" % 
                                        (reverse('imgbrowser_list'), 
                                         directorio.fullpath) )
        else:
            data['forms']['directorios'] = form

    return render(request, "django_imgbrowser/mkdir.html", data)

@permission_required('django_imgbrowser.add_directorios')
def mkdir_add(request):
    return mkdir(request)

@permission_required('django_imgbrowser.change_directorios')
def mkdir_change(request, obj_id):
    return mkdir(request, obj_id)

@login_required
def upload(request, obj_id=None):
    imagen = Imagenes()
    directorio = Directorios.objects.none()

    if obj_id:
        imagen = Imagenes.objects.get(id=obj_id,
                                      directorio__grupo__in=request.user.groups.all())
        if imagen.deleted:
            contenido_no_disponible()

        directorio = imagen.directorio
        directorios_qs = Directorios.objects.not_deleted(padre=directorio.id,
                                                         grupo__in=request.user.groups.all())

    else:
        directorios_qs = Directorios.objects.not_deleted(padre=None,
                                                         grupo__in=request.user.groups.all())

    data = {
        'forms':{
            'imagenes': ImagenesForm(instance=imagen,
                                     request=request),
            },
        'directorio': directorio,
        'directorios': directorios_qs,
        'imagenes': Imagenes.objects.none(),
        }

    if request.method == "POST":
        form = ImagenesForm(request.POST, request.FILES, instance=imagen,
                            request=request)
        if form.is_valid():
            imagen = form.instance
            imagen.save()

            if not utils.has_thumbnail(imagen.path):
                utils.generate_thumbnail(imagen.path)
        

            return HttpResponseRedirect("%s%s"%(reverse('imgbrowser_list'), 
                                                '' if not imagen.directorio \
                                                    else imagen.directorio.fullpath)
                                        )
        else:
            data['forms']['imagenes'] = form

    return render(request, "django_imgbrowser/upload.html", data)

@permission_required('django_imgbrowser.add_imagenes')
def upload_add(request):
    return upload(request)

@permission_required('django_imgbrowser.change_imagenes')
def upload_change(request, obj_id):
    return upload(request, obj_id)

@login_required
def delete_obj(request, obj_type=None, obj_id=None):
    if not obj_id or not obj_type:
        return HttpResponseRedirect(reverse('imgbrowser_list'))
    else:
        data = {
            'objeto': None,
            'relacionados': {'directorios':Directorios.objects.none(), 
                             'imagenes': Imagenes.objects.none() },
            'directorio': Directorios.objects.none(),
            'directorios': Directorios.objects.not_deleted(padre__id=None),
            'imagenes': Imagenes.objects.none(),
            }

        if obj_type == u"mkdir":
            directorio = Directorios.objects.get(id=obj_id)
            data['objeto'] = directorio

            if directorio.deleted:
                contenido_no_disponible()

            data['directorio'] = directorio
            data['directorios'] = directorio.directorios_set.not_deleted(padre__id=obj_id)
            data['relacionados']['imagenes'] = Imagenes.objects.in_fullpath(directorio.fullpath)
            
            if directorio.directorios_set.count() > 0:
                messages.add_message(request, messages.WARNING, 
                                     "Esta por eliminar un directorio con contenido relacionado.")

        if obj_type == u"upload":
            imagen = Imagenes.objects.get(id=obj_id)
            data['objeto'] = imagen
            if imagen.deleted:
                contenido_no_disponible()

        if request.POST.get('post'):
            obj_name = ""

            if obj_type == u"mkdir":
                obj_name = Directorios._meta.verbose_name

                # delete directori
                directorio.deleted = True
                directorio.save()

                # delete children directori
                for subdirectorio in data['directorios']:            
                    if subdirectorio.directorios_set.count()>0:
                        # recursive directori
                        delete_obj(request, obj_type, obj_id)

                    subdirectorio.deleted = True
                    subdirectorio.save()

                for imagen in data['imagenes']:
                    imagen.deleted = True
                    imagen.save()

            if obj_type == u"upload":
                obj_name = Imagenes._meta.verbose_name
                
                # delete imagen
                imagen.deleted = True
                imagen.save()


            messages.add_message(request, messages.SUCCESS, 
                                 "%s eliminado correctamente." % obj_name)
            return HttpResponseRedirect(reverse('imgbrowser_list'))

        return render(request, "django_imgbrowser/delete.html", data)

@permission_required('django_imgbrowser.delete_directorios')
def delete_mkdir(request, obj_id=None):
    return delete_obj(request, 'mkdir', obj_id)

@permission_required('django_imgbrowser.delete_imagenes')
def delete_upload(request, obj_id=None):
    return delete_obj(request, 'upload', obj_id)
