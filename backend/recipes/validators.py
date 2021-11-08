from rest_framework.exceptions import ParseError
from rest_framework.serializers import ValidationError


class RecipeCreateValidator:

    def check_duplicates(self, field, field_name):
        if len(field) != len(set(field)):
            self.errors.append({
                field_name: 'duplicate values not allowed'
            })

    def check_negatives(self, field, field_name):
        if (isinstance(field, int) and field < 0
                or any([value < 0 for value in field])):
            self.errors.append({
                field_name: 'negative values not allowed'
            })

    def __call__(self, value):
        self.errors = []
        try:
            ingredients = [dict(ingredient)
                           for ingredient in value.pop('recipe')]
            self.check_duplicates([
                elem['ingredient']['id'] for elem in ingredients
            ], 'ingredients')
            self.check_duplicates(value.pop('tags'), 'tags')
            self.check_negatives([
                elem['amount'] for elem in ingredients
            ], 'amount')
            self.check_negatives(value.pop('cooking_time'), 'cooking_time')
        except KeyError as error:
            raise ParseError(f'failed to parse the request: {error}')
        if self.errors:
            raise ValidationError(self.errors)
        return value
