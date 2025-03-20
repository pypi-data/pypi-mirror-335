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

  rule_name = "noun_propio"

  dep_matcher = DependencyMatcher(nlp.vocab)

  pattern = [
    {
      "RIGHT_ID": "propn",
      "RIGHT_ATTRS": {"POS": "PROPN"}
    }
  ]

  dep_matcher.add(rule_name, [pattern])

  matches = dep_matcher(doc)
  for index, (_, [propn_id]) in enumerate(matches):
    propn_core = doc[propn_id]
    propn_tree = [list(e.subtree) for e in propn_core.children if e.dep_ in ["flat", "det"]]
    propn_tree = [e.i for e in sum(propn_tree, [])]
    propn_tree.append(propn_id)
    propn_tree.sort()
    propn_assertion = len(propn_tree)==propn_tree[-1]-propn_tree[0]+1
    if propn_assertion:
      raw_matches.append((propn_tree[0], propn_tree[-1]+1, {"sign": "propn", "gid": index})) 

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
