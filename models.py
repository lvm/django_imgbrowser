from django.db import models
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import Http404
from django.db.models import Q
import os
import utils

class DirectoriosManager(models.Manager):
    # def clean_kwargs(self, kwargs):
    #     for k in kwargs.keys():
    #         if k not in self.model._meta.get_all_field_names():
    #             kwargs.pop(k, None)
    #     return kwargs

    def con_grupo(self, *args, **kwargs):
        return self.get_query_set().filter(**kwargs)

    def deleted(self, *args, **kwargs):
        return self.con_grupo(*args, **kwargs).filter(**dict(kwargs, **{'deleted':True}))

    def not_deleted(self, *args, **kwargs):
        return self.con_grupo(*args, **kwargs).filter(**dict(kwargs, **{'deleted':False}))

    def with_fullpath(self, fullpath=None, *args, **kwargs):
        if not fullpath:
            return None

        path = fullpath
        if path.find('/') != -1 and path[-1] == '/':
            path = path[:-1]
            fullpath = fullpath[:-1]
        path = os.path.basename(path)

        directories_list = [d for d in self.not_deleted(*args, **kwargs)\
                                .filter(nombre=path) if d.fullpath == fullpath]

        if len(directories_list)>=1:
            return directories_list[0]
        else:
            raise Http404()

    def siblings(self, path=None, *args, **kwargs):
        return [d for d in self.not_deleted(*args, **kwargs) if d.fullpath == path]

    def children(self, path=None, *args, **kwargs):
        if not path:
            return [d for d in self.not_deleted(*args, **kwargs) if not d.padre]
        else:
            return self.with_fullpath(path, *args, **kwargs).directorios_set.not_deleted(*args, **kwargs)

class ImagenesManager(models.Manager):
    def deleted(self, *args, **kwargs):
        return self.get_query_set().filter(**dict(kwargs, **{'deleted':True}))

    def not_deleted(self, *args, **kwargs):
        return self.get_query_set().filter(**dict(kwargs, **{'deleted':False}))

    def in_fullpath(self, path=None, keyword=None, *args, **kwargs):
        imagenes_qs = Imagenes.objects.none()

        if not path:
            imagenes_qs = self.not_deleted(*args, **kwargs).filter(directorio=None)
            if keyword:
                imagenes_qs = imagenes_qs.filter(id__in=imagenes_list).filter(
                    Q(nombre__icontains=keyword)|Q(alt__icontains=keyword)|
                    Q(descripcion__icontains=keyword))
        else: 
            imagenes_qs = Directorios.objects.with_fullpath(path).imagenes_set.not_deleted(*args, **kwargs)
            if keyword:
                imagenes_qs = imagenes_qs.filter(Q(nombre__icontains=keyword)|
                                                 Q(alt__icontains=keyword)|
                                                 Q(descripcion__icontains=keyword))

        return imagenes_qs

class Directorios(models.Model):
    deleted = models.BooleanField(default=False, editable=False)
    grupo = models.ManyToManyField(Group)

    nombre = models.CharField('Nombre', max_length=255)
    padre = models.ForeignKey('self', null=True, blank=True)

    @property
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, 
                                               ontent_type.model),
                       args=(self.id,))

    @property
    def fullpath(self):
        if self.padre:
            return u"%s/%s"%(self.padre, self.nombre)
        else:
            return u"%s"%self.nombre        

    def __unicode__(self):
        return self.fullpath

    def save(self,*args,**kwargs):
        if self.padre != None:
            dir_list = self.padre.directorios_set.not_deleted().values_list('nombre')
        else:
            dir_list = [d[0] for d in Directorios.objects.not_deleted(padre=None)\
                            .values_list('nombre')]

        if self.nombre in dir_list:
            raise Exception('Directorio existente.')

        super(Directorios, self).save(*args,**kwargs)

    objects = DirectoriosManager()
    class Meta:
        verbose_name = "Directorio"
        verbose_name_plural = "Directorios"

        permissions = (
            ("view_directorios", "Can view Directorio"),
            )


class Imagenes(models.Model):
    deleted = models.BooleanField(default=False, editable=False)

    directorio = models.ForeignKey(Directorios)
    nombre = models.CharField('Title', max_length=255, blank=True)
    alt = models.CharField('Alt', max_length=255, blank=True)
    descripcion = models.TextField('Descripcion', blank=True)

    archivo = models.ImageField(upload_to='.', max_length=500)

    @property
    def path(self):
        return u"%s"%self.archivo.path

    @property
    def thumbnail(self):
        if utils.has_thumbnail(self.path):
            return utils.thumbnail_name(self.url)
        return None

    @property
    def url(self):
        return u"%s"%self.archivo.url

    @property
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, 
                                               content_type.model),
                       args=(self.id,))

    def __unicode__(self):
        if self.nombre:
            return u"%s" % self.nombre
        else:
            return u"%s" % self.archivo.name

    objects = ImagenesManager()

    class Meta:
        verbose_name = "Imagen"
        verbose_name_plural = "Imagenes"

        permissions = (
            ("view_imagenes", "Can view Imagen"),
            )
