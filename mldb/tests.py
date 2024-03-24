from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from mldb.models import Genre, Movie, UserRating

User = get_user_model()


class MovieRatingViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.genre = Genre.objects.create(name="Drama")
        self.movie = Movie.objects.create(title="Test Movie", rating=5)
        self.movie.genres.add(self.genre)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_rating(self) -> None:
        url = reverse("movie-rate", kwargs={"movie_id": self.movie.id})
        data = {"movie_id": 1, "rating": 5}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserRating.objects.filter(user=self.user, movie=self.movie).exists())


class MovieListCreateViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.genre = Genre.objects.create(name="Comedy")
        self.movie = Movie.objects.create(title="Initial Movie", rating=5)
        self.movie.genres.add(self.genre)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("movie-list-create")

    def test_list_movies(self) -> None:
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results")
        self.assertEqual(len(results), 1)

    def test_create_movie(self) -> None:
        data = {"title": "New Movie", "genres": [self.genre.name], "tags": "", "rating": 4}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Movie.objects.filter(title="New Movie").exists())


class MovieDetailUpdateViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="testuser2", password="12345")
        self.genre = Genre.objects.create(name="Thriller")
        self.movie = Movie.objects.create(title="Updateable Movie", rating=3)
        self.movie.genres.add(self.genre)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("movie-detail-update", kwargs={"pk": self.movie.id})  # Updated URL name

    def test_retrieve_movie(self) -> None:
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updateable Movie")

    def test_update_movie(self) -> None:
        updated_data = {"title": "Updated Movie Title", "genres": [self.genre.name], "tags": "", "rating": 4}
        response = self.client.put(self.url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.title, "Updated Movie Title")
