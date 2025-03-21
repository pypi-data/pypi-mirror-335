from .client import Phrappy
from .async_client import AsyncPhrappy
import urllib.parse

def cdh_generator(filename: str) -> str:
    """
    Takes UTF-8 filename. Returns Content Disposition value.
    """
    encoded_file_name = urllib.parse.quote(filename, encoding="utf-8")
    return f"attachment; filename*=UTF-8''{encoded_file_name}"

__version__ = "0.0.1"
__all__ = [Phrappy, AsyncPhrappy]
