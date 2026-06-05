from django.urls import include, path
from rest_framework import routers

from .views import GenreViewSet, CategoryViewSet, TitleViewSet

router = routers.DefaultRouter()
router.register('genres', GenreViewSet)
router.register('categories', CategoryViewSet)
router.register('titles', TitleViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
]
