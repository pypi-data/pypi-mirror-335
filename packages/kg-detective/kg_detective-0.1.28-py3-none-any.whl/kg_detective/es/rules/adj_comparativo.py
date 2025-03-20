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
  dep_matcher = DependencyMatcher(nlp.vocab)

  # mas/menos adj que
  cmp_adj_que = [
    {
      "RIGHT_ID": "adj",
      "RIGHT_ATTRS": {"POS": "ADJ"}
    },
    {
      "LEFT_ID": "adj",
      "REL_OP": ">-",
      "RIGHT_ID": "cmp",
      "RIGHT_ATTRS": {"POS": "ADV", "LOWER": {"IN": ["menos", "más"]}, "MORPH": {"IS_SUPERSET": ["Degree=Cmp"]}}
    },
    {
      "LEFT_ID": "adj",
      "REL_OP": ">++",
      "RIGHT_ID": "obj",
      "RIGHT_ATTRS": {"DEP": {"IN": ["obl", "advcl"]}},
    },
    {
      "LEFT_ID": "obj",
      "REL_OP": ">--",
      "RIGHT_ID": "que",
      "RIGHT_ATTRS": {"DEP": "mark", "LOWER": "que"}
    }
  ]

  # adjer que
  adjer_que = [
    {
      "RIGHT_ID": "adj",
      "RIGHT_ATTRS": {"POS": "ADJ", "MORPH": {"IS_SUPERSET": ["Degree=Cmp"]}}
    },
    {
      "LEFT_ID": "adj",
      "REL_OP": ">++",
      "RIGHT_ID": "obj",
      "RIGHT_ATTRS": {"DEP": {"IN": ["obl", "advcl"]}},
    },
    {
      "LEFT_ID": "obj",
      "REL_OP": ">--",
      "RIGHT_ID": "que",
      "RIGHT_ATTRS": {"DEP": "mark", "LOWER": "que"}
    }
  ] 

  raw_matches = []

  rule_name = "adj_comparativo"

  dep_matcher.add(rule_name, [cmp_adj_que])

  matches = dep_matcher(doc)
  for index, (_, [adj_id, cmp_id, obj_id, que_id]) in enumerate(matches):
    adj_core = doc[adj_id]
    obj_core = doc[obj_id]

    obj_tree = [e.i for e in obj_core.subtree]
    obj_tree.sort()

    obj_assertion = len(obj_tree)==obj_tree[-1]-obj_tree[0]+1
    que_assertion = que_id==obj_tree[0]

    if obj_assertion and que_assertion:
      raw_matches.append((cmp_id, adj_id+1, {"sign": "cmp_adj", "adj_lemma": adj_core.lemma_, "gid": index})) 
      raw_matches.append((que_id, que_id+1, {"sign": "que", "gid": index}))
      raw_matches.append((obj_tree[1], obj_tree[-1]+1, {"sign": "obj", "gid": index}))

  dep_matcher.remove(rule_name)

  base_index = len(raw_matches)//3

  dep_matcher.add(rule_name, [adjer_que])

  matches = dep_matcher(doc)
  for index, (_, [adjer_id, obj_id, que_id]) in enumerate(matches):
    adjer_core = doc[adjer_id]
    obj_core = doc[obj_id]

    obj_tree = [e.i for e in obj_core.subtree]
    obj_tree.sort()

    obj_assertion = len(obj_tree)==obj_tree[-1]-obj_tree[0]+1
    que_assertion = que_id==obj_tree[0]

    if obj_assertion and que_assertion:
      raw_matches.append((adjer_id, adjer_id+1, {"sign": "cmp_adj", "adj_lemma": adjer_core.lemma_, "gid": base_index+index})) 
      raw_matches.append((que_id, que_id+1, {"sign": "que", "gid": base_index+index}))
      raw_matches.append((obj_tree[1], obj_tree[-1]+1, {"sign": "obj", "gid": base_index+index}))

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)

