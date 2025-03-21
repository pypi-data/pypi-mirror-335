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

  rule_name = "subordinada_relativo"

  dep_matcher = DependencyMatcher(nlp.vocab)

  pattern = [
    {
      "RIGHT_ID": "noun",
      "RIGHT_ATTRS": {"POS": {"IN": ["NOUN", "PROPN"]}}
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">++",
      "RIGHT_ID": "acl",
      "RIGHT_ATTRS": {"DEP": "acl"}
    },
    {
      "LEFT_ID": "acl",
      "REL_OP": ">--",
      "RIGHT_ID": "key",
      "RIGHT_ATTRS": {"DEP": {"IN": ["obj", "obl", "nsubj"]}, "POS": "PRON", "LEMMA": {"IN": ["que", "quien", "donde", "adonde"]}}
    },
  ]

  dep_matcher.add(rule_name, [pattern])

  matches = dep_matcher(doc)
  for index, (_, [noun_id, acl_id, _]) in enumerate(matches):
    noun_core = doc[noun_id]
    acl_core = doc[acl_id]

    noun_tree = [e.i for e in noun_core.subtree if e.dep_ not in ["punct"]]
    acl_tree = [e.i for e in acl_core.subtree if e.dep_ not in ["punct"]]
    noun_part = list(set(noun_tree)-set(acl_tree))

    noun_part.sort()
    acl_tree.sort()

    noun_assertion = len(noun_part)==noun_part[-1]-noun_part[0]+1
    acl_assertion = len(acl_tree)==acl_tree[-1]-acl_tree[0]+1

    if noun_assertion and acl_assertion:
      raw_matches.append((noun_part[0], noun_part[-1]+1, {"sign": "noun_part", "gid": index})) 
      raw_matches.append((acl_tree[0], acl_tree[-1]+1, {"sign": "acl", "gid": index})) 

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)

