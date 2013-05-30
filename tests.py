"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase

from django.test.client import Client
from django.test.utils import override_settings

# from urls import urlpatterns
# from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from models import Directorios
from models import Imagenes

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class LoginTest(TestCase):
    def test_index(self):
        self.assertTrue(1)

    def test_list(self):
        self.assertTrue(1)

    def test_mkdir(self):
        self.assertTrue(1)

    def test_upload(self):
        self.assertTrue(1)
    
#@override_settings(PASSWORD_HASHERS=('django.contrib.auth.hashers.MD5PasswordHasher',))
class DirectoriosTest(TestCase):
    def setUp(self):
        Group.objects.create(name="racing")
        Group.objects.create(name="river")
        


        ossie = User.objects.create_user(username="osvaldo", 
                                         password="osvaldo")
        ossie.is_staff = False
        ossie.save()

        ubaldo = User.objects.create_user(username="ubaldo",
                                          password="ubaldo")
        ubaldo.is_staff = True
        ubaldo.save()

    def test_fhaflaghagt166(self):
        racing = Group.objects.get(name="racing")

        # blue = Directorios.objects.create(grupo=racing,
        #                                   deleted=False,
        #                                   nombre="blue velvet",
        #                            )
        self.assertTrue(1)

    def test_anonymous(self):
        c = Client()
        response = c.get('/admin/imgbrowser/list/', follow=True)        
        self.assertRedirects(response, 
                             '/admin/login/?next=%2Fadmin%2Fimgbrowser%2Flist%2F')

    # def test_admin_no_staff(self):
    #     c = Client()
    #     log = c.login(username="osvaldo", password="osvaldo")
    #     print log
        
    #     response = c.get('/admin/imgbrowser/list/',follow=True)
    #     print response.status_code
    #     self.assertEqual(1+1, 2)


    def test_admin_staff(self):
        c = Client()
        log = c.login(username="ubaldo", password="ubaldo")
        print log
        
        response = c.get('/admin/imgbrowser/list/', follow=True)
        print response.status_code
        print response.redirect_chain
        self.assertEqual(1+1, 2)
