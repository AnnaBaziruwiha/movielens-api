import hashlib
import os
import re
import zipfile
from typing import Optional

import pandas as pd
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from mldb.models import Genre, Movie, Tag


class Command(BaseCommand):
    """Handles downloading, verifying, extracting, and loading the Movielens 20M dataset into the database."""

    help = "Downloads the Movielens 20M dataset, verifies it, and loads it into the database."

    def handle(self, *args, **kwargs) -> None:
        """Entry point for the command."""
        self.stdout.write("Starting to download the Movielens 20M dataset...")

        # Define URLs and paths
        dataset_url = "https://files.grouplens.org/datasets/movielens/ml-20m.zip"
        checksum_url = "https://files.grouplens.org/datasets/movielens/ml-20m.zip.md5"
        dataset_path = os.path.join(settings.BASE_DIR, "ml-20m.zip")
        checksum_path = os.path.join(settings.BASE_DIR, "ml-20m.zip.md5")

        # Download dataset and checksum
        self.download_file(dataset_url, dataset_path)
        self.download_file(checksum_url, checksum_path)

        # Verify checksum
        if not self.verify_checksum(dataset_path, checksum_path):
            self.stdout.write(self.style.ERROR("Checksum verification failed."))
            return

        self.stdout.write("Checksum verified successfully.")

        # Extract and load data
        self.extract_and_load_data(dataset_path)

    def download_file(self, url: str, path: str) -> None:
        """
        Downloads a file from a given URL and saves it to a specified path.

        Args:
            url: The URL of the file to download.
            path: The local path to save the downloaded file.
        """
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            self.stdout.write(self.style.SUCCESS(f"Successfully downloaded {url} to {path}"))
        except requests.exceptions.HTTPError as err:
            self.stdout.write(self.style.ERROR(f"HTTP Error: {err}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error downloading the file: {e}"))

    @staticmethod
    def calculate_md5(file_path: str) -> str:
        """
        Calculates the MD5 checksum of a file.

        Args:
            file_path: The path to the file for which to calculate the checksum.

        Returns:
            The MD5 checksum as a hexadecimal string.
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def extract_md5(content: str) -> Optional[str]:
        """
        Extracts the MD5 checksum from a string using a regular expression.

        Args:
            content: The string containing the MD5 checksum.

        Returns:
            The extracted MD5 checksum as a string, or None if not found.
        """
        match = re.search(r"([a-fA-F\d]{32})", content)
        return match.group(0) if match else None

    def verify_checksum(self, dataset_path: str, checksum_path: str) -> bool:
        """
        Verifies the MD5 checksum of the downloaded file against the expected checksum.

        Args:
            dataset_path: The path to the downloaded dataset file.
            checksum_path: The path to the file containing the expected MD5 checksum.

        Returns:
            True if the checksums match, False otherwise.
        """
        try:
            dataset_checksum = self.calculate_md5(dataset_path)
            with open(checksum_path, "r") as f:
                md5_file_content = f.read().strip().lower()

            expected_checksum = self.extract_md5(md5_file_content)

            if dataset_checksum == expected_checksum:
                return True
            else:
                self.stdout.write(
                    self.style.ERROR(f"Checksum mismatch: expected {expected_checksum}, got {dataset_checksum}")
                )
                return False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error verifying checksum: {e}"))
            return False

    def extract_and_load_data(self, dataset_path: str) -> None:
        """
        Extracts the ZIP file and loads data into the database.

        Args:
            dataset_path: The path to the dataset ZIP file.
        """
        extract_path = os.path.join(settings.BASE_DIR, "ml-20m")
        with zipfile.ZipFile(dataset_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        movies_path = os.path.join(extract_path, "ml-20m", "movies.csv")
        ratings_path = os.path.join(extract_path, "ml-20m", "ratings.csv")
        tags_path = os.path.join(extract_path, "ml-20m", "tags.csv")

        self.populate_genres(movies_path)
        self.populate_movies(movies_path, ratings_path)
        self.populate_tags(tags_path)

    def populate_genres(self, movies_path: str) -> None:
        """
        Populates genres data into the database from the movies CSV file.

        Args:
            movies_path: The path to the movies CSV file.
        """
        self.stdout.write("Loading genres data...")
        df_movies = pd.read_csv(movies_path)
        genres = set(df_movies["genres"].str.split("|").explode().unique())
        Genre.objects.bulk_create(
            [Genre(name=genre) for genre in genres if genre != "(no genres listed)"], ignore_conflicts=True
        )
        self.stdout.write(self.style.SUCCESS("Successfully populated genres."))

    @transaction.atomic
    def populate_movies(self, movies_path: str, ratings_path: str) -> None:
        """
        Loads movie data from CSV files into the database.

        Args:
            movies_path: The path to the movies CSV file.
            ratings_path: The path to the ratings CSV file.
        """
        df_movies = pd.read_csv(movies_path)
        df_ratings = pd.read_csv(ratings_path)

        # Calculating average rating
        avg_ratings = df_ratings.groupby("movieId")["rating"].mean().reset_index()

        for _, row in df_movies.iterrows():
            movie_genres = row["genres"].split("|")
            avg_rating = avg_ratings[avg_ratings["movieId"] == row["movieId"]]["rating"]
            avg_rating_value = 5.0 if avg_rating.empty else avg_rating.iloc[0]

            movie, created = Movie.objects.get_or_create(
                id=row["movieId"],
                defaults={
                    "title": row["title"],
                    "rating": avg_rating_value,
                },
            )

            # Linking genres
            genre_objs = Genre.objects.filter(name__in=movie_genres)
            movie.genres.set(genre_objs)

        self.stdout.write(self.style.SUCCESS("Successfully populated movies and calculated ratings."))

    @transaction.atomic
    def populate_tags(self, tags_path: str) -> None:
        """
        Populates tags data into the database from the movies CSV file.

        Args:
            tags_path: The path to the tags CSV file.
        """
        df_tags = pd.read_csv(tags_path)
        Tag.objects.all().delete()
        for _, row in df_tags.iterrows():
            tag, _ = Tag.objects.get_or_create(name=row["tag"])
            movie = Movie.objects.get(id=row["movieId"])
            movie.tags.add(tag)

        self.stdout.write(self.style.SUCCESS("Successfully populated tags."))
