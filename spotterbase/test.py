from spotterbase.config_loader import ConfigLoader
from spotterbase.data.arxmliv_corpus import ArXMLiv

ConfigLoader().load_from_args()

arxmliv = ArXMLiv()

corpus = arxmliv.get_corpus('2020')

print('number of documents:', sum(1 for _ in corpus))
