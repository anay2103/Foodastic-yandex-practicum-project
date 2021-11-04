from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MyUserViewSet

router_v1 = DefaultRouter()
router_v1.register('users', MyUserViewSet, basename='User')

urlpatterns = [
    path('', include(router_v1.urls)),
]
