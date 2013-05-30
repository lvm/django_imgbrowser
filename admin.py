from django.contrib import admin
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from models import Directorios
from models import Imagenes

class ImagenesAdmin(admin.ModelAdmin):
    def add_view(self, request, form_url='', extra_context=None):
        return HttpResponseRedirect(reverse('imgbrowser_upload'))

    def change_view(self, request, obj_id, form_url='', extra_context=None):
        return HttpResponseRedirect(reverse('imgbrowser_upload',
                                            kwargs={'obj_id':obj_id}))

    def changelist_view(self, request, extra_context=None):
        return HttpResponseRedirect(reverse('imgbrowser_list'))

    def has_view_permission(self, request):
        return request.user.has_perm('django_imgbrowser.view_imagenes')

    def has_add_permission(self, request):
        return request.user.has_perm('django_imgbrowser.add_imagenes')

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('django_imgbrowser.change_imagenes')

    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm('django_imgbrowser.delete_imagenes')

class DirectoriosAdmin(admin.ModelAdmin):
    def add_view(self, request, form_url='', extra_context=None):
        return HttpResponseRedirect(reverse('imgbrowser_mkdir'))

    def change_view(self, request, obj_id, form_url='', extra_context=None):
        return HttpResponseRedirect(reverse('imgbrowser_mkdir',
                                            kwargs={'obj_id':obj_id}))

    def changelist_view(self, request, extra_context=None):
        return HttpResponseRedirect(reverse('imgbrowser_list'))

    def has_view_permission(self, request):
        return request.user.has_perm('django_imgbrowser.view_directorios')

    def has_add_permission(self, request):
        return request.user.has_perm('django_imgbrowser.add_directorios')

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('django_imgbrowser.change_directorios')

    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm('django_imgbrowser.delete_directorios')


admin.site.register(Imagenes, ImagenesAdmin)
admin.site.register(Directorios, DirectoriosAdmin)


