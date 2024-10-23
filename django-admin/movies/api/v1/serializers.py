from rest_framework import serializers

from movies.models import FilmWork, Person, Roles


class FilmWorkSerializer(serializers.ModelSerializer):
    genres = serializers.StringRelatedField(many=True)
    actors = serializers.SerializerMethodField()
    directors = serializers.SerializerMethodField()
    writers = serializers.SerializerMethodField()

    class Meta:
        model = FilmWork
        fields = (
            'id',
            'title',
            'description',
            'creation_date',
            'rating',
            'type',
            'genres',
            'actors',
            'directors',
            'writers'
        )

    def get_actors(self, obj):
        return Person.objects.filter(
            person_film_work__film_work=obj,
            person_film_work__role=Roles.ACTOR
        ).values_list('full_name', flat=True)

    def get_directors(self, obj):
        return Person.objects.filter(
            person_film_work__film_work=obj,
            person_film_work__role=Roles.DIRECTOR
        ).values_list('full_name', flat=True)

    def get_writers(self, obj):
        return Person.objects.filter(
            person_film_work__film_work=obj,
            person_film_work__role=Roles.WRITER
        ).values_list('full_name', flat=True)



