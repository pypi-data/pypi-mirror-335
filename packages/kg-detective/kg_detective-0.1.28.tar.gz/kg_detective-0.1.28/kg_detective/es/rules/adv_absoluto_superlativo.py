from spacy.matcher import Matcher, PhraseMatcher, DependencyMatcher
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

  rule_name = "adv_absoluto_superlativo"

  dep_matcher = DependencyMatcher(nlp.vocab)

  pattern = [
    {
      "RIGHT_ID": "adv",
      "RIGHT_ATTRS": {"POS": "ADV", "MORPH": {"IS_SUPERSET": ["Degree=Abs"]}}
    }
  ]

  dep_matcher.add(rule_name, [pattern])

  matches = dep_matcher(doc)
  for index, (_, [adv_id]) in enumerate(matches):
    adv_core = doc[adv_id]
    raw_matches.append((adv_id, adv_id+1, {"sign": "advest", "adv_lemma": adv_core.lemma_, "gid": index})) 

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)

