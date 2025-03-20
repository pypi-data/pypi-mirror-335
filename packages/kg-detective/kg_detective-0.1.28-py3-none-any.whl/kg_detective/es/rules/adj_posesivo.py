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

  rule_name = "adj_posesivo"

  dep_matcher = DependencyMatcher(nlp.vocab)

  # poss noun
  pattern = [
    {
      "RIGHT_ID": "noun",
      "RIGHT_ATTRS": {"POS": "NOUN"}
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">--",
      "RIGHT_ID": "poss",
      "RIGHT_ATTRS": {"POS": "DET", "MORPH": {"IS_SUPERSET": ["Poss=Yes"]}}
    }
  ]

  dep_matcher.add(rule_name, [pattern])

  matches = dep_matcher(doc)
  for index, (_, [noun_id, poss_id]) in enumerate(matches):
    raw_matches.append((poss_id, noun_id+1, {"sign": "poss_noun", "gid": index})) 

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)

