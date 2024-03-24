from django.urls import path

from .views import MovieDetailUpdateView, MovieListCreateView, MovieRatingView

urlpatterns = [
    path("movies/", MovieListCreateView.as_view(), name="movie-list-create"),
    path("movies/<int:pk>/", MovieDetailUpdateView.as_view(), name="movie-detail-update"),
    path("movies/<int:movie_id>/rate/", MovieRatingView.as_view(), name="movie-rate"),
]
