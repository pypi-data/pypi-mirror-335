import json
from sencore import PhraseParser, StructureParser
import click

def _write_to_jsonl(content, jsonlfile="prodigy.jsonl"):
  with open(jsonlfile, 'w') as outfile:
    for entry in content:
      json.dump(entry, outfile)
      outfile.write('\n')

@click.command()
@click.option("--lang", help="Specify the language", default="en", prompt="Language")
@click.option("--senfile", help="Specify the sentence file in json", prompt="Sentence file")
@click.option("--dstname", help="Specify the phrase review file", prompt="Review file")
def generate_prodigy_phrases(lang, senfile, dstname):
  pp = PhraseParser(lang)

  with open(senfile, encoding="utf8") as f:
    TEXTS = json.loads(f.read())

  np_content = []

  for sen in TEXTS:
    phrases = pp.digest(sen)

    noun_phrases = []
    print(sen)
    for np in phrases["noun_phrases"]:
      #print("{}:{}, {}, {}".format(np.start, np.end, np.text, sen[np.start_char:np.end_char]))
      refined_np = {"token_start": np["start"], "token_end": np["end"]-1, "start": np["start_char"], "end": np["end_char"]-1, "label": "NP"}
      noun_phrases.append(refined_np)
    #print("="*140)
    np_content.append({"text": sen, "meta": {}, "_is_binary": False, "_view_id": "ner_manual", "spans": noun_phrases})

  #print(np_content)
  _write_to_jsonl(np_content, jsonlfile=dstname+".noun_phrase.jsonl")



@click.command()
@click.option("--lang", help="Specify the language", default="en", prompt="Language")
@click.option("--senfile", help="Specify the sentence file in json", prompt="Sentence file")
@click.option("--dstname", help="Specify the phrase review file", prompt="Review file")
def generate_prodigy_structures(lang, senfile, dstname):
  sp = StructureParser(lang)

  with open(senfile, encoding="utf8") as f:
    TEXTS = json.loads(f.read())

  structure_content = []

  for sen in TEXTS:
    print(sen)

    try:
      structure = sp.digest(sen)
      print(structure)
      ss = []
      for part in structure:
        #print("{}:{}, {}, {}".format(np.start, np.end, np.text, sen[np.start_char:np.end_char]))
        if part["explanation"]:
          refined_structure = {"token_start": part["start"], "token_end": part["end"]-1, "start": part["start_char"], "end": part["end_char"]-1, "label": part["explanation"]}
          ss.append(refined_structure)
      #print("="*140)
      structure_content.append({"text": sen, "meta": {}, "_is_binary": False, "_view_id": "ner_manual", "spans": ss})
    except:
      pass 

  _write_to_jsonl(structure_content, jsonlfile=dstname+".structure.jsonl")

