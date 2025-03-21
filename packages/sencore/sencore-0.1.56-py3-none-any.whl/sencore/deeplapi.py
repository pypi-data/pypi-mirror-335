import deepl
import os

class DeepLAPI:

  def __init__(self, from_lang, to_lang="ZH"):
    self.from_lang, self.to_lang = from_lang.upper(), "ZH" if to_lang == "cn" else to_lang.upper()
    self.api = deepl.Translator(os.getenv("DEEPL_AUTH_KEY"))

  def search(self, p, context=None):
    try:
      _r = self.api.translate_text(p, source_lang=self.from_lang, target_lang=self.to_lang, context=context)
      result = {
        "original": p,
        "translated": _r.text,
        "from": "DeepL"
      }
    except Exception as e:
      print(e)
      result = {
        "original": p,
        "translated": "",
        "from": "DeepL"
      }
    return result


