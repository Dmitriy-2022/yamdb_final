from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitleFilter
from .mixins import CreateDestroyList
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAdminOrModeratorOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer,
                          ReviewSerializer, SignUpSerializer,
                          TitleListRetrieveSerializer, TitleSerializer,
                          UsersSerializer)
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


@permission_classes([IsAdminOrReadOnly])
class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_class = TitleFilter
    ordering_fields = ('name', 'year', 'category', 'genre', 'rating',)
    ordering = ('name',)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleListRetrieveSerializer
        return TitleSerializer


@permission_classes([IsAdminOrReadOnly])
class CategoryViewSet(CreateDestroyList):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@permission_classes([IsAdminOrReadOnly])
class GenreViewSet(CreateDestroyList):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


@permission_classes([IsAdminOrModeratorOrReadOnly])
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        serializer.save(title=self.get_title(),
                        author=self.request.user)

    def get_queryset(self):
        return self.get_title().reviews.all()


@permission_classes([IsAdminOrModeratorOrReadOnly])
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def perform_create(self, serializer):
        serializer.save(review=self.get_review(),
                        author=self.request.user)

    def get_queryset(self):
        return self.get_review().comments.all()


@permission_classes([IsAdmin])
class UsersViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(detail=False,
            methods=['patch', 'get'],
            url_path='me',
            permission_classes=[permissions.IsAuthenticated],
            )
    def me(self, request):
        user = request.user
        if request.method == 'PATCH':
            serializer = UsersSerializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=user.role)
        if request.method == 'GET':
            serializer = UsersSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
    USERNAME_ERROR = 'Такой username уже занят!'
    EMAIL_ERROR = 'Такой email уже занят!'

    try:
        user, created = User.objects.get_or_create(
            username=username, email=email)
    except IntegrityError:
        valid_error = USERNAME_ERROR if User.objects.filter(
            username=username).exists() else EMAIL_ERROR
        raise serializers.ValidationError(detail=[valid_error, ])

    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Подтверждение email',
        f'Ваш код подтверждения: {confirmation_code}',
        from_email=settings.FROM_EMAIL,
        recipient_list=[serializer.validated_data['email']],
        fail_silently=True,
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_token_for_user(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User, username=serializer.validated_data['username'])
    if default_token_generator.check_token(
            user, serializer.validated_data['confirmation_code']):
        token = AccessToken.for_user(user)
        return Response({"token": str(token)}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
