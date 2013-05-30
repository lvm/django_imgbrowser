from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$',
        'django_imgbrowser.views.list',
        name="imgbrowser_index"),
    url(r'^list/(?P<path>((.+)/?)+)?',
        'django_imgbrowser.views.list',
        name="imgbrowser_list"),

    url(r'^mkdir/$',
        'django_imgbrowser.views.mkdir_add',
        name="imgbrowser_mkdir_add"),
    url(r'^mkdir/(?P<obj_id>\d+)$',
        'django_imgbrowser.views.mkdir_change',
        name="imgbrowser_mkdir_change"),

    url(r'^upload/$',
        'django_imgbrowser.views.upload_add',
        name="imgbrowser_upload_add"),
    url(r'^upload/(?P<obj_id>\d+)?$',
        'django_imgbrowser.views.upload_change',
        name="imgbrowser_upload_change"),

    url(r'^delete/mkdir/(?P<obj_id>\d+)$',
        'django_imgbrowser.views.delete_mkdir',
        name="imgbrowser_delete_mkdir"),
    url(r'^delete/upload/(?P<obj_id>\d+)$',
        'django_imgbrowser.views.delete_upload',
        name="imgbrowser_delete_upload"),
)
