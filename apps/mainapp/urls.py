from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, BookViewSet, UserViewSet, ConfirmEmailViewSet

router = DefaultRouter()
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'books', BookViewSet, basename='book')
router.register('user', views.UserViewSet, basename='user')

urlpatterns = [
        path('confirm-email/<str:uidb64>/<str:token>/', views.ConfirmEmailViewSet.as_view(), name='confirm-email'),
]

urlpatterns = router.urls