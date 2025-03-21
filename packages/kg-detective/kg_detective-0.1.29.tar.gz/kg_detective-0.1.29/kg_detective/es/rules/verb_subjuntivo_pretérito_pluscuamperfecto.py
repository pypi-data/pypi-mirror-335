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

  rule_name = "verb_subjuntivo_pretérito_pluscuamperfecto"

  dep_matcher = DependencyMatcher(nlp.vocab)

  # haber ser verb 
  haber_ser_verb = [
    {
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": "VERB", "MORPH": {"IS_SUPERSET": ["Tense=Past", "VerbForm=Part"]}}
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">--",
      "RIGHT_ID": "ser",
      "RIGHT_ATTRS": {"POS": "AUX", "DEP": "aux", "LEMMA": "ser", "MORPH": {"IS_SUPERSET": ["Tense=Past", "VerbForm=Part"]}}
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">--",
      "RIGHT_ID": "haber",
      "RIGHT_ATTRS": {"POS": "AUX", "DEP": "aux", "LEMMA": {"IN": ["haber", "hubieras", "hubierais"]}, "MORPH": {"IS_SUPERSET": ["Mood=Sub", "Tense=Imp"]}}
    }
  ]

  dep_matcher.add(rule_name, [haber_ser_verb])

  matches = dep_matcher(doc)
  for index, (_, [verb_id, ser_id, haber_id]) in enumerate(matches):
    verb_core = doc[verb_id]
    ser_core = doc[ser_id]
    haber_core = doc[haber_id]

    assertion = ser_id > haber_id
    if assertion:
      raw_matches.append((haber_id, haber_id+1, {"sign": "aux_haber", "aux_lemma": haber_core.lemma_, "gid": index})) 
      raw_matches.append((ser_id, ser_id+1, {"sign": "aux_ser", "aux_lemma": ser_core.lemma_, "gid": index})) 
      raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": verb_core.lemma_, "gid": index})) 

  dep_matcher.remove(rule_name)

  base_index = len(raw_matches)//3

  # haber verb 
  haber_verb = [
    {
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": "VERB", "MORPH": {"IS_SUPERSET": ["Tense=Past", "VerbForm=Part"]}}
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">--",
      "RIGHT_ID": "aux",
      "RIGHT_ATTRS": {"POS": "AUX", "DEP": "aux", "LEMMA": {"IN": ["haber", "hubieras", "hubierais"]}, "MORPH": {"IS_SUPERSET": ["Mood=Sub", "Tense=Imp"]}}
    }
  ]

  dep_matcher.add(rule_name, [haber_verb])

  matches = dep_matcher(doc)
  for index, (_, [verb_id, aux_id]) in enumerate(matches):
    aux_core = doc[aux_id]
    verb_core = doc[verb_id]

    reflex_pron = [t for t in verb_core.lefts if t.dep_ in ["obj", "iobj", "expl:pv", "expl:pass"] and "Reflex=Yes" in t.morph]
    if len(reflex_pron)==1:
      raw_matches.append((reflex_pron[0].i, reflex_pron[0].i+1, {"sign": "pron_se", "pron_lemma": reflex_pron[0].lemma_, "gid": index})) 

    raw_matches.append((aux_id, aux_id+1, {"sign": "aux_haber", "aux_lemma": aux_core.lemma_, "gid": base_index+index})) 
    raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": verb_core.lemma_, "gid": base_index+index})) 

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
  
