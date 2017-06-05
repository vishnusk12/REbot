from django.conf.urls import url, include
from django.contrib.auth.models import User
from .views import Bot
from rest_framework import routers
 
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'Response', Bot, 'GoGoCarScore')

urlpatterns = [
    url(r'^', include(router.urls)),
]