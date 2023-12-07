""" A very simple word tokenizer implementation.

As it does not use any DNM-specific features (except for working on DnmDstr),
it might be better to use an off-the-shelf tokenizer.
"""
import typing

from intervaltree import Interval, IntervalTree

from spotterbase.dnm.linked_str import LinkedStr_T


@typing.overload
def word_tokenize(sentence: LinkedStr_T, keep_as_words: typing.Optional[list[tuple[int, int]]] = None) -> \
        list[LinkedStr_T]:
    ...


@typing.overload
def word_tokenize(sentence: str, keep_as_words: typing.Optional[list[tuple[int, int]]] = None) -> list[str]:
    ...


def word_tokenize(sentence, keep_as_words: typing.Optional[list[tuple[int, int] | Interval]] = None) -> list:
    """Tokenizes a sentence (or longer text) into words using some simple rules.
    keep_as_words can be used to keep certain parts (range is right-exclusive) of the text as words
    (e.g. annotated ranges that were replaced with a complex token)."""
    if keep_as_words is None:
        keep_as_words = []

    # merge all overlapping ranges that should be kept as words
    it = IntervalTree()
    for entry in keep_as_words:
        if isinstance(entry, Interval):
            it.add(entry)
        else:
            it.addi(entry[0], entry[1])
    it.merge_overlaps(strict=True)

    keep_as_words = sorted(it)

    # keep_as_words.sort()
    # assert all(keep_as_words[i][1] <= keep_as_words[i + 1][0] for i in range(len(keep_as_words) - 1)), \
    #     'keep_as_words ranges must not overlap'

    words = []
    word_start = 0
    pos = 0
    keep_as_words_pos = 0
    while pos < len(sentence):
        if keep_as_words_pos < len(keep_as_words) and keep_as_words[keep_as_words_pos][0] == pos:
            if word_start != pos:
                words.append(sentence[word_start:pos])
            words.append(sentence[keep_as_words[keep_as_words_pos][0]:keep_as_words[keep_as_words_pos][1]])
            word_start = keep_as_words[keep_as_words_pos][1]
            pos = word_start - 1
            keep_as_words_pos += 1
        elif str(sentence[pos]).isspace():
            if word_start != pos:
                words.append(sentence[word_start:pos])
            word_start = pos + 1
        elif str(sentence[pos]) in {'.', ',', ':', ';', '!', '?', ')', '(', '[', ']', '{', '}', '-', '”', '“'}:
            if word_start != pos:
                words.append(sentence[word_start:pos])
            words.append(sentence[pos])
            word_start = pos + 1
        pos += 1
    if word_start != len(sentence):
        words.append(sentence[word_start:])
    return words
