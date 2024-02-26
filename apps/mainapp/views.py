from django.shortcuts import render
from .serializers import AuthorSerializer, BookSerializer, UserSerializer

from .models import Author, Book, User
from rest_framework.viewsets import ModelViewSet
from .permissions import IsAuthorOrReadOnly

from django_filters.rest_framework import FilterSet, DjangoFilterBackend, DateFilter
from rest_framework import viewsets, filters, pagination

from rest_framework.status import HTTP_400_BAD_REQUEST

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

from rest_framework.views import APIView
from rest_framework.response import Response


class AuthorViewSet(ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class AuthorPagination(pagination.PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

class AuthorFilter(FilterSet):
    start_date = DateFilter(field_name="created_at", lookup_expr='gte')
    end_date = DateFilter(field_name="created_at", lookup_expr='lte')

    class Meta:
        model = Author
        fields = ['start_date', 'end_date']


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookPagination(pagination.PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

class BookFilter(FilterSet):
    start_date = DateFilter(field_name="created_at", lookup_expr='gte')
    end_date = DateFilter(field_name="created_at", lookup_expr='lte')

    class Meta:
        model = Book
        fields = ['start_date', 'end_date']

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        # регистрации пользователя
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Создание токена и ссылки для подтверждения
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        confirmation_link = self.request.build_absolute_uri(
            reverse('confirm-email', kwargs={'uidb64': uid, 'token': token})
        )

        # Отправка письма с ссылкой для подтверждения
        email_subject = 'Подтверждение регистрации'
        email_message = render_to_string('registration_confirmation_email.html', {
            'user': user,
            'confirmation_link': confirmation_link,
            })
        print(email_message)
        send_mail(email_subject, email_message, settings.DEFAULT_FROM_EMAIL, 
                  [user.email], html_message=email_message)

        return Response({'detail': 'Подтверждения  Email отправлена на почту!'})



class ConfirmEmailViewSet(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError):
            return Response({'detail': 'Invalid confirmation link.'}, status=HTTP_400_BAD_REQUEST)

        if user and default_token_generator.check_token(user, token):
            user.email_confirmed = True
            user.save()
            return Response({'detail': 'Email successfully confirmed!'})
        else:
            return Response({'detail': 'Invalid confirmation token.'}, status=HTTP_400_BAD_REQUEST)