import spacy
from sencore.parser import Parser
from spacy import Language
from phrase_detective import NounPhraseRecognizer, VerbKnowledgeRecognizer, PKG_INDICES
from sencore.lib import extend_ranges

@Language.factory("nprecog")
def create_np_parser(nlp: Language, name: str):
  """Register ``NounPhraseRecognizer`` into pipeline with component name ``nprecog``
  """
  return NounPhraseRecognizer(nlp) 

#@Language.factory("vkbrecog")
#def create_vkb_parser(nlp: Language, name: str):
#  """Register ``VerbKnowledgeRecognizer`` into pipeline with component name ``vkbrecog``
#  """
#  return VerbKnowledgeRecognizer(nlp) 

class PhraseParser(Parser):
  """``PhraseParser`` is to detect phrases from sentence. Inherit ``Parser``, implements ``digest``.
  """

  def __init__(self, lang):
    """Initialize nlp processor according to language

    Args:
      lang (str): language abbreviation
    """

    super().__init__(lang) 
    self._nlp = spacy.load(PKG_INDICES[lang])
    self._nlp.add_pipe("nprecog")
    #self._nlp.add_pipe("vkbrecog")

  def digest(self, sentence):
    """Parse sentence into phrases with linguistic meta info

    Args:
      sentence (str): sentence to be parsed

    Returns:
      dict: keys are ``noun_phrases`` and ``buildin_np``, which are of type ``list[dict]``. 

    """

    doc = self._nlp(sentence)
    
    # Obtain from phrase_detective
    noun_phrases = [np for np in doc._.noun_phrases]
    #verbs = [v for v in doc._.verbs]

    # Obtain from spacy build-in
    buildin_np = [np for np in doc.noun_chunks]

    # In order to mark the span as noun_phrases, verbs or plain for subtitle usage
    #noun_phrases_ranges = [(np.start, np.end, "noun_phrases") for np in noun_phrases]
    #verbs_ranges = [(v.i, v.i+1, "verbs") for v in verbs]
    #doc_mark = extend_ranges(noun_phrases_ranges+verbs_ranges, len(doc))
    #markers = [(doc[d[0]: d[1]].text, d[2]) for d in doc_mark]

    result = {
      "noun_phrases": [{"text": np.text, "start":np.start, "end": np.end, "start_char": np.start_char, "end_char": np.end_char} for np in noun_phrases],
      #"verbs": [{"text": v.text, "tag": v.tag_, "form": spacy.explain(v.tag_), "lemma": v.lemma_} for v in verbs],
      "buildin_np": [{"text": np.text, "start":np.start, "end": np.end, "start_char": np.start_char, "end_char": np.end_char} for np in buildin_np], 
      #"markers": markers,
    }

    return result

  def __del__(self):
    self._nlp.remove_pipe("nprecog")
    #self._nlp.remove_pipe("vkbrecog")
