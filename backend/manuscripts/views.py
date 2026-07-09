from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Collection, ManuscriptPage
from .serializers import (
    CollectionSerializer,
    ManuscriptPageDetailSerializer,
    ManuscriptPageListSerializer,
)


class CollectionViewSet(viewsets.ReadOnlyModelViewSet):
    """系统手稿集浏览（只读，登录用户可访问）。"""

    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "slug"

    @action(detail=True, methods=["get"])
    def pages(self, request, slug=None):
        collection = self.get_object()
        qs = collection.pages.all()
        search = request.query_params.get("search")
        if search:
            qs = qs.filter(transcription__icontains=search)
        page = self.paginate_queryset(qs)
        serializer = ManuscriptPageListSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class ManuscriptPageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ManuscriptPage.objects.select_related("collection").all()
    serializer_class = ManuscriptPageDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
