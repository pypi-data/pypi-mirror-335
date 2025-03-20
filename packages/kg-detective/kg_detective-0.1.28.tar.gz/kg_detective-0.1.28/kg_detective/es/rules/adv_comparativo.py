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

  # mas/menos adv que
  cmp_adv_que = [
    {
      "RIGHT_ID": "adv",
      "RIGHT_ATTRS": {"POS": "ADV", "DEP": "advmod"}
    },
    {
      "LEFT_ID": "adv",
      "REL_OP": ">-",
      "RIGHT_ID": "cmp",
      "RIGHT_ATTRS": {"POS": "ADV", "LOWER": {"IN": ["menos", "más"]}, "MORPH": {"IS_SUPERSET": ["Degree=Cmp"]}}
    },
    {
      "LEFT_ID": "adv",
      "REL_OP": "<--",
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": "VERB"} 
    },
    {
      "LEFT_ID": "adv",
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

  # adver que
  adver_que = [
    {
      "RIGHT_ID": "adv",
      "RIGHT_ATTRS": {"POS": "ADV", "MORPH": {"IS_SUPERSET": ["Degree=Cmp"]}, "DEP": "advmod"}
    },
    {
      "LEFT_ID": "adv",
      "REL_OP": "<--",
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": "VERB"} 
    },
    {
      "LEFT_ID": "adv",
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

  rule_name = "adv_comparativo"

  dep_matcher.add(rule_name, [cmp_adv_que])

  matches = dep_matcher(doc)
  for index, (_, [adv_id, cmp_id, verb_id, obj_id, que_id]) in enumerate(matches):
    adv_core = doc[adv_id]
    obj_core = doc[obj_id]

    obj_tree = [e.i for e in obj_core.subtree]
    obj_tree.sort()

    obj_assertion = len(obj_tree)==obj_tree[-1]-obj_tree[0]+1
    que_assertion = que_id==obj_tree[0]

    if obj_assertion and que_assertion:
      raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": doc[verb_id].lemma_, "gid": index})) 
      raw_matches.append((cmp_id, adv_id+1, {"sign": "cmp_adv", "adv_lemma": adv_core.lemma_, "gid": index})) 
      raw_matches.append((que_id, que_id+1, {"sign": "que", "gid": index}))
      raw_matches.append((obj_tree[1], obj_tree[-1]+1, {"sign": "obj", "gid": index}))

  dep_matcher.remove(rule_name)

  base_index = len(raw_matches)//4

  dep_matcher.add(rule_name, [adver_que])

  matches = dep_matcher(doc)
  for index, (_, [adver_id, verb_id, obj_id, que_id]) in enumerate(matches):
    adver_core = doc[adver_id]
    obj_core = doc[obj_id]

    obj_tree = [e.i for e in obj_core.subtree]
    obj_tree.sort()

    obj_assertion = len(obj_tree)==obj_tree[-1]-obj_tree[0]+1
    que_assertion = que_id==obj_tree[0]

    if obj_assertion and que_assertion:
      raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": doc[verb_id].lemma_, "gid": index})) 
      raw_matches.append((adver_id, adver_id+1, {"sign": "cmp_adv", "adv_lemma": adver_core.lemma_, "gid": base_index+index})) 
      raw_matches.append((que_id, que_id+1, {"sign": "que", "gid": base_index+index}))
      raw_matches.append((obj_tree[1], obj_tree[-1]+1, {"sign": "obj", "gid": base_index+index}))

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)

