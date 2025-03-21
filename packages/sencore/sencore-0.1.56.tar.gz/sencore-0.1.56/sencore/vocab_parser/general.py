from sencore.parser import Parser
import spacy
from spacy.util import compile_infix_regex
from sencore.lib import infixes

class VocabParser(Parser):
  """``VocabParser`` is to detect vocabularies from sentence. Inherit ``Parser``, implements ``digest``.
  """

  _pkgindices = {
    "en": "en_core_web_trf",
    "es": "es_dep_news_trf",
    "de": "de_dep_news_trf",
    "fr": "fr_dep_news_trf",
  }

  def __init__(self, lang: str):
    """Initialize nlp processor according to language

    Args:
      lang (str): language abbreviation
    """

    super().__init__(lang) 
    self._nlp = spacy.load(self.__class__._pkgindices[lang])
    infix_re = compile_infix_regex(infixes)
    self._nlp.tokenizer.infix_finditer = infix_re.finditer

  def digest(self, sentence):
    """Parse sentence into vocabularies with linguistic meta info

    Args:
      sentence (str): sentence to be parsed

    Returns:
      list[dict]: keys are ``word``, ``pos``, "lemma", "start" and "end". 
    
    """
    raise Exception("You have to implement method {}!!!".format("digest"))
 
