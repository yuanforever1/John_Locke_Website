from rest_framework import serializers

from .models import Collection, ManuscriptPage


class CollectionSerializer(serializers.ModelSerializer):
    page_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Collection
        fields = [
            "id",
            "slug",
            "title",
            "subtitle",
            "description",
            "period",
            "language",
            "page_count",
        ]


class ManuscriptPageListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()

    class Meta:
        model = ManuscriptPage
        fields = ["id", "page_number", "image_name", "image", "excerpt"]

    def get_image(self, obj):
        request = self.context.get("request")
        url = obj.image.url if obj.image else ""
        return request.build_absolute_uri(url) if request and url else url

    def get_excerpt(self, obj):
        text = (obj.transcription or "").strip()
        return text[:160] + ("…" if len(text) > 160 else "")


class ManuscriptPageDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    collection = CollectionSerializer(read_only=True)

    class Meta:
        model = ManuscriptPage
        fields = [
            "id",
            "collection",
            "page_number",
            "image_name",
            "image",
            "transcription",
        ]

    def get_image(self, obj):
        request = self.context.get("request")
        url = obj.image.url if obj.image else ""
        return request.build_absolute_uri(url) if request and url else url
