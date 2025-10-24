from django.urls import path
from . import views
from .views import *
urlpatterns =[
 #path("liste/", views.list_conferences, name="liste_conferences"),
    path("register/",views.register,name="register")
]