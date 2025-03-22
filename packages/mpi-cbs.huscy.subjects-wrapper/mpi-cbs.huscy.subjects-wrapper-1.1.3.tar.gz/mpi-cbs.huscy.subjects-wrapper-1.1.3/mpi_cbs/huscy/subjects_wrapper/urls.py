from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import WrappedSubjectViewSet


router = DefaultRouter()
router.register('subjects', WrappedSubjectViewSet)


urlpatterns = [
    path('api/mpicbs/', include(router.urls)),
]
