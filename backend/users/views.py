from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Follow, MyUser
from .serializers import SubscriptionSerializer


class LimitSizePagination(PageNumberPagination):
    '''класс для создания кастомной пагинации с параметром limit'''
    page_size_query_param = 'limit'


class MyUserViewSet(UserViewSet):
    '''
    класс переопределяет ViewSet из библиотеки Djoser
    для создания необходимых action
    '''
    pagination_class = LimitSizePagination

    @action(detail=False)
    def subscriptions(self, request):
        '''метод для  получения списка подписок текущего пользователя'''
        page = self.paginate_queryset(
            MyUser.objects.filter(
                following__user=self.request.user
            ).all().order_by('id')
        )
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get', 'delete'])
    def subscribe(self, request, id=None):
        '''метод для создания/удаления подписки на пользователя'''
        following = self.get_object()
        user = self.request.user
        if self.request.method == 'GET':
            Follow.objects.create(
                following=following,
                user=user,
            )
            serializer = SubscriptionSerializer(
                following,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        Follow.objects.filter(
            following=following,
            user=user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
