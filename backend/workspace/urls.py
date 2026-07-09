from rest_framework.routers import DefaultRouter

from .views import FolderViewSet, UserImageViewSet

router = DefaultRouter()
router.register("folders", FolderViewSet, basename="folder")
router.register("images", UserImageViewSet, basename="image")

urlpatterns = router.urls
