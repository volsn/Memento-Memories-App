from django.urls import path, include
from rest_framework.routers import DefaultRouter

from memories import views

router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('domains', views.DomainViewSet)
router.register('memories', views.MemoryViewSet)

app_name = 'memories'

urlpatterns = [
    path('', include(router.urls))
]
