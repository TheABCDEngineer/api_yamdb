from django.shortcuts import get_object_or_404
from rest_framework import serializers

from titles.models import Comment, Review, Title


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = (
            'id',
            'text',
            'author',
            'pub_date'
        )
        read_only_fields = (
            'id',
            'author',
            'review'
            'pub_date'
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def validate(self, attrs):
        author = self.context['request'].user
        title = get_object_or_404(
            Title,
            pk=self.context['kwargs']['title_id']
        )
        try:
            _ = author.reviews.get(title=title)
            raise serializers.ValidationError(
                'Нельзя оставить более одного отзыва на произведение'
            )
        except Review.DoesNotExist:
            return super().validate(attrs)

    class Meta:
        model = Review
        fields = (
            'id',
            'text',
            'author',
            'score'
            'pub_date'
        )
        read_only_fields = (
            'id',
            'author',
            'title'
            'pub_date'
        )


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = 'name, rating'
        read_only_fields = 'rating'

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.count() == 0:
            return 0

        summary_score = 0
        for review in reviews:
            summary_score += review.score

        return round(
            summary_score / reviews.count()
        )
