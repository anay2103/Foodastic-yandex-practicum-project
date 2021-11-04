from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from users.models import MyUser


class Ingredient(models.Model):
    name = models.CharField(
        max_length=250,
        verbose_name='Название',
        unique=True,
    )
    measurement_unit = models.CharField(
        max_length=250,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'),
        ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название',
        unique=True,
    )
    color = ColorField(
        default='#FF0000',
        verbose_name='Цвет',
        unique=True,
    )
    slug = models.SlugField(
        unique=True
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        MyUser,
        on_delete=models.SET_NULL,
        related_name='recipes',
        null=True
    )
    name = models.CharField(
        max_length=250,
        verbose_name='Название',
        unique=True,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        unique=True,
    )
    is_favorite = models.ManyToManyField(
        MyUser,
        related_name='is_favorite'
    )
    is_in_shopping_cart = models.ManyToManyField(
        MyUser,
        related_name='is_in_shopping_cart'
    )
    text = models.TextField(
        verbose_name='Описание',
        unique=True,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='Recipe_Ingredient',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes'
    )
    cooking_time = models.IntegerField(
        verbose_name='время приготовления',
        validators=[MinValueValidator(
            1,
            message='время приготовления должно быть больше нуля')]
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
    )
    amount = models.FloatField(
        verbose_name='количество',
        validators=[MinValueValidator(
            0.01,
            message='количество ингредиента должно быть больше нуля')]
    )

    class Meta:
        ordering = ['id']
