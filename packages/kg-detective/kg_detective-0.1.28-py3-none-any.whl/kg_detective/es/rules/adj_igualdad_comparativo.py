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

  rule_name = "adj_igualdad_comparativo"

  dep_matcher = DependencyMatcher(nlp.vocab)

  # tan adj como
  tan_adj_como = [
    {
      "RIGHT_ID": "adj",
      "RIGHT_ATTRS": {"POS": "ADJ"}
    },
    {
      "LEFT_ID": "adj",
      "REL_OP": ">-",
      "RIGHT_ID": "tan",
      "RIGHT_ATTRS": {"POS": "ADV", "LOWER": "tan"}
    },
    {
      "LEFT_ID": "adj",
      "REL_OP": ">++",
      "RIGHT_ID": "obj",
      "RIGHT_ATTRS": {"DEP": {"IN": ["obl"]}},
    },
    {
      "LEFT_ID": "obj",
      "REL_OP": ">--",
      "RIGHT_ID": "como",
      "RIGHT_ATTRS": {"DEP": "mark", "LOWER": "como"}
    }
  ]

  dep_matcher.add(rule_name, [tan_adj_como])

  matches = dep_matcher(doc)
  for index, (_, [adj_id, tan_id, obj_id, como_id]) in enumerate(matches):
    adj_core = doc[adj_id]
    obj_core = doc[obj_id]

    obj_tree = [e.i for e in obj_core.subtree]
    obj_tree.sort()

    obj_assertion = len(obj_tree)==obj_tree[-1]-obj_tree[0]+1
    como_assertion = como_id==obj_tree[0]

    if obj_assertion and como_assertion:
      raw_matches.append((tan_id, adj_id+1, {"sign": "tan_adj", "adj_lemma": adj_core.lemma_, "gid": index})) 
      raw_matches.append((como_id, como_id+1, {"sign": "como", "gid": index}))
      raw_matches.append((obj_tree[1], obj_tree[-1]+1, {"sign": "obj", "gid": index}))

  dep_matcher.remove(rule_name)

  base_index = len(raw_matches)//3

  igual_de_adj_que = [
    {
      "RIGHT_ID": "igual",
      "RIGHT_ATTRS": {"POS": "ADJ", "LEMMA": "igual"}
    },
    {
      "LEFT_ID": "igual",
      "REL_OP": ">++",
      "RIGHT_ID": "adj",
      "RIGHT_ATTRS": {"POS": "ADJ", "DEP": {"IN": ["nmod", "amod"]}}
    },
    {
      "LEFT_ID": "adj",
      "REL_OP": ">-",
      "RIGHT_ID": "de",
      "RIGHT_ATTRS": {"DEP": "case", "LEMMA": "de"}
    },
    {
      "LEFT_ID": "igual",
      "REL_OP": ">++",
      "RIGHT_ID": "obj",
      "RIGHT_ATTRS": {"DEP": "obl"}
    },
    {
      "LEFT_ID": "obj",
      "REL_OP": ">--",
      "RIGHT_ID": "que",
      "RIGHT_ATTRS": {"DEP": "mark", "LEMMA": "que"}
    },
  ]

  dep_matcher.add(rule_name, [igual_de_adj_que])

  matches = dep_matcher(doc)
  for index, (_, [igual_id, adj_id, de_id, obj_id, que_id]) in enumerate(matches):
    adj_core = doc[adj_id]
    obj_core = doc[obj_id]

    obj_tree = [e.i for e in obj_core.subtree]
    obj_tree.sort()

    obj_assertion = len(obj_tree)==obj_tree[-1]-obj_tree[0]+1
    que_assertion = que_id==obj_tree[0] and que_id==adj_id+1
    adj_assertion = igual_id+1==de_id and de_id+1==adj_id

    if obj_assertion and que_assertion and adj_assertion:
      raw_matches.append((igual_id, adj_id+1, {"sign": "igual_de_adj", "adj_lemma": adj_core.lemma_, "gid": base_index+index})) 
      raw_matches.append((que_id, que_id+1, {"sign": "que", "gid": base_index+index}))
      raw_matches.append((obj_tree[1], obj_tree[-1]+1, {"sign": "obj", "gid": base_index+index}))

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)

