from spacy.matcher import Matcher, DependencyMatcher
from kg_detective.lib import clean_merge, mark

def search_out(doc, nlp):
  """Search for  

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """
  raw_matches = []

  rule_name = "pron_posesivo"

  dep_matcher = DependencyMatcher(nlp.vocab)

  p1 = [
    {
      "RIGHT_ID": "pron",
      "RIGHT_ATTRS": {"POS": {"IN": ["DET", "PRON"]}, "MORPH": {"IS_SUPERSET": ["Poss=Yes"]}}
    },
    {
      "LEFT_ID": "pron",
      "REL_OP": ">-",
      "RIGHT_ID": "det",
      "RIGHT_ATTRS": {"POS": "DET", "LEMMA": "el", "MORPH": {"IS_SUPERSET": ["PronType=Art"]}}
    }
  ]

  dep_matcher.add(rule_name, [p1])

  matches = dep_matcher(doc)
  for index, (_, [pron_id, det_id]) in enumerate(matches):
    det_core = doc[det_id]
    det_assertion = len(list(det_core.children))==0
    if det_assertion:
      raw_matches.append((det_id, pron_id+1, {"sign": "det_pron", "gid": index})) 

  dep_matcher.remove(rule_name)

  base_index = len(raw_matches)

  p2 = [
    {
      "RIGHT_ID": "pron",
      "RIGHT_ATTRS": {"POS": {"IN": ["DET", "PRON"]}, "DEP": {"IN": ["compound", "det"]}, "MORPH": {"IS_SUPERSET": ["Poss=Yes"]}}
    },
    {
      "LEFT_ID": "pron",
      "REL_OP": "<-",
      "RIGHT_ID": "det",
      "RIGHT_ATTRS": {"POS": "DET", "LEMMA": "el", "MORPH": {"IS_SUPERSET": ["PronType=Art"]}}
    }
  ]

  dep_matcher.add(rule_name, [p2])

  matches = dep_matcher(doc)
  for index, (_, [pron_id, det_id]) in enumerate(matches):
    pron_core = doc[pron_id]
    pron_assertion = len(list(pron_core.children))==0
    if pron_assertion:
      raw_matches.append((det_id, pron_id+1, {"sign": "det_pron", "gid": base_index + index})) 

  dep_matcher.remove(rule_name)


  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
