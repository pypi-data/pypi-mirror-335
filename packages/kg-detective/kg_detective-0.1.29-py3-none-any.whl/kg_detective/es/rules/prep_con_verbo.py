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

  rule_name = "prep_con_verb"

  dep_matcher = DependencyMatcher(nlp.vocab)

  pattern = [
    {
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": "VERB"}
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">++",
      "RIGHT_ID": "x",
      "RIGHT_ATTRS": {"DEP": {"IN": ["xcomp"]}}
    },
    {
      "LEFT_ID": "x",
      "REL_OP": ">--",
      "RIGHT_ID": "prep",
      "RIGHT_ATTRS": {"DEP": {"IN": ["mark"]}, "POS": "ADP"}
    },
  ]

  dep_matcher.add(rule_name, [pattern])

  matches = dep_matcher(doc)
  for index, (_, [verb_id, x_id, prep_id]) in enumerate(matches):
    verb_core = doc[verb_id]
    verb_tree = sum([list(e.subtree) for e in verb_core.lefts if e.dep_ in ["expl:pv", "aux", "mark"]],[])
    verb_tree = [e.i for e in verb_tree] 
    verb_tree.append(verb_id)
    verb_tree.sort()
    
    x_core = doc[x_id]
    x_tree = [e.i for e in list(x_core.subtree)]
    x_tree.sort()

    verb_assertion = len(verb_tree)==verb_tree[-1]-verb_tree[0]+1
    x_assertion = x_tree[0]==prep_id

    if verb_assertion and x_assertion:
      raw_matches.append((verb_tree[0], verb_tree[-1]+1, {"sign": "verb", "verb_lemma": verb_core.lemma_, "gid": index})) 
      raw_matches.append((prep_id, prep_id+1, {"sign": "prep", "gid": index})) 
      raw_matches.append((x_tree[1], x_tree[-1]+1, {"sign": "x", "gid": index})) 

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)

