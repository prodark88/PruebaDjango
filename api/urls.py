from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.view.CustomersView import CustomerViewSet

router = DefaultRouter()
router.register(r'clientes', CustomerViewSet, basename='clientes')

urlpatterns = [
    path('', include(router.urls)),
]