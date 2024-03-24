from django.contrib import admin

from .models import Genre, Movie, Tag, UserRating


class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "rating")
    search_fields = ("title", "genres__name", "tags__name")
    list_filter = ("genres", "tags")


class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class UserRatingAdmin(admin.ModelAdmin):
    list_display = ("movie", "user", "rating")
    search_fields = ("movie__title", "user__username")
    list_filter = ("movie", "user")


admin.site.register(Movie, MovieAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(UserRating, UserRatingAdmin)
