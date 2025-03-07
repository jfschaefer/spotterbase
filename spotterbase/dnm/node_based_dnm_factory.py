import abc
from itertools import chain, repeat
from typing import Iterable, Optional

from lxml.etree import _Element

from spotterbase.dnm.dnm import DnmMeta, DnmFactory, Dnm
from spotterbase.dnm.replacement_pattern import ReplacementPattern
from spotterbase.dnm.xml_util import get_node_classes
from spotterbase.model_core.annotation import Annotation
from spotterbase.model_core.body import ReplacedHtmlBody
from spotterbase.rdf.literal import HtmlFragment
from spotterbase.selectors.dom_range import DomRange


class NodeProcessor(abc.ABC):
    @abc.abstractmethod
    def apply(self, node: _Element, dnm_meta: DnmMeta) -> tuple[Iterable[int], Iterable[int], Iterable[str]]:
        ...


class ReplacingNP(NodeProcessor):
    def __init__(self, replacement_pattern: ReplacementPattern, category: str, number_replacements: bool = True,
                 keep_annotation: bool = True):
        self.replacement_pattern = replacement_pattern
        self.category = category
        self.number_replacements = number_replacements
        self.keep_annotation = keep_annotation

    def apply(self, node: _Element, dnm_meta: DnmMeta) -> tuple[Iterable[int], Iterable[int], Iterable[str]]:
        dom_offset_range = dnm_meta.offset_converter.convert_dom_range(DomRange.from_node(node))
        replacement: str
        number = dnm_meta.embedded_annotations.get_next_replacement_number(self.category)
        if self.number_replacements:
            replacement = self.replacement_pattern(self.category, number)
        else:
            replacement = self.replacement_pattern(self.category)

        if self.keep_annotation:
            # we need to make a copy without the tail
            import copy
            node_copy = copy.deepcopy(node)
            node_copy.tail = None

            # TODO: the following should be a bit more efficient, but it seems to remove
            #   the children from the original DOM
            # node_copy = Element(node.tag, attrib=node.attrib)    # type: ignore
            # node_copy.text = node.text
            # for child in node.getchildren():   # type: ignore
            #     node_copy.append(child)

            dnm_meta.embedded_annotations.insert(
                replacement,
                dom_offset_range,
                Annotation(
                    uri=dnm_meta.uri / f'dnm-replacement/{self.category.replace(" ", "-")}#{number}',
                    body=ReplacedHtmlBody(HtmlFragment(node_copy, wrapped_in_div=False)),
                ),
                replacement_unique=self.number_replacements,
            )

        return (
            repeat(dom_offset_range.start, len(replacement)),
            repeat(dom_offset_range.end, len(replacement)),
            [replacement]
        )


class SkippingNP(NodeProcessor):
    def apply(self, node: _Element, dnm_meta: DnmMeta) -> tuple[Iterable[int], Iterable[int], Iterable[str]]:
        return [], [], []


class TokenAfterNodeNP(NodeProcessor):
    def __init__(self, token: str, node_processor: NodeProcessor):
        self.token = token
        self.node_processor: NodeProcessor = node_processor

    def apply(self, node: _Element, dnm_meta: DnmMeta) -> tuple[Iterable[int], Iterable[int], Iterable[str]]:
        offs = dnm_meta.offset_converter.get_offset_data(node)
        r = self.node_processor.apply(node, dnm_meta)

        token = self.token
        return (
            chain(r[0], repeat(offs.node_text_offset_after, len(token))),
            chain(r[1], repeat(offs.node_text_offset_after, len(token))),
            chain(r[2], [token])
        )


class TextExtractingNP(NodeProcessor):
    def __init__(self):
        self._tag_processors: dict[str, NodeProcessor] = {}
        self._class_processors: dict[str, NodeProcessor] = {}

    def register_tag_processor(self, tag: str, processor: NodeProcessor):
        if tag in self._class_processors:
            raise ValueError(f'Processor for tag {tag} already registered')
        self._tag_processors[tag] = processor

    def register_class_processor(self, class_: str, processor: NodeProcessor):
        if class_ in self._class_processors:
            raise ValueError(f'Processor for class {class_} already registered')
        self._class_processors[class_] = processor

    def apply(self, node: _Element, dnm_meta: DnmMeta) -> tuple[Iterable[int], Iterable[int], Iterable[str]]:
        # NOTE: This is a time-critical method.
        # Using local functions (in particular `recurse`) made it substantially faster.
        _tag_processors = self._tag_processors
        _class_processors = self._class_processors

        def get_relevant_node_processor(node: _Element) -> Optional[NodeProcessor]:
            if node.tag in _tag_processors:
                return _tag_processors[node.tag]
            for c in get_node_classes(node):
                if c in _class_processors:
                    return _class_processors[c]
            return None

        # start_refs: list[Iterable[int]] = []
        start_refs: list[Iterable[int]] = []
        end_refs: list[Iterable[int]] = []
        strings: list[Iterable[str]] = []

        def recurse(node: _Element):
            offs = dnm_meta.offset_converter.get_offset_data(node)

            processor = get_relevant_node_processor(node)
            if processor is not None:
                r = processor.apply(node, dnm_meta)
                start_refs.append(r[0])
                end_refs.append(r[1])
                strings.append(r[2])
            else:   # no replacement -> recurse
                if node.text:
                    text = node.text
                    strings.append([text])
                    start_refs.append(range(offs.node_text_offset_before + 1,
                                            offs.node_text_offset_before + len(text) + 1))
                    end_refs.append(range(offs.node_text_offset_before + 2,
                                          offs.node_text_offset_before + len(text) + 2))
                for child in node:
                    recurse(child)
                    # r = self.apply(child, dnm_meta)
                    # start_refs.append(r[0])
                    # end_refs.append(r[1])
                    # strings.append(r[2])

                    if child.tail:
                        tail = child.tail
                        strings.append([tail])
                        child_offs = dnm_meta.offset_converter.get_offset_data(child)
                        start_refs.append(range(child_offs.node_text_offset_after,
                                                child_offs.node_text_offset_after + len(tail)))
                        end_refs.append(range(child_offs.node_text_offset_after + 1,
                                              child_offs.node_text_offset_after + len(tail) + 1))

        recurse(node)

        return chain(*start_refs), chain(*end_refs), chain(*strings)


class TextExtractingBlockedNP(NodeProcessor):
    """Extracts the text content of a node, but processes the children with a different processor.
    This can be useful to avoid infinite recursion in some cases.
    """
    def __init__(self, child_processor: NodeProcessor):
        self.child_processor = child_processor

    def apply(self, node: _Element, dnm_meta: DnmMeta) -> tuple[Iterable[int], Iterable[int], Iterable[str]]:
        offs = dnm_meta.offset_converter.get_offset_data(node)

        start_refs: list[Iterable[int]] = []
        end_refs: list[Iterable[int]] = []
        strings: list[Iterable[str]] = []

        # TODO: this is mostly a copy of the code in TextExtractingNP. Refactor!
        if node.text:
            text = node.text
            strings.append([text])
            start_refs.append(range(offs.node_text_offset_before + 1,
                                    offs.node_text_offset_before + len(text) + 1))
            end_refs.append(range(offs.node_text_offset_before + 2,
                                  offs.node_text_offset_before + len(text) + 2))
        for child in node:
            r = self.child_processor.apply(child, dnm_meta)
            start_refs.append(r[0])
            end_refs.append(r[1])
            strings.append(r[2])

            if child.tail:
                tail = child.tail
                strings.append([tail])
                child_offs = dnm_meta.offset_converter.get_offset_data(child)
                start_refs.append(range(child_offs.node_text_offset_after,
                                        child_offs.node_text_offset_after + len(tail)))
                end_refs.append(range(child_offs.node_text_offset_after + 1,
                                      child_offs.node_text_offset_after + len(tail) + 1))

        return chain(*start_refs), chain(*end_refs), chain(*strings)


class SourceHtmlNP(NodeProcessor):
    """Essentially outputs the original HTML sources of the node (but generates it from the DOM).
    TODO: Currently, attributes are skipped. This should be configurable.
    """
    def __init__(self):
        pass

    def apply(self, node: _Element, dnm_meta: DnmMeta) -> tuple[Iterable[int], Iterable[int], Iterable[str]]:
        start_refs: list[Iterable[int]] = []
        end_refs: list[Iterable[int]] = []
        strings: list[Iterable[str]] = []

        def recurse(node: _Element):
            offs = dnm_meta.offset_converter.get_offset_data(node)

            token = f'<{node.tag}>'
            start_refs.append(repeat(offs.node_text_offset_before, len(token)))
            end_refs.append(repeat(offs.node_text_offset_before + 1, len(token)))
            strings.append(token)

            if text := node.text:
                strings.append([text])
                start_refs.append(range(offs.node_text_offset_before + 1,
                                        offs.node_text_offset_before + len(text) + 1))
                end_refs.append(range(offs.node_text_offset_before + 2,
                                      offs.node_text_offset_before + len(text) + 2))
            for child in node:
                recurse(child)

                if child.tail:
                    tail = child.tail
                    strings.append([tail])
                    child_offs = dnm_meta.offset_converter.get_offset_data(child)
                    start_refs.append(range(child_offs.node_text_offset_after,
                                            child_offs.node_text_offset_after + len(tail)))
                    end_refs.append(range(child_offs.node_text_offset_after + 1,
                                          child_offs.node_text_offset_after + len(tail) + 1))

            token = f'</{node.tag}>'
            start_refs.append(repeat(offs.node_text_offset_after - 1, len(token)))
            end_refs.append(repeat(offs.node_text_offset_after, len(token)))
            strings.append(token)

        recurse(node)

        return chain(*start_refs), chain(*end_refs), chain(*strings)


class NodeBasedDnmFactory(DnmFactory):
    def __init__(self, root_processor: NodeProcessor):
        self._root_processor = root_processor

    def make_dnm_from_meta(self, dnm_meta: DnmMeta) -> Dnm:
        if dnm_meta.embedded_annotations:
            raise ValueError('dnm_meta should not contain embedded annotations before creating the DNM')

        start_refs, end_refs, strings = self._root_processor.apply(dnm_meta.dom, dnm_meta)

        string = ''.join(strings)
        start_refs = list(start_refs)
        end_refs = list(end_refs)

        if len(string) != len(start_refs) or len(string) != len(end_refs):
            raise Exception('Lengths of string, start_refs, and end_refs do not match. '
                            'This is likely a bug in a NodeProcessor.')

        return Dnm(meta_info=dnm_meta, string=string, start_refs=start_refs, end_refs=end_refs)
