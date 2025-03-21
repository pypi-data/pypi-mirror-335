from spacy.matcher import DependencyMatcher
from kg_detective.lib import combine_merge, mark

def search_out(doc, nlp):
  """Search for proper nouns 

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """

  dep_matcher = DependencyMatcher(nlp.vocab)

  # propn
  propn = [
    {
      "RIGHT_ID": "propn",
      "RIGHT_ATTRS": {"POS": "PROPN"}
    },
  ]

  # propn_noun
  propn_noun = [
    {
      "RIGHT_ID": "noun",
      "RIGHT_ATTRS": {"POS": "NOUN"}
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">",
      "RIGHT_ID": "propn",
      "RIGHT_ATTRS": {"POS": "PROPN"}
    },
  ]

  dep_matcher.add("noun_proper", [propn, propn_noun])

  matches = dep_matcher(doc)

  raw_matches = []

  for index, (_, ids) in enumerate(matches):
    core = doc[ids[0]]
    tree = [e.i for e in core.subtree]
    tree.sort()
    propn_assertion = len(tree)>1 and len(tree)==tree[-1]-tree[0]+1

    if propn_assertion:
      raw_matches.append((tree[0], tree[-1]+1, {"sign": "propn", "gid": index}))

  dep_matcher.remove("noun_proper")
  refined_matches = combine_merge(raw_matches)

  return mark(doc, refined_matches)
