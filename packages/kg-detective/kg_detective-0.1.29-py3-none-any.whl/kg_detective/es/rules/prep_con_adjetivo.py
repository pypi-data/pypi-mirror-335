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

  dep_matcher = DependencyMatcher(nlp.vocab)
  
  rule_name = "prep_con_adj"

  pattern = [
    {
      "RIGHT_ID": "adj",
      "RIGHT_ATTRS": {"POS": "ADJ"}
    },
    {
      "LEFT_ID": "adj",
      "REL_OP": ">++",
      "RIGHT_ID": "obj",
      "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "acl", "obj"]}}
    },
    {
      "LEFT_ID": "obj",
      "REL_OP": ">--",
      "RIGHT_ID": "prep",
      "RIGHT_ATTRS": {"DEP": {"IN": ["mark", "case"]}, "POS": "ADP"}
    },
  ]

  dep_matcher.add(rule_name, [pattern])

  matches = dep_matcher(doc)
  for index, (_, [adj_id, obj_id, prep_id]) in enumerate(matches):
    adj_core = doc[adj_id]
    obj_core = doc[obj_id]
    obj_tree = [e.i for e in obj_core.subtree]
    obj_tree.sort()

    adj_assertion = not (doc[adj_id-1] in adj_core.children and doc[adj_id-1].dep_=="det")
    obj_assertion = prep_id==obj_tree[0] and len(obj_tree)==obj_tree[-1]-obj_tree[0]+1
    if adj_assertion and obj_assertion:
      raw_matches.append((adj_id, adj_id+1, {"sign": "adj", "adj_lemma": doc[adj_id].lemma_, "gid": index})) 
      raw_matches.append((prep_id, prep_id+1, {"sign": "prep", "gid": index})) 
      raw_matches.append((obj_tree[1], obj_tree[-1]+1, {"sign": "obj", "gid": index})) 

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)

