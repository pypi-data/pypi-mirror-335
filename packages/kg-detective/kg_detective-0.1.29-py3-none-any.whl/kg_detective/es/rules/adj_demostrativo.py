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

  rule_name = "adj_demostrativo"

  dep_matcher = DependencyMatcher(nlp.vocab)

  pattern = [
    {
      "RIGHT_ID": "noun",
      "RIGHT_ATTRS": {"POS": "NOUN"}
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">-",
      "RIGHT_ID": "det",
      "RIGHT_ATTRS": {"POS": "DET", "MORPH": {"IS_SUPERSET": ["PronType=Dem"]}, "LEMMA": {"NOT_IN": ["tanto"]}}
    }
  ]

  dep_matcher.add(rule_name, [pattern])

  matches = dep_matcher(doc)
  for index, (_, [noun_id, det_id]) in enumerate(matches):
    det = doc[det_id]
    noun = doc[noun_id]
    raw_matches.append((det_id, det_id+1, {"sign": "det", "det_lemma": det.lemma_, "gid": index})) 
    raw_matches.append((noun_id, noun_id+1, {"sign": "noun", "noun_lemma": noun.lemma_, "gid": index})) 

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
