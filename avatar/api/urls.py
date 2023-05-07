from avatar.api.views import AvatarViewSets
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('avatar', AvatarViewSets)

urlpatterns = router.urls
