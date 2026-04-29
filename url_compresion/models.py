from django.db import models


class ShortUrl(models.Model):
    url = models.URLField(max_length=2048)
    code = models.CharField(max_length=12, unique=True, db_index=True)

    def __str__(self) -> str:
        return f"url: {self.url} code: {self.code}"
