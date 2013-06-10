# coding: utf-8
from django.conf import settings
from django.db import models
from django.db.models import CharField
from django.db.models import Field
from django.forms.fields import MultiValueField
from django import forms
from django.forms.widgets import Input, HiddenInput
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
import pickle

class IMGBrowserWidget(Input):
    input_type = 'hidden'

    def __init__(self, attrs=None):
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            self.attrs = {}

    def render(self, name, value, attrs=None):
        if value is None:
            value = ""
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        return render_to_string("django_imgbrowser/imgbrowserfield.html", 
                                {'MEDIA_URL':settings.MEDIA_URL,
                                 'popup_url': reverse('imgbrowser_list'),
                                 'final_attrs':final_attrs,
                                 'value':value})

    class Media:
        js = (u"%sjs/imgbrowser.js"%settings.STATIC_URL, )

class IMGBrowserFormField(forms.CharField):
    widget = IMGBrowserWidget
    def __init__(self, *args, **kwargs):
        super(IMGBrowserFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(IMGBrowserFormField, self).clean(value)
        return value

class IMGBrowserField(Field):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 666
        return super(IMGBrowserField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

    def clean(self, value):
        if not value:
            value = ""
        return value

    def formfield(self, **kwargs):
        attrs = {}
        defaults = {
            'form_class': IMGBrowserFormField,
            'widget': IMGBrowserWidget(attrs=attrs),
        }
        defaults.update(kwargs)
        return super(IMGBrowserField, self).formfield(**defaults)


class IMGBrowserWithIDWidget(forms.widgets.MultiWidget):
    def __init__(self, attrs=None):
        widgets = [IMGBrowserWidget(),
                   forms.HiddenInput()]
        super(IMGBrowserWithIDWidget, self).__init__(widgets, attrs)
 
    def decompress(self, value):
        if value:
            return pickle.loads(value)
        else:
            return ['', '']

class IMGBrowserWithIDField(forms.fields.MultiValueField):
    widget = IMGBrowserWithIDWidget
 
    def __init__(self, *args, **kwargs):
        list_fields = [IMGBrowserField(),
                       forms.fields.CharField(max_length=10)]
                       #models.ForeignKey(Imagenes)]
        super(IMGBrowserWithIDField, self).__init__(list_fields, *args, **kwargs)

    def compress(self, values):
        return pickle.dumps(values)
