import secrets
import string

from url_compresion.models import ShortUrl

ALPHABET = string.ascii_letters + string.digits
DEFAULT_CODE_LENGTH = 12


def generate_code(length: int = DEFAULT_CODE_LENGTH) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def create_short_url(url: str) -> ShortUrl:
    code = generate_code()
    return ShortUrl.objects.create(url=url, code=code)
