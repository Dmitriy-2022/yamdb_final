import re

from rest_framework import mixins, viewsets, filters, serializers


class CreateDestroyList(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class MeValidator(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    USERNAME_ME = 'Нельзя использовать "me" в качестве username'
    USERNAME_EMPTY = 'Поле "username" не должно быть пустым'

    def validate_username(self, value):
        if value == 'me' or '':
            invalid_username = self.USERNAME_ME if (
                value == 'me') else self.USERNAME_EMPTY
            raise serializers.ValidationError(detail=[invalid_username])
        result = re.findall(r'[^\w.@+-]', value)
        if result:
            raise serializers.ValidationError(
                f'Некорректные символы в username:'
                f' `{"`, `".join(set(result))}`.'
            )
        return value
