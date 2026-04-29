from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from url_compresion.models import ShortUrl
from url_compresion.serializers import ShortenUrlInputSerializer


class ShortenUrlView(APIView):
    def post(self, request: Request) -> Response:
        serializer = ShortenUrlInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        short_url = serializer.save()

        return Response(
            {
                "url": short_url.url,
                "code": short_url.code,
                "short_url": request.build_absolute_uri(f"/shrt/{short_url.code}/"),
            },
            status=status.HTTP_201_CREATED,
        )


class ExpandShortUrlView(APIView):
    def get(self, code: str) -> Response:
        short_url = get_object_or_404(ShortUrl, code=code)
        return Response({"url": short_url.url})
