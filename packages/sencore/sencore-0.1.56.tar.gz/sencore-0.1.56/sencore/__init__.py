"""``sencore`` Package

.. topic:: Parse sentence into vocabularies

  .. code:: python

    from sencore import EnVocabParser

    def vocab(lang, sen):
      vp = EnVocabParser(lang)
      vocabs = vp.digest(sen)
      print(vocabs)

.. topic:: Parse sentence into phrases

  .. code:: python

    from sencore import PhraseParser

    def phrase(lang, sen):
      pp = PhraseParser(lang)
      phrases = pp.digest(sen)
      print(phrases)

"""

__version__ = '0.1.56'

#from .parser import Parser
from .vocab_parser.en import EnVocabParser
from .vocab_parser.es import EsVocabParser
from .phrase_parser import PhraseParser
from .phrase_model_parser import PhraseModelParser
from .structure_parser import StructureParser
from .kg_parser import KGParser
from .deeplapi import DeepLAPI
