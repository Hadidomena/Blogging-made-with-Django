from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    author = UserSerializer(read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'author', 'author_username', 'content', 
            'created_at', 'is_approved', 'parent'
        ]
        read_only_fields = ['id', 'created_at', 'author']
        
    def create(self, validated_data):
        # Set the author to the current user
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post model with comments"""
    author = UserSerializer(read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author', 'author_username',
            'created_at', 'updated_at', 'comments', 'comment_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'author']
        
    def create(self, validated_data):
        # Set the author to the current user
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class PostListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for post lists (without comments)"""
    author_username = serializers.CharField(source='author.username', read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author_username',
            'created_at', 'updated_at', 'comment_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
        
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user