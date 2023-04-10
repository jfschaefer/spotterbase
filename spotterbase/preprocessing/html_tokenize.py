from typing import Optional

from lxml import etree
from lxml.etree import _ElementTree, _Element, _Comment

from spotterbase.corpora.interface import Document
from spotterbase.corpora.resolver import Resolver
from spotterbase.dnm.linked_str import string_to_lstr, LinkedStr
from spotterbase.dnm_nlp.word_tokenizer import word_tokenize
from spotterbase.selectors.offset_converter import OffsetConverter
from spotterbase.utils import config_loader
from spotterbase.utils.config_loader import ConfigUri, ConfigPath

# TODO: Would be better to have a positive list (and not recurse)?
DEFAULT_NODES_TO_IGNORE: set[str] = {
    'svg', 'math', 'head', 'script', 'img'
}


class HtmlTokenizer:
    def __init__(self, add_word_ids: bool = False, word_class: Optional[str] = None,
                 nodes_to_ignore: Optional[set[str]] = None):
        self.nodes_to_ignore: set[str] = DEFAULT_NODES_TO_IGNORE if nodes_to_ignore is None else nodes_to_ignore
        self.add_word_ids: bool = add_word_ids
        self.word_class: Optional[str] = word_class

    def process(self, document: Document) -> _ElementTree:
        tree = document.get_html_tree(cached=False)
        offset_converter = OffsetConverter(tree.getroot())
        word_counter = 0

        def span_from_word(word: LinkedStr, offset: int) -> _Element:
            nonlocal word_counter
            node = etree.Element('span')
            node.attrib['data-sb-start'] = str(offset + word.get_start_ref())
            node.attrib['data-sb-end'] = str(offset + word.get_end_ref())
            if self.add_word_ids:
                node.attrib['id'] = f'sb:w{word_counter}'
            if self.word_class:
                node.attrib['class'] = self.word_class
            node.text = word.string

            word_counter += 1
            return node

        def recurse(node: _Element, mark_words: bool):

            child_mark_words = mark_words
            if mark_words and node.tag in self.nodes_to_ignore:
                child_mark_words = False

            node_offsets = offset_converter.get_offset_data(node)
            node.attrib['data-sb-start'] = str(node_offsets.node_text_offset_before)
            node.attrib['data-sb-end'] = str(node_offsets.node_text_offset_after)

            number_of_word_nodes_added: int = 0

            if child_mark_words and node.text:
                original_text = node.text
                lstr: LinkedStr = string_to_lstr(original_text)
                words = word_tokenize(lstr)
                if words:
                    node.text = original_text[:words[0].get_start_ref()]
                    for i, word in enumerate(words):
                        span = span_from_word(word, offset=node_offsets.node_text_offset_before + 1)
                        if i == len(words) - 1:
                            span.tail = original_text[word.get_end_ref():]
                        else:
                            span.tail = original_text[word.get_end_ref():words[i + 1].get_start_ref()]
                        node.insert(index=i, element=span)
                        number_of_word_nodes_added += 1

            for i, child in enumerate(node):
                if i < number_of_word_nodes_added:
                    continue
                if isinstance(child, _Comment):
                    continue
                recurse(child, child_mark_words)

            if mark_words and node.tail:
                original_text = node.tail
                lstr = string_to_lstr(original_text)
                words = word_tokenize(lstr)
                if words:
                    node.tail = original_text[:words[0].get_start_ref()]
                    last_element = node
                    for i, word in enumerate(words):
                        span = span_from_word(word, offset=node_offsets.node_text_offset_after)
                        oldtail = last_element.tail    # lxml moves the tail when using addnext...
                        last_element.addnext(span)
                        last_element.tail = oldtail
                        if i == len(words) - 1:
                            span.tail = original_text[word.get_end_ref():]
                        else:
                            span.tail = original_text[word.get_end_ref():words[i + 1].get_start_ref()]
                        last_element = span

        recurse(tree.getroot(), mark_words=True)

        return tree


def main():
    document = ConfigUri('--document', 'URI of the document to be tokenized')
    outpath = ConfigPath('--output', 'Path to the tokenized document')
    config_loader.auto()
    assert document.value
    actual_doc = Resolver.get_document(document.value)
    assert actual_doc is not None, f'Failed to find {document}'
    tree = HtmlTokenizer(add_word_ids=True).process(actual_doc)

    assert outpath.value
    with open(outpath.value, 'wb') as fp:
        tree.write(fp)


if __name__ == '__main__':
    main()
