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

  rule_name = "verb_indicativo_futuro"

  dep_matcher = DependencyMatcher(nlp.vocab)

  # verb 
  verb = [
    {
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": "VERB", "DEP": "ROOT", "MORPH": {"IS_SUPERSET": ["Mood=Ind", "Tense=Fut"]}}
    }
  ]

  dep_matcher.add(rule_name, [verb])

  matches = dep_matcher(doc)
  for index, (_, [verb_id]) in enumerate(matches):
    verb_core = doc[verb_id]
    raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": verb_core.lemma_, "gid": index})) 

  dep_matcher.remove(rule_name)


  base_index = len(raw_matches)
  # ser verb 
  ser_verb = [
    {
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": "VERB", "DEP": "ROOT", "MORPH": {"IS_SUPERSET": ["Tense=Past", "VerbForm=Part"]}}
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">--",
      "RIGHT_ID": "aux",
      "RIGHT_ATTRS": {"POS": "AUX", "LEMMA": "ser", "MORPH": {"IS_SUPERSET": ["Mood=Ind", "Tense=Fut"]}}
    }
  ]

  dep_matcher.add(rule_name, [ser_verb])

  matches = dep_matcher(doc)
  for index, (_, [verb_id, aux_id]) in enumerate(matches):
    aux_core = doc[aux_id]
    verb_core = doc[verb_id]
    raw_matches.append((aux_id, aux_id+1, {"sign": "aux_ser", "aux_lemma": aux_core.lemma_, "gid": base_index+index})) 
    raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": verb_core.lemma_, "gid": base_index+index})) 

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)

