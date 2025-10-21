from django.urls import path
from . import views
from .views import *
urlpatterns =[
 #path("liste/", views.list_conferences, name="liste_conferences"),
    path("liste/",ConferenceList.as_view(),name="liste_conferences"),
    path("<int:pk>/",ConferenceDetails.as_view(),name="conference_details"),
    path("add/",ConferenceCreate.as_view(),name="conference_add")
]