# Generated by Django 5.0.7 on 2024-08-06 14:40

import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FilmWork",
            fields=[
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="title")),
                (
                    "description",
                    models.TextField(blank=True, null=True, verbose_name="description"),
                ),
                (
                    "creation_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="creation date"
                    ),
                ),
                (
                    "rating",
                    models.FloatField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1.0),
                            django.core.validators.MaxValueValidator(10.0),
                        ],
                        verbose_name="rating",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("movie", "movie"), ("tv show", "tv show")],
                        default="movie",
                        max_length=7,
                        verbose_name="type",
                    ),
                ),
            ],
            options={
                "verbose_name": "film",
                "verbose_name_plural": "films",
                "ordering": ["-creation_date"],
            },
        ),
        migrations.CreateModel(
            name="Genre",
            fields=[
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="genre")),
                (
                    "description",
                    models.TextField(blank=True, null=True, verbose_name="description"),
                ),
            ],
            options={
                "verbose_name": "genre",
                "verbose_name_plural": "genres",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Person",
            fields=[
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("full_name", models.CharField(max_length=255, verbose_name="name")),
            ],
            options={
                "verbose_name": "person",
                "verbose_name_plural": "persons",
            },
        ),
        migrations.CreateModel(
            name="GenreFilmWork",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "film_work",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="movies.filmwork",
                    ),
                ),
                (
                    "genre",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="movies.genre",
                        verbose_name="genre",
                    ),
                ),
            ],
            options={
                "verbose_name": "genre",
                "verbose_name_plural": "film genres",
            },
        ),
        migrations.AddField(
            model_name="filmwork",
            name="genres",
            field=models.ManyToManyField(
                through="movies.GenreFilmWork", to="movies.genre", verbose_name="genres"
            ),
        ),
        migrations.CreateModel(
            name="PersonFilmWork",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("actor", "actor"),
                            ("director", "director"),
                            ("writer", "writer"),
                        ],
                        default="actor",
                        max_length=10,
                        verbose_name="role",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "film_work",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="person_film_work",
                        to="movies.filmwork",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="person_film_work",
                        to="movies.person",
                        verbose_name="person",
                    ),
                ),
            ],
            options={
                "verbose_name": "person",
                "verbose_name_plural": "film persons",
            },
        ),
        migrations.AddField(
            model_name="filmwork",
            name="persons",
            field=models.ManyToManyField(
                through="movies.PersonFilmWork", to="movies.person"
            ),
        ),
        migrations.AddConstraint(
            model_name="genrefilmwork",
            constraint=models.UniqueConstraint(
                fields=("film_work", "genre"), name="film_work_genre_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="personfilmwork",
            constraint=models.UniqueConstraint(
                fields=("film_work", "person", "role"), name="film_work_person_role_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="filmwork",
            index=models.Index(
                fields=["creation_date", "rating"], name="film_work_creation_rating_idx"
            ),
        ),
    ]
