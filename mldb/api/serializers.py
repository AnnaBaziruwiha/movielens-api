from django.contrib.auth import get_user_model
from rest_framework import exceptions, serializers

from mldb.models import Genre, Movie, Tag, UserRating

User = get_user_model()


class UserRatingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    movie_id = serializers.IntegerField()

    class Meta:
        model = UserRating
        fields = ["id", "user", "movie_id", "rating"]

    def validate_movie_id(self, value):
        if Movie.objects.filter(id=value).exists():
            return value
        raise serializers.ValidationError("Movie with this ID does not exist.")

    def create(self, validated_data):
        user = self.context["request"].user
        movie_id = validated_data.get("movie_id")
        rating = validated_data.get("rating")

        if UserRating.objects.filter(user=user, movie_id=movie_id).exists():
            raise exceptions.ValidationError("You have already rated this movie.")

        movie = Movie.objects.get(id=movie_id)
        user_rating = UserRating.objects.create(user=user, movie=movie, rating=rating)
        return user_rating


class MovieSerializer(serializers.ModelSerializer):
    genres = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Genre.objects.all())
    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    class Meta:
        model = Movie
        fields = ["id", "title", "genres", "tags", "rating"]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]
