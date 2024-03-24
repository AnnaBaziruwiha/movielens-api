import csv

from django.core.management.base import BaseCommand, CommandParser

from mldb.models import Movie


class Command(BaseCommand):
    """Exports movies list to a CSV file."""

    help = "Exports movies list to a CSV file"

    def add_arguments(self, parser: CommandParser) -> None:
        """
        Adds arguments to the command.

        Args:
            parser: The command line argument parser instance.
        """
        parser.add_argument("output_file", type=str, help="The CSV file to write movies to")

    def handle(self, *args, **options) -> None:
        """
        The main entry point for the command execution.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments.
        """
        output_file_path = options["output_file"]
        self.export_movies_to_csv(output_file_path)

    def export_movies_to_csv(self, file_path: str) -> None:
        """
        Exports movie data from the database to a CSV file.

        Args:
            file_path: The path to the output CSV file.
        """
        # Query the database for movies with related genres and tags
        movies = Movie.objects.all().prefetch_related("genres", "tags")

        # Define the CSV file's headers
        headers = ["Movie ID", "Title", "Rating", "Genres", "Tags"]

        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)

            for movie in movies:
                # Extract genres and tags as comma-separated strings
                genres = ", ".join([genre.name for genre in movie.genres.all()])
                tags = ", ".join([tag.name for tag in movie.tags.all()])

                # Write the movie data to the CSV file
                writer.writerow([movie.id, movie.title, movie.rating, genres, tags])

        self.stdout.write(self.style.SUCCESS(f"Successfully exported movies to {file_path}"))
