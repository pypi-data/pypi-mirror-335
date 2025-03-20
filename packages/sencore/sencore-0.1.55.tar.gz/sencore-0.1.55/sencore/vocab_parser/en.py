from sencore.vocab_parser.general import VocabParser
import spacy

class EnVocabParser(VocabParser):
  """``VocabParser`` is to detect vocabularies from sentence. Inherit ``Parser``, implements ``digest``.
  """

  def __init__(self, lang: str):
    """Initialize nlp processor according to language

    Args:
      lang (str): language abbreviation
    """

    super().__init__(lang) 
    self._poses = ["VERB", "AUX"]

  def digest(self, sentence):
    """Parse sentence into vocabularies with linguistic meta info

    Args:
      sentence (str): sentence to be parsed

    Returns:
      list[dict]: keys are ``word``, ``pos``, "lemma", "start" and "end". 
    
    """

    doc = self._nlp(sentence)
    if len(self._poses)>0:
      result = [{"word": e.text, "pos": e.pos_, "lemma": e.lemma_, "start": e.i, "end": e.i+1} for e in doc if e.pos_ in self._poses]
    else:
      result = [{"word": e.text, "pos": e.pos_, "lemma": e.lemma_, "start": e.i, "end": e.i+1} for e in doc]

    return result 
