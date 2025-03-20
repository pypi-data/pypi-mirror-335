import json
import csv
from sencore import EnVocabParser, EsVocabParser, PhraseModelParser, StructureParser, KGParser, DeepLAPI
from sencore.lib import explain
import click


def _write_to_csv(fields, content, csvfile="review.csv"):
  #print('Create {} file'.format(csvfile))
  with open(csvfile, encoding="utf8", mode='w') as output_file:
    dict_writer = csv.DictWriter(output_file, restval="-", fieldnames=fields, delimiter='\t')
    dict_writer.writeheader()
    dict_writer.writerows(content)

def _read_from_csv(csvfile):
  content = None
  with open(csvfile, newline='') as cfile:
    reader = csv.DictReader(cfile, delimiter='\t')
    content = [row for row in reader]

  return content

@click.command()
@click.option("--lang", help="Specify the language", default="en", prompt="Language")
@click.option("--senfile", help="Specify the sentence file in json", prompt="Sentence file")
@click.option("--dstname", help="Specify the phrase parsed file", prompt="Review file")
def generate_vocab_parsed(lang, senfile, dstname):
  parsers = {
    "en": EnVocabParser,
    "es": EsVocabParser,
  }
  vp = parsers[lang](lang)

  with open(senfile, encoding="utf8") as f:
    TEXTS = json.loads(f.read())

  content = []

  t_api = DeepLAPI(lang)

  for sen in TEXTS:
    vocabs = vp.digest(sen)
    for v in vocabs:
      print(v)
      r = t_api.search(v["lemma"])
      v["translated"] = r["translated"]
      
    content.append({"sentence": sen, "vocabs": json.dumps(vocabs)})

  _write_to_csv(["sentence", "vocabs"], content, csvfile=dstname+".vocabs.csv")


@click.command()
@click.option("--lang", help="Specify the language", default="en", prompt="Language")
@click.option("--senfile", help="Specify the sentence file in json", prompt="Sentence file")
@click.option("--dstname", help="Specify the phrase parsed file", prompt="Review file")
def generate_phrase_parsed(lang, senfile, dstname):
  pp = PhraseModelParser(lang)

  with open(senfile, encoding="utf8") as f:
    TEXTS = json.loads(f.read())

  np_content = []

  #t_api = DeepLAPI(lang)

  for sen in TEXTS:
    phrases = pp.digest(sen)

    #for p in phrases:
    #  print(p)
    #  r = t_api.search(p["text"])
    #  p.update(r) 
   
    np_content.append({"sentence": sen, "phrases": json.dumps(phrases)})

  _write_to_csv(["sentence", "phrases"], np_content, csvfile="{}.tbr.{}.noun_phrase.csv".format(dstname, lang))

@click.command()
@click.option("--lang", help="Specify the language", default="en", prompt="Language")
@click.option("--senfile", help="Specify the sentence file in json", prompt="Sentence file")
@click.option("--dstname", help="Specify the phrase parsed file", prompt="Review file")
def generate_kg_parsed(lang, senfile, dstname):
  adj_rules = ["adj_for_equal_comparisons", "adj_comparative", "adj_superlative"]
  adv_rules = ["adv_for_equal_comparisons", "adv_comparative", "adv_superlative"]
  prep_rules = ["prep_with_verb", "prep_with_adj", "prep_with_noun"]
  noun_rules = ["noun_proper"]
  verb_rules = ["verb_passive_voice", "verb_simple_present_tense", "verb_simple_past_tense", "verb_simple_future_tense", "verb_present_progressive_tense", "verb_past_progressive_tense", "verb_present_perfect_tense", "verb_past_perfect_tense", "verb_transitive"]

  rules = adj_rules + adv_rules + noun_rules + verb_rules + prep_rules
  labels = ["NOMINAL_CLAUSE", "RELATIVE_CLAUSE", "SUBJUNCTIVE_MOOD"]

  kgp = KGParser(lang, labels=labels, rules=rules)
  kgp_translator = kgp.get_translator("cn")

  with open(senfile, encoding="utf8") as f:
    TEXTS = json.loads(f.read())

  content = []
  t_api = DeepLAPI(lang)

  for sen in TEXTS:
    kgs = explain(kgp.digest(sen), kgp_translator) 
  
    for k, vs in kgs.items():
      if len(vs) > 1:
        for v in vs:
          if "meta" in v:
            r = t_api.search(v["text"])
            v["translated"] = r["translated"]

    _kgs = [(k, vs) for k, vs in kgs.items() if len(vs)>1]
    
    merged_kgs = {}
    for k, vs in _kgs:
      _tmp = {}
      for v in vs:
        if "meta" in v:
          print(v["meta"])
          _gid = str(v["meta"]["gid"]) 
          if _gid in _tmp.keys():
            _tmp[_gid].append(v["text"])
          else:
            _tmp[_gid] = [v["text"]]
      merged_kgs[k] = _tmp

    for k, vs in merged_kgs.items():
      for gid, kg in vs.items():
        text = " ".join(kg) 
        vs[gid] = {
          "text": text,
          "translated": t_api.search(text)["translated"]
        }
    print(kgs)

    content.append({"sentence": sen, "kgs": json.dumps(kgs), "merged_kgs": json.dumps(merged_kgs)})

  _write_to_csv(["sentence", "kgs", "merged_kgs"], content, csvfile=dstname+".kg.csv")


@click.command()
@click.option("--structure_csv", help="Specify structure csv", prompt="structure csv")
@click.option("--kg_csv", help="Specify kg csv", prompt="kg csv")
@click.option("--trans_json", help="Specify translated json", prompt="translated json")
@click.option("--dstname", help="Specify the output csv file", prompt="output csv file")
def merge_csv(structure_csv, kg_csv, trans_json, dstname):
  c1 = _read_from_csv(structure_csv)
  c2 = _read_from_csv(kg_csv)
  t = []
  with open(trans_json, encoding="utf8") as f:
    t = json.loads(f.read())

  assert(len(c1)==len(c2))
  assert(len(t)==len(c1))

  final = []
  for i in range(len(c1)):
    l1 = c1[i]
    l2 = c2[i]
    assert(l1["sentence"] == l2["sentence"])
    e = {
      "sentence": l1["sentence"],
      "structures": l1["structures"],
      "kgs": l2["kgs"],
      "translation": t[i], 
      "merged_kgs": l2["merged_kgs"],
    }
    final.append(e)

  _write_to_csv(["sentence", "structures", "kgs", "merged_kgs", "translation"], final, csvfile=dstname+".structure_kg.csv")
