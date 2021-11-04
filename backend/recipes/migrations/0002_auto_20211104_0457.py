# Generated by Django 3.0.5 on 2021-11-04 04:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='recipes',
                to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(
                related_name='recipes',
                through='recipes.Recipe_Ingredient',
                to='recipes.Ingredient'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='is_favorite',
            field=models.ManyToManyField(
                related_name='is_favorite',
                to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='is_in_shopping_cart',
            field=models.ManyToManyField(
                related_name='is_in_shopping_cart',
                to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(
                related_name='recipes',
                to='recipes.Tag'),
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(
                fields=(
                    'name',
                    'measurement_unit'),
                name='unique_ingredient'),
        ),
    ]
