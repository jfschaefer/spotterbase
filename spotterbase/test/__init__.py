import io
from typing import IO

from spotterbase.corpora.interface import Document
from spotterbase.rdf import Uri


class InMemoryDocument(Document):
    def __init__(self, uri: Uri, content: bytes):
        self._uri: Uri = uri
        self._content: bytes = content

    def get_uri(self) -> Uri:
        return self._uri

    def open_binary(self) -> IO[bytes]:
        return io.BytesIO(self._content)
