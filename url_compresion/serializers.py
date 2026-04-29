from rest_framework import serializers

from url_compresion.models import ShortUrl
from url_compresion.services import create_short_url


class ShortenUrlInputSerializer(serializers.Serializer):
    url = serializers.URLField(max_length=2048)

    def create(self, validated_data: dict[str, str]) -> ShortUrl:
        return create_short_url(validated_data["url"])
