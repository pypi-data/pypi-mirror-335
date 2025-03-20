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

  patterns = [
    [{"POS": {"IN": ["VERB", "AUX"]}, "MORPH": {"IS_SUPERSET": ["Mood=Sub", "Tense=Imp", "VerbForm=Fin"]}}],
  ]

  raw_matches = []

  rule_name = "verb_subjuntivo_pretérito_imperfecto"
   
  dep_matcher = DependencyMatcher(nlp.vocab)

  # ser verb 
  ser_verb = [
    {
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": "VERB", "MORPH": {"IS_SUPERSET": ["Tense=Past", "VerbForm=Part"]}}
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">--",
      "RIGHT_ID": "aux",
      "RIGHT_ATTRS": {"POS": "AUX", "LEMMA": "ser", "MORPH": {"IS_SUPERSET": ["Mood=Sub", "Tense=Imp"]}}
    }
  ]

  dep_matcher.add(rule_name, [ser_verb])

  matches = dep_matcher(doc)
  for index, (_, [verb_id, aux_id]) in enumerate(matches):
    aux_core = doc[aux_id]
    verb_core = doc[verb_id]
    raw_matches.append((aux_id, aux_id+1, {"sign": "aux_ser", "aux_lemma": aux_core.lemma_, "gid": index})) 
    raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": verb_core.lemma_, "gid": index})) 

  dep_matcher.remove(rule_name)

  base_index = len(raw_matches)//2
  # verb 
  verb = [
    {
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": {"IN": ["AUX", "VERB"]}, "MORPH": {"IS_SUPERSET": ["Mood=Sub", "Tense=Imp"]}}
    }
  ]

  dep_matcher.add(rule_name, [verb])

  matches = dep_matcher(doc)
  for index, (_, [verb_id]) in enumerate(matches):
    verb_core = doc[verb_id]

    reflex_pron = [t for t in verb_core.lefts if t.dep_ in ["obj", "iobj", "expl:pv", "expl:pass"] and "Reflex=Yes" in t.morph]
    if len(reflex_pron)==1:
      raw_matches.append((reflex_pron[0].i, reflex_pron[0].i+1, {"sign": "pron_se", "pron_lemma": reflex_pron[0].lemma_, "gid": base_index+index}))
    raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": verb_core.lemma_, "gid": base_index+index})) 

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)

