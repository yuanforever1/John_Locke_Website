from pathlib import Path

from rest_framework import parsers, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .agnes import AgnesAPIError, AgnesConfigError, transcribe_image
from .models import Folder, Recognition, UserImage
from .serializers import (
    FolderSerializer,
    RecognitionSerializer,
    UserImageSerializer,
)


class FolderViewSet(viewsets.ModelViewSet):
    """当前用户工作区的文件夹增删改查。"""

    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Folder.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserImageViewSet(viewsets.ModelViewSet):
    """工作区图片：上传、列出、删除，以及识别。"""

    serializer_class = UserImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        qs = UserImage.objects.filter(owner=self.request.user).select_related(
            "recognition"
        )
        folder = self.request.query_params.get("folder")
        if folder == "root":
            qs = qs.filter(folder__isnull=True)
        elif folder:
            qs = qs.filter(folder_id=folder)
        return qs

    def create(self, request, *args, **kwargs):
        """支持一次上传多张图片。"""
        files = request.FILES.getlist("images") or request.FILES.getlist("image")
        if not files:
            return Response(
                {"detail": "未收到任何图片文件。"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        folder = None
        folder_id = request.data.get("folder")
        if folder_id:
            folder = Folder.objects.filter(
                id=folder_id, owner=request.user
            ).first()
            if folder is None:
                return Response(
                    {"detail": "目标文件夹不存在。"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        created = []
        for f in files:
            obj = UserImage.objects.create(
                owner=request.user,
                folder=folder,
                image=f,
                original_name=f.name,
                size=f.size,
            )
            created.append(obj)

        serializer = self.get_serializer(created, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def recognize(self, request, pk=None):
        image = self.get_object()
        result = self._run_recognition(image)
        return Response(result)

    @action(detail=False, methods=["post"])
    def batch_recognize(self, request):
        ids = request.data.get("ids") or []
        images = self.get_queryset().filter(id__in=ids)
        results = []
        for image in images:
            results.append(
                {
                    "id": image.id,
                    "recognition": self._run_recognition(image),
                }
            )
        return Response({"results": results})

    def _run_recognition(self, image: UserImage):
        recognition, _ = Recognition.objects.get_or_create(image=image)
        recognition.status = Recognition.Status.PROCESSING
        recognition.error = ""
        recognition.save(update_fields=["status", "error", "updated_at"])

        from django.conf import settings

        try:
            text = transcribe_image(Path(image.image.path))
            recognition.text = text
            recognition.model_name = settings.AGNES_MODEL
            recognition.status = Recognition.Status.DONE
        except (AgnesConfigError, AgnesAPIError) as exc:
            recognition.status = Recognition.Status.FAILED
            recognition.error = str(exc)
        recognition.save()
        return RecognitionSerializer(recognition).data
