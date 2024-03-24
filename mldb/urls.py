from django.urls import include, path

urlpatterns = [
    path("api/", include("mldb.api.urls")),
]
