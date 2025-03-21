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

  rule_name = "verb_reflexivo"

  dep_matcher = DependencyMatcher(nlp.vocab)

  # pron haber verb 
  pron_haber_verb = [
    {
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": "VERB"}
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">--",
      "RIGHT_ID": "pron",
      "RIGHT_ATTRS": {"DEP": {"IN": ["obj", "iobj", "expl:pv"]}, "MORPH": {"IS_SUPERSET": ["Reflex=Yes"]}}
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">--",
      "RIGHT_ID": "aux_haber",
      "RIGHT_ATTRS": {"POS": "AUX", "DEP": "aux", "LEMMA": "haber"}
    },
  ]

  dep_matcher.add(rule_name, [pron_haber_verb])

  matches = dep_matcher(doc)
  for index, (_, [verb_id, pron_id, aux_haber_id]) in enumerate(matches):
    pron_core = doc[pron_id]
    aux_haber_core = doc[aux_haber_id]
    verb_core = doc[verb_id]

    assertion = aux_haber_id > pron_id
    if assertion:
      raw_matches.append((pron_id, pron_id+1, {"sign": "pron", "pron_lemma": pron_core.lemma_, "gid": index})) 
      raw_matches.append((aux_haber_id, aux_haber_id+1, {"sign": "aux_haber", "aux_lemma": aux_haber_core.lemma_, "gid": index})) 
      raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": verb_core.lemma_, "gid": index})) 

  dep_matcher.remove(rule_name)

  base_index = len(raw_matches)//3

  # pron verb 
  pron_verb = [
    {
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": "VERB"}
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">--",
      "RIGHT_ID": "pron",
      "RIGHT_ATTRS": {"DEP": {"IN": ["obj", "iobj", "expl:pv"]}, "MORPH": {"IS_SUPERSET": ["Reflex=Yes"]}}
    }
  ]

  dep_matcher.add(rule_name, [pron_verb])

  matches = dep_matcher(doc)
  for index, (_, [verb_id, pron_id]) in enumerate(matches):
    pron_core = doc[pron_id]
    verb_core = doc[verb_id]
    
    exclude_assertion = verb_id not in [e[0] for e in raw_matches if e[2]["sign"]=="verb"]
    filter_assertion = " ".join([e.lemma_ for e in doc[verb_id-2: verb_id]]) != "ir a"
    if exclude_assertion and filter_assertion:
      raw_matches.append((pron_id, pron_id+1, {"sign": "pron", "pron_lemma": pron_core.lemma_, "gid": base_index+index})) 
      raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": verb_core.lemma_, "gid": base_index+index})) 

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)

