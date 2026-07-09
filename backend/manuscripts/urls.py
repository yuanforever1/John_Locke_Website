from rest_framework.routers import DefaultRouter

from .views import CollectionViewSet, ManuscriptPageViewSet

router = DefaultRouter()
router.register("collections", CollectionViewSet, basename="collection")
router.register("pages", ManuscriptPageViewSet, basename="page")

urlpatterns = router.urls
