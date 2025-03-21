from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER
from spacy.lang.char_classes import CONCAT_QUOTES, LIST_ELLIPSES, LIST_ICONS

infixes = (
  LIST_ELLIPSES
  + LIST_ICONS
  + [
      r"(?<=[0-9])[+\\-\\*^](?=[0-9-])",
      r"(?<=[{al}{q}])\\.(?=[{au}{q}])".format(
          al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
      ),
      r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
      # ✅ Commented out regex that splits on hyphens between letters:
      # r"(?<=[{a}])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),
      r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
  ]
)


def merge_ranges(ranges):
  ordered = sorted(ranges, key=lambda x: x[0])
  purified = []
  index = 0
  while index < len(ordered)-1:
    first, second = ordered[index], ordered[index+1]
    if first[1] > second[0]:
      purified.append((first[0], max(first[1], second[1]), first[2]))
      index = index + 2
    else:
      purified.append(first)
      index = index + 1
  if index == len(ordered)-1:
    purified.append(ordered[index])
  return purified

def extend_ranges(ranges, maxlen):
  ordered = merge_ranges(ranges)
  start = 0
  result = []
  for e in ordered:
    if start < e[0]:
      result.append((start, e[0], "plain"))
    result.append(e)
    start = e[1]
  if start < maxlen:
    result.append((start, maxlen, "plain"))
  return result

def explain(kg, translator):
  d = {}
  for k, v in kg.items():
    if k in translator.keys():
      d[translator[k]] = v
    else:
      d[k] = v
  return d
