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

  rule_name = "verb_imperativo"

  dep_matcher = DependencyMatcher(nlp.vocab)

  verb = [
    {
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": "VERB", "MORPH": {"IS_SUPERSET": ["Mood=Imp"]}}
    }
  ]

  no_verb = [
    {
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": "VERB", "MORPH": {"IS_SUPERSET": ["Mood=Sub"]}}
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">--",
      "RIGHT_ID": "no",
      "RIGHT_ATTRS": {"POS": "ADV", "DEP":"advmod", "MORPH": {"IS_SUPERSET": ["Polarity=Neg"]}, "LEMMA": "no"}
    }
  ]

  dep_matcher.add(rule_name, [verb, no_verb])

  matches = dep_matcher(doc)
  for index, (_, ids) in enumerate(matches):
    if len(ids) == 2:
      neg_id = ids[1]
      neg_core = doc[neg_id]
      raw_matches.append((neg_id, neg_id+1, {"sign": "neg", "neg_lemma": neg_core.lemma_, "gid": index})) 
    verb_id = ids[0]
    verb_core = doc[verb_id]
    reflex_pron = [e for e in verb_core.lefts if e.dep_ in ["expl:pv", "iobj"] and "Reflex=Yes" in e.morph]
    if len(reflex_pron)>0:
      raw_matches.append((reflex_pron[0].i, reflex_pron[0].i+1, {"sign": "pron", "pron_lemma": reflex_pron[0].lower_, "gid": index})) 
    raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": verb_core.lemma_, "gid": index})) 

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)

