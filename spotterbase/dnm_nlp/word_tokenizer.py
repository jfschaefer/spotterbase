""" A very simple word tokenizer implementation.

As it does not use any DNM-specific features (except for working on DnmDstr),
it might be better to use an off-the-shelf tokenizer.
"""
import typing

from spotterbase.dnm.linked_str import LinkedStr_T


@typing.overload
def word_tokenize(sentence: LinkedStr_T) -> list[LinkedStr_T]:
    ...


@typing.overload
def word_tokenize(sentence: str) -> list[str]:
    ...


def word_tokenize(sentence) -> list:
    words = []
    word_start = 0
    for i in range(len(sentence)):
        if str(sentence[i]).isspace():
            if word_start != i:
                words.append(sentence[word_start:i])
            word_start = i + 1
        if str(sentence[i]) in {'.', ',', ':', ';', '!', '?', ')', '(', '[', ']', '{', '}', '-', '”', '“'}:
            if word_start != i:
                words.append(sentence[word_start:i])
            words.append(sentence[i])
            word_start = i + 1
    if word_start != len(sentence):
        words.append(sentence[word_start:])
    return words
