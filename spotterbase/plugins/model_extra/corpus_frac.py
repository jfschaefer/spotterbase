"""Model for annotating "fractional corpora", i.e. corpora that are a subset of a larger corpus.

Motivation:
Often, people might not want to work with a big corpus, but only with a small subset.
This might be because they do not have the computational resources or just want to quickly test something.
If everyone chooses a different subset, annotations cannot be re-used.
Standardizing the subset selection could help with that.

Implementation:
We can tag documents to indicate that they belong to a subset of the corpus.
To select subcorpora representatively, an option would be to use the hash of the document ID.
We can then make subsets that correspond to e.g. a 10th or a 100th of the corpus.
The subcorpora should be nested.
That way, if someone ran a spotter over a 10th of the corpus, someone else who only works with a 100th of the corpus
can still use the results."""

from spotterbase.model_core import SB, TagSet, Tag
from spotterbase.rdf import Vocabulary, NameSpace, Uri
from spotterbase.records.record import Record


class FRAC_CORPUS(Vocabulary):
    NS: NameSpace = NameSpace(SB.NS.uri / 'ext/fraccorpus/', prefix='fraccorpus:')

    deci: Uri
    centi: Uri
    milli: Uri
    decimilli: Uri


TAGSET_RECORDS: list[Record] = [
    TagSet(
        uri=Uri(FRAC_CORPUS),
        label='Tag set for fractional corpora',
    ),
    Tag(
        uri=FRAC_CORPUS.deci,
        label='deci',
        comment='Belongs to a selected ~10th of the corpus',
        belongs_to=Uri(FRAC_CORPUS),
    ),
    Tag(
        uri=FRAC_CORPUS.centi,
        label='centi',
        comment='Belongs to a selected ~100th of the corpus',
        belongs_to=Uri(FRAC_CORPUS),
    ),
    Tag(
        uri=FRAC_CORPUS.milli,
        label='milli',
        comment='Belongs to a selected ~1000th of the corpus',
        belongs_to=Uri(FRAC_CORPUS),
    ),
    Tag(
        uri=FRAC_CORPUS.decimilli,
        label='decimilli',
        comment='Belongs to a selected ~10000th of the corpus',
        belongs_to=Uri(FRAC_CORPUS),
    ),
]
