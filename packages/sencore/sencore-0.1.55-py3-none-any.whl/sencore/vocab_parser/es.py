from sencore.vocab_parser.general import VocabParser
import spacy

class EsVocabParser(VocabParser):
  """``VocabParser`` is to detect vocabularies from sentence. Inherit ``Parser``, implements ``digest``.
  """

  def __init__(self, lang: str):
    """Initialize nlp processor according to language

    Args:
      lang (str): language abbreviation
    """

    super().__init__(lang) 


  def digest(self, sentence):
    """Parse sentence into vocabularies with linguistic meta info

    Args:
      sentence (str): sentence to be parsed

    Returns:
      list[dict]: keys are ``word``, ``pos``, "lemma", "start" and "end". 
    
    """

    result = []
    doc = self._nlp(sentence)
    verbs = [e for e in doc if e.pos_=="VERB"]
    for e in verbs:
      start, end = e.i, e.i+1
      if "Reflex=Yes" in e.morph:
        _lemmas = e.lemma_.split(" ")
        lemma = _lemmas[0]+"se" if len(_lemmas)>1 else _lemmas[0]+"[Review]"
      elif "Mood=Imp" in e.morph:
        lemma = e.lemma_+"[Review]"
      elif doc[e.i-1].dep_ in["iobj", "expl:pv", "expl:pass", "obj"] and doc[e.i-1].head==e and "Reflex=Yes" in doc[e.i-1].morph:
        lemma = e.lemma_+"se"
        start = e.i-1
      elif any(["Reflex=Yes" in v.morph for v in e.lefts]):
        continue
      else:
        lemma = e.lemma_.split(" ")[0]
      result.append({"word": doc[start:end].text, "pos": e.pos_, "lemma": lemma, "start": start, "end": end})

    return result 
