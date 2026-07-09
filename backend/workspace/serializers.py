from rest_framework import serializers

from .models import Folder, Recognition, UserImage


class RecognitionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = Recognition
        fields = [
            "status",
            "status_display",
            "text",
            "model_name",
            "error",
            "updated_at",
        ]


class UserImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    recognition = RecognitionSerializer(read_only=True)

    class Meta:
        model = UserImage
        fields = [
            "id",
            "folder",
            "image",
            "original_name",
            "size",
            "uploaded_at",
            "recognition",
        ]
        read_only_fields = ["size", "original_name"]

    def get_image(self, obj):
        request = self.context.get("request")
        url = obj.image.url if obj.image else ""
        return request.build_absolute_uri(url) if request and url else url


class FolderSerializer(serializers.ModelSerializer):
    image_count = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = ["id", "name", "parent", "created_at", "image_count"]

    def get_image_count(self, obj):
        return obj.images.count()

    def validate(self, attrs):
        request = self.context["request"]
        parent = attrs.get("parent")
        if parent and parent.owner_id != request.user.id:
            raise serializers.ValidationError("父文件夹不属于当前用户。")
        return attrs
