from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UsersViewSet,
                    get_token_for_user, signup)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('users', UsersViewSet, basename='users')

router_v1.register(
    r'titles/(?P<title_id>.+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>.+)/reviews/(?P<review_id>.+)/comments',
    CommentViewSet,
    basename='comments')


urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/token/', get_token_for_user, name='token'),
    path('auth/signup/', signup, name='signup'),
]
