from sencore.parser import Parser
import torch
from transformers import BertTokenizerFast, BertForTokenClassification
from phrase_detective import PKG_INDICES
import spacy

def align_back_to_words(word_ids, labels):
  assert(len(word_ids) == len(labels))

  word_labels = []
  previous_idx = None

  for i, word_idx in enumerate(word_ids):
    if word_idx is not None and word_idx != previous_idx:
      word_labels.append(labels[i])
    previous_idx = word_idx
  return word_labels


def align_back_to_tokens(word_ids, subtokens):
  assert(len(word_ids) == len(subtokens))

  tokens = []
  previous_idx = None

  for i, word_idx in enumerate(word_ids):
    if word_idx is not None and word_idx != previous_idx:
      tokens.append(subtokens[i])
    elif word_idx is not None and word_idx == previous_idx:
      tokens[-1] = tokens[-1]+subtokens[i][2:]
    previous_idx = word_idx
  return tokens

class PhraseModelParser(Parser):
  """``PhraseModelParser`` is to detect phrases from sentence. Inherit ``Parser``, implements ``digest``.
  """

  def __init__(self, lang):
    """Initialize nlp processor according to language

    Args:
      lang (str): language abbreviation
    """

    super().__init__(lang) 
    self._nlp = spacy.load(PKG_INDICES[lang])

    model_name = "phi0108/np_{}".format(lang)
    self.tokenizer = BertTokenizerFast.from_pretrained(model_name)#, local_files_only=True)
    self.np_model = BertForTokenClassification.from_pretrained(model_name)

    self.labels_2_ids = {"O": 0, "B-N": 1, "I-N": 2}

    self.ids_2_labels = {v: k for k,v in self.labels_2_ids.items()}

    self.unique_labels = self.labels_2_ids.keys()

  def predict_sentence(self, sentence):
    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda:0" if use_cuda else "cpu")

    if use_cuda:
        self.np_model =self.np_model.cuda()

    inputs = self.tokenizer(sentence, return_tensors='pt')
    with torch.no_grad():
      logits = self.np_model(**inputs).logits

    predictions = torch.argmax(logits, dim=2)
    prediction_labels = [self.ids_2_labels[i.item()] for i in predictions[0]]

    subtokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    word_ids = inputs.word_ids()
    tokens = align_back_to_tokens(word_ids, subtokens)
    word_labels = align_back_to_words(word_ids, prediction_labels)
    assert(len(word_labels) == len(tokens))
    return word_labels, tokens, len(tokens)

  def align_to_spacy(self, sentence, tags, tokens):
    doc = self._nlp(sentence)
    i = 0
    alignment = [[] for t in doc]

    #print([t for t in doc])
    #print(tokens)
    #print(tags)
    for index, t in enumerate(doc):
      if tokens[i] == "[UNK]":
        tokens[i] = t.text
      if len(tokens[i])>len(t.text):
        text = tokens[i]
        tokens[i] = text[:len(t.text)]
        tokens.insert(i+1, text[len(t.text):]) 
        tags.insert(i+1, tags[i])
        alignment[index].append(i)
      elif len(tokens[i]) <= len(t.text):
        alignment[index].append(i) 
        while t.text != "".join([tokens[n] for n in alignment[index]]):
          i = i+1
          alignment[index].append(i)
      i = i+1

    _tags = []
    for index, e in enumerate(alignment):
      _tags.append(tags[e[0]]) 
    return _tags

  def merge_to_phrases(self, tags, sentence):
    #print(sentence)
    #print(tags)
    phrases = []
    size = len(tags)
    for i in range(size):
      if tags[i] == "B-N":
        phrases.append({"start": i})
      elif i>=1 and tags[i-1]=="O" and tags[i] == "I-N":
        phrases.append({"start": i})
      elif tags[i] == "I-N":
        phrases[-1]["end"] = i+1

    doc = self._nlp(sentence)
    _phrases = []
    for p in phrases:
      if "end" in p:
        p["text"] = doc[p["start"]: p["end"]].text
        _phrases.append(p)
    return _phrases

  def digest(self, sentence):
    """Parse sentence into phrases with linguistic meta info

    Args:
      sentence (str): sentence to be parsed

    Returns:
      list(dict): keys are ``text`` and ``start`` and ``end``. 

    """
    tags, tokens, _ = self.predict_sentence(sentence)
    aligned_tags = self.align_to_spacy(sentence, tags, tokens)
    result = self.merge_to_phrases(aligned_tags, sentence)
    
    return result

