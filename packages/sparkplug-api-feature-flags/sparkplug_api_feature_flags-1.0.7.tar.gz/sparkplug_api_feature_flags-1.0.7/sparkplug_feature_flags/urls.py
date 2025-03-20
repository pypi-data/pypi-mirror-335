# django
from django.urls import (
    include,
    path,
)

# contrib
from rest_framework.routers import SimpleRouter

# app
from . import views


router = SimpleRouter()


router.register(
    prefix=r"feature-flags/admin/search",
    viewset=views.AdminSearch,
    basename="feature-flags-admin-search",
)


router.register(
    prefix=r"feature-flags/admin",
    viewset=views.Admin,
    basename="feature-flags-admin",
)


router.register(
    prefix=r"feature-flags",
    viewset=views.FeatureFlag,
    basename="feature-flags",
)


urlpatterns = [
    path(
        "",
        include(router.urls),
    ),
]
