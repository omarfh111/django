from rest_framework.routers import DefaultRouter
from .views import SessionViewSet
from django.urls import path,include

router=DefaultRouter()
router.register('sessions',SessionViewSet)
urlpatterns = [
    path('',include(router.urls))
]
