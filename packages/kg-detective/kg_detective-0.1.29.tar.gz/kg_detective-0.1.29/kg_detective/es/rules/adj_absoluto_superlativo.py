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

  rule_name = "adj_absoluto_superlativo"

  dep_matcher = DependencyMatcher(nlp.vocab)

  pattern = [
    {
      "RIGHT_ID": "adj",
      "RIGHT_ATTRS": {"POS": "ADJ", "MORPH": {"IS_SUPERSET": ["Degree=Abs"]}}
    }
  ]

  dep_matcher.add(rule_name, [pattern])

  matches = dep_matcher(doc)
  for index, (_, [adj_id]) in enumerate(matches):
    adj_core = doc[adj_id]
    raw_matches.append((adj_id, adj_id+1, {"sign": "adjest", "adj_lemma": adj_core.lemma_, "gid": index})) 

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)

