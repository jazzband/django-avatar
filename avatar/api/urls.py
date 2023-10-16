from rest_framework.routers import SimpleRouter

from avatar.api.views import AvatarViewSets

router = SimpleRouter()
router.register("avatar", AvatarViewSets)

urlpatterns = router.urls
