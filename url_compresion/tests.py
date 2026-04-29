import json
import urllib.request
from typing import cast

from django.test import Client
from django.test import LiveServerTestCase, TestCase
from rest_framework import status

from url_compresion.models import ShortUrl
from url_compresion.services import (
    ALPHABET,
    DEFAULT_CODE_LENGTH,
    create_short_url,
    generate_code,
)

JsonData = dict[str, str]


class ShortUrlServiceTests(TestCase):
    def test_generate_code_uses_default_length_and_allowed_characters(self) -> None:
        code = generate_code()

        self.assertEqual(len(code), DEFAULT_CODE_LENGTH)
        self.assertTrue(set(code).issubset(set(ALPHABET)))

    def test_create_short_url_saves_url_and_generates_code(self) -> None:
        short_url = create_short_url("http://example.com/very/long/url")

        self.assertEqual(short_url.url, "http://example.com/very/long/url")
        self.assertEqual(len(short_url.code), DEFAULT_CODE_LENGTH)
        self.assertTrue(set(short_url.code).issubset(set(ALPHABET)))
        self.assertTrue(ShortUrl.objects.filter(code=short_url.code).exists())


class ShortUrlApiTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_shorten_url_returns_created_short_url(self) -> None:
        original_url = "http://example.com/very-very/long/url/even-longer"

        response = self.client.post(
            "/shorten/",
            data=json.dumps({"url": original_url}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        body = response.json()
        self.assertEqual(body["url"], original_url)
        self.assertEqual(len(body["code"]), DEFAULT_CODE_LENGTH)
        self.assertEqual(
            body["short_url"],
            f"http://testserver/shrt/{body['code']}/",
        )

    def test_shorten_url_rejects_invalid_url(self) -> None:
        response = self.client.post(
            "/shorten/",
            data=json.dumps({"url": "not-a-url"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ShortUrl.objects.count(), 0)

    def test_expand_short_url_returns_original_url(self) -> None:
        short_url = ShortUrl.objects.create(
            url="https://example.com/articles/123/",
            code="abc123",
        )

        response = self.client.get(f"/shrt/{short_url.code}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"url": short_url.url})

    def test_expand_short_url_returns_404_for_unknown_code(self) -> None:
        response = self.client.get("/shrt/unknown/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ShortUrlEndToEndTests(LiveServerTestCase):
    def test_create_and_expand_short_url(self) -> None:
        original_url = "http://t1.com/long/url"
        request = urllib.request.Request(
            f"{self.live_server_url}/shorten/",
            data=json.dumps({"url": original_url}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=5) as response:
            self.assertEqual(response.status, status.HTTP_201_CREATED)
            created = cast(JsonData, json.loads(response.read().decode("utf-8")))

        with urllib.request.urlopen(
            f"{self.live_server_url}/shrt/{created['code']}/",
            timeout=5,
        ) as response:
            self.assertEqual(response.status, status.HTTP_200_OK)
            expanded = cast(JsonData, json.loads(response.read().decode("utf-8")))

        self.assertEqual(created["url"], original_url)
        self.assertEqual(
            created["short_url"],
            f"{self.live_server_url}/shrt/{created['code']}/",
        )
        self.assertEqual(expanded["url"], original_url)
