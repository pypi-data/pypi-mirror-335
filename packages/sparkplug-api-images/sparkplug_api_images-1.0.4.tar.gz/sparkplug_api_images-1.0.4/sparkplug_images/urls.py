# django
from django.urls import include, path

# contrib
from rest_framework.routers import SimpleRouter

# app
from . import views


router = SimpleRouter()


router.register(
    prefix=r"images",
    viewset=views.Image,
    basename="images",
)


urlpatterns = [
    path(
        "",
        include(router.urls),
    ),
]
