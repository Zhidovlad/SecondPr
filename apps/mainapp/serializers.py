from rest_framework import serializers
from .models import Author, Book, User


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    class Meta:
        model = Book
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 'birth_date', 'age')
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
            'age': {'read_only': True}
        }
