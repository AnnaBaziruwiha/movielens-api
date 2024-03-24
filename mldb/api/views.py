from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, views
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from mldb.models import Movie

from .pagination import StandardResultsSetPagination
from .serializers import MovieSerializer, UserRatingSerializer


class MovieRatingView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, movie_id):
        serializer = UserRatingSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            # Check if the movie exists
            if not Movie.objects.filter(id=movie_id).exists():
                return Response({"detail": "Movie not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer.validated_data["movie_id"] = movie_id
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MovieListCreateView(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["tags__name", "genres__name"]
    ordering_fields = ["title"]


class MovieDetailUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticated]
