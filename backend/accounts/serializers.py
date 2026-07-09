from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(
        source="user.email", required=False, allow_blank=True
    )
    date_joined = serializers.DateTimeField(source="user.date_joined", read_only=True)
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "username",
            "email",
            "nickname",
            "avatar",
            "bio",
            "affiliation",
            "date_joined",
            "updated_at",
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        email = user_data.get("email")
        if email is not None:
            instance.user.email = email
            instance.user.save(update_fields=["email"])
        return super().update(instance, validated_data)


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["avatar"]


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    nickname = serializers.CharField(max_length=60, required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("该用户名已被注册。")
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("该邮箱已被注册。")
        return value

    def create(self, validated_data):
        nickname = validated_data.pop("nickname", "")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        # 档案由信号自动创建，这里补充昵称。
        profile = user.profile
        profile.nickname = nickname or validated_data["username"]
        profile.save(update_fields=["nickname"])
        return user
