from django.urls import path

from api import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("create/", views.create_url, name="create"),
    path("s/<str:url>/", views.redirect_to_original_url, name="redirect"),
]
