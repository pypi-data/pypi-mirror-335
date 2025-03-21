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

  rule_name = "subordinada_substantivo"

  dep_matcher = DependencyMatcher(nlp.vocab)

  pattern = [
    {
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": {"IN": ["VERB"]}}
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">++",
      "RIGHT_ID": "noun_clause",
      "RIGHT_ATTRS": {"DEP": {"IN": ["ccomp", "csubj"]}}
    },
    {
      "LEFT_ID": "noun_clause",
      "REL_OP": ">--",
      "RIGHT_ID": "sconj",
      "RIGHT_ATTRS": {"DEP": "mark", "POS": "SCONJ"},
    },
  ]

  dep_matcher.add(rule_name, [pattern])

  matches = dep_matcher(doc)
  for index, (_, [verb_id, clause_id, _]) in enumerate(matches):
    verb_core = doc[verb_id]
    clause_core = doc[clause_id]

    clause_tree = [e.i for e in clause_core.subtree]
    clause_tree.sort()

    clause_assertion = len(clause_tree)==clause_tree[-1]-clause_tree[0]+1

    if clause_assertion:
      # TODO: verb tree 
      raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": verb_core.lemma_, "gid": index})) 
      raw_matches.append((clause_tree[0], clause_tree[-1]+1, {"sign": "acl", "gid": index})) 

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)

