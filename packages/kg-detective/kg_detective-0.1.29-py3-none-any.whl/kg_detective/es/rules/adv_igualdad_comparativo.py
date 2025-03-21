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

  rule_name = "adv_igualdad_comparativo"

  dep_matcher = DependencyMatcher(nlp.vocab)

  # verb tan adv como obj
  verb_tan_adv_como = [
    {
      "RIGHT_ID": "adv",
      "RIGHT_ATTRS": {"POS": "ADV", "DEP": "advmod"}
    },
    {
      "LEFT_ID": "adv",
      "REL_OP": ">-",
      "RIGHT_ID": "tan",
      "RIGHT_ATTRS": {"POS": "ADV", "LOWER": "tan"}
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
      "RIGHT_ATTRS": {"DEP": {"IN": ["obl"]}},
    },
    {
      "LEFT_ID": "obj",
      "REL_OP": ">--",
      "RIGHT_ID": "como",
      "RIGHT_ATTRS": {"DEP": "mark", "LOWER": "como"}
    }
  ]

  dep_matcher.add(rule_name, [verb_tan_adv_como])

  matches = dep_matcher(doc)
  for index, (_, [adv_id, tan_id, verb_id, obj_id, como_id]) in enumerate(matches):
    adv_core = doc[adv_id]
    verb_core = doc[verb_id]
    obj_core = doc[obj_id]

    obj_tree = [e.i for e in obj_core.subtree]
    obj_tree.sort()

    obj_assertion = len(obj_tree)==obj_tree[-1]-obj_tree[0]+1
    como_assertion = como_id==obj_tree[0]

    if obj_assertion and como_assertion:
      raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": verb_core.lemma_, "gid": index})) 
      raw_matches.append((tan_id, adv_id+1, {"sign": "tan_adv", "adv_lemma": adv_core.lemma_, "gid": index})) 
      raw_matches.append((como_id, como_id+1, {"sign": "como", "gid": index}))
      raw_matches.append((obj_tree[1], obj_tree[-1]+1, {"sign": "obj", "gid": index}))

  dep_matcher.remove(rule_name)

  base_index = len(raw_matches)//4

  # verb tanto como obj
  verb_tanto_como = [
    {
      "RIGHT_ID": "adv",
      "RIGHT_ATTRS": {"POS": "ADV", "LOWER": "tanto"}
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
      "RIGHT_ATTRS": {"DEP": {"IN": ["obl"]}},
    },
    {
      "LEFT_ID": "obj",
      "REL_OP": ">--",
      "RIGHT_ID": "como",
      "RIGHT_ATTRS": {"DEP": "mark", "LOWER": "como"}
    }
  ]

  dep_matcher.add(rule_name, [verb_tanto_como])

  matches = dep_matcher(doc)
  for index, (_, [adv_id, verb_id, obj_id, como_id]) in enumerate(matches):
    adv_core = doc[adv_id]
    verb_core = doc[verb_id]
    obj_core = doc[obj_id]

    obj_tree = [e.i for e in obj_core.subtree]
    obj_tree.sort()

    obj_assertion = len(obj_tree)==obj_tree[-1]-obj_tree[0]+1
    como_assertion = como_id==obj_tree[0]

    if obj_assertion and como_assertion:
      raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": verb_core.lemma_, "gid": index})) 
      raw_matches.append((adv_id, adv_id+1, {"sign": "tan_adv", "adv_lemma": adv_core.lemma_, "gid": index})) 
      raw_matches.append((como_id, como_id+1, {"sign": "como", "gid": index}))
      raw_matches.append((obj_tree[1], obj_tree[-1]+1, {"sign": "obj", "gid": index}))

  dep_matcher.remove(rule_name)

  base_index = len(raw_matches)//4
 
  # verb igual_de_adv_que
  verb_igual_de_adv_que = [
    {
      "RIGHT_ID": "igual",
      "RIGHT_ATTRS": {"POS": "ADV", "LEMMA": "igual"}
    },
    {
      "LEFT_ID": "igual",
      "REL_OP": ">++",
      "RIGHT_ID": "adv",
      "RIGHT_ATTRS": {"POS": "ADV", "DEP": {"IN": ["advmod"]}}
    },
    {
      "LEFT_ID": "adv",
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
    {
      "LEFT_ID": "igual",
      "REL_OP": "<",
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": "VERB"}
    },
  ]

  dep_matcher.add(rule_name, [verb_igual_de_adv_que])

  matches = dep_matcher(doc)
  for index, (_, [igual_id, adv_id, de_id, obj_id, que_id, verb_id]) in enumerate(matches):
    verb_core = doc[verb_id]
    adv_core = doc[adv_id]
    obj_core = doc[obj_id]

    obj_tree = [e.i for e in obj_core.subtree]
    obj_tree.sort()

    obj_assertion = len(obj_tree)==obj_tree[-1]-obj_tree[0]+1
    que_assertion = que_id==obj_tree[0] and que_id==adv_id+1
    adv_assertion = igual_id+1==de_id and de_id+1==adv_id and igual_id>verb_id

    if obj_assertion and que_assertion and adv_assertion:
      raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": verb_core.lemma_, "gid": base_index+index})) 
      raw_matches.append((igual_id, adv_id+1, {"sign": "igual_de_adv", "adv_lemma": adv_core.lemma_, "gid": base_index+index})) 
      raw_matches.append((que_id, que_id+1, {"sign": "que", "gid": base_index+index}))
      raw_matches.append((obj_tree[1], obj_tree[-1]+1, {"sign": "obj", "gid": base_index+index}))

  dep_matcher.remove(rule_name)


  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)

