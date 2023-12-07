import abc
from io import TextIOWrapper
from typing import IO, Iterable, Iterator, Optional, TextIO

from lxml.etree import _ElementTree, _Element
import lxml.etree as etree

from spotterbase.rdf.uri import Uri
from spotterbase.selectors.offset_converter import OffsetConverter
from spotterbase.selectors.selector_converter import SelectorConverter


class Document(abc.ABC):
    _html_tree: Optional[_ElementTree] = None
    _offset_converter: Optional[OffsetConverter] = None
    _selector_converter: Optional[SelectorConverter] = None
    _node_by_id: Optional[dict[str, _Element]] = None

    @abc.abstractmethod
    def get_uri(self) -> Uri:
        raise NotImplementedError()

    def open_text(self, encoding: str = 'utf-8') -> TextIO:
        return TextIOWrapper(self.open_binary(), encoding=encoding)

    @abc.abstractmethod
    def open_binary(self) -> IO[bytes]:
        raise NotImplementedError()

    def get_html_tree(self, *, cached: bool) -> _ElementTree:
        if cached and self._html_tree is not None:
            return self._html_tree
        with self.open_binary() as fp:
            # note: the choice of parser is difficult.
            # Options:
            # - HTMLParser:  has some weird bugs that are hard to re-produce
            #                (something like: if character 10000 is an & and part of an attribute value,
            #                 then the parser will silently fail and recover by making a different DOM)
            # - XMLParser:   cannot parse all documents
            # - html5parser: introduces new nodes (e.g. tbody), which breaks offsets and XPaths.
            #                Unfortunately, modern browsers do the same.
            tree: _ElementTree = etree.parse(fp, parser=etree.HTMLParser())  # type: ignore
        if cached:
            self._html_tree = tree
        return tree

    def get_node_for_id(self, node_id: str) -> _Element:
        if self._node_by_id is None:
            nodes: Iterable[_Element] = self.get_html_tree(cached=True).xpath('//*[@id]')   # type: ignore
            self._node_by_id = {node.attrib['id']: node for node in nodes}  # type: ignore
        return self._node_by_id[node_id]

    def get_offset_converter(self) -> OffsetConverter:
        if self._offset_converter is None:
            self._offset_converter = OffsetConverter(self.get_html_tree(cached=True).getroot())
        return self._offset_converter

    def get_selector_converter(self) -> SelectorConverter:
        if self._selector_converter is None:
            self._selector_converter = SelectorConverter(
                document_uri=self.get_uri(),
                dom=self.get_html_tree(cached=True).getroot(),
                offset_converter=self.get_offset_converter(),
            )
        return self._selector_converter


class DocumentNotInCorpusException(Exception):
    """ The requested document is not part of the corpus """
    pass


class DocumentNotFoundError(Exception):
    """ If the document exists, it is part of the corpus,
    but it cannot be found right now (e.g. the file does not exist). """
    pass


class CannotLocateCorpusDataError(Exception):
    """ The corpus data cannot be found (e.g. because no path was provided) """
    pass


class Corpus(abc.ABC):
    @abc.abstractmethod
    def get_uri(self) -> Uri:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_document(self, uri: Uri) -> Document:
        """ Should throw DocumentNotInCorpusException if necessary! """
        raise NotImplementedError()

    @abc.abstractmethod
    def __iter__(self) -> Iterator[Document]:
        raise NotImplementedError()

    def get_documents(self) -> Iterator[Document]:
        return iter(self)
