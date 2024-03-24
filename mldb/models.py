from django.conf import settings
from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=255)
    genres = models.ManyToManyField("Genre", related_name="movie_genres")
    tags = models.ManyToManyField("Tag", related_name="movie_tags")
    rating = models.DecimalField(max_digits=5, decimal_places=1, default=5.0)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title


class UserRating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ("movie", "user")

    def __str__(self):
        return f"{self.user} rated {self.movie} as {self.rating}"


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    movies = models.ManyToManyField(Movie, related_name="movie_genres")

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    movies = models.ManyToManyField(Movie, related_name="movie_tags")

    def __str__(self):
        return self.name
