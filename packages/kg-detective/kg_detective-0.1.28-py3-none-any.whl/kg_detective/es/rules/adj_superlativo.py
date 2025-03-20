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

  dep_matcher = DependencyMatcher(nlp.vocab)

  rule_name = "adj_superlativo"

  # adj_core: el/los/la/las mas/menos adj de
  det_cmp_adj_de = [
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
      "REL_OP": ">--",
      "RIGHT_ID": "det",
      "RIGHT_ATTRS": {"POS": "DET", "LEMMA": "el"}
    },
    {
      "LEFT_ID": "adj",
      "REL_OP": ">++",
      "RIGHT_ID": "obj",
      "RIGHT_ATTRS": {"DEP": {"IN": ["nmod"]}},
    },
    {
      "LEFT_ID": "obj",
      "REL_OP": ">--",
      "RIGHT_ID": "de",
      "RIGHT_ATTRS": {"DEP": {"IN": ["case"]}, "LOWER": {"IN": ["de", "del"]}}
    }
  ]
  dep_matcher.add(rule_name, [det_cmp_adj_de])

  matches = dep_matcher(doc)
  for index, (_, [adj_id, cmp_id, det_id, obj_id, de_id]) in enumerate(matches):
    adj_core = doc[adj_id]
    obj_core = doc[obj_id]

    obj_tree = [e.i for e in obj_core.subtree]
    obj_tree.sort()

    adj_assertion = det_id+1==cmp_id
    obj_assertion = len(obj_tree)==obj_tree[-1]-obj_tree[0]+1
    de_assertion = de_id==obj_tree[0]

    if adj_assertion and obj_assertion and de_assertion:
      raw_matches.append((det_id, adj_id+1, {"sign": "det_cmp_adj", "adj_lemma": adj_core.lemma_, "gid": index})) 
      raw_matches.append((de_id, de_id+1, {"sign": "de", "gid": index}))
      raw_matches.append((obj_tree[1], obj_tree[-1]+1, {"sign": "obj", "gid": index}))

  dep_matcher.remove(rule_name)

  base_index = len(raw_matches)//3

  # adj_core: el/los/la/las adjer de
  det_adjer_prep = [
    {
      "RIGHT_ID": "adj",
      "RIGHT_ATTRS": {"POS": "ADJ", "MORPH": {"IS_SUPERSET": ["Degree=Cmp"]}}
    },
    {
      "LEFT_ID": "adj",
      "REL_OP": ">-",
      "RIGHT_ID": "det",
      "RIGHT_ATTRS": {"POS": "DET", "LEMMA": "el"}
    },
    {
      "LEFT_ID": "adj",
      "REL_OP": ">++",
      "RIGHT_ID": "obj",
      "RIGHT_ATTRS": {"DEP": {"IN": ["nmod"]}},
    },
    {
      "LEFT_ID": "obj",
      "REL_OP": ">--",
      "RIGHT_ID": "de",
      "RIGHT_ATTRS": {"DEP": {"IN": ["case"]}, "LOWER": {"IN": ["de", "del"]}}
    }
  ]

  dep_matcher.add(rule_name, [det_adjer_prep])

  matches = dep_matcher(doc)
  for index, (_, [adjer_id, det_id, obj_id, de_id]) in enumerate(matches):
    adjer_core = doc[adjer_id]
    obj_core = doc[obj_id]

    obj_tree = [e.i for e in obj_core.subtree]
    obj_tree.sort()

    adjer_assertion = det_id+1==adjer_id
    obj_assertion = len(obj_tree)==obj_tree[-1]-obj_tree[0]+1
    de_assertion = de_id==obj_tree[0]

    if adjer_assertion and obj_assertion and de_assertion:
      raw_matches.append((det_id, adjer_id+1, {"sign": "det_adjer", "adj_lemma": adjer_core.lemma_, "gid": base_index+index})) 
      raw_matches.append((de_id, de_id+1, {"sign": "de", "gid": base_index+index}))
      raw_matches.append((obj_tree[1], obj_tree[-1]+1, {"sign": "obj", "gid": base_index+index}))

  dep_matcher.remove(rule_name)

  base_index = len(raw_matches)//3

  # noun_core: el/los/la/las mas/menos adj noun de
  det_cmp_adj_noun_de = [
    {
      "RIGHT_ID": "noun",
      "RIGHT_ATTRS": {"POS": "NOUN"}
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">--",
      "RIGHT_ID": "det",
      "RIGHT_ATTRS": {"POS": "DET", "LEMMA": "el"}
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">",
      "RIGHT_ID": "adj",
      "RIGHT_ATTRS": {"DEP": {"IN": ["amod"]}},
    },
    {
      "LEFT_ID": "adj",
      "REL_OP": ">-",
      "RIGHT_ID": "cmp",
      "RIGHT_ATTRS": {"POS": "ADV", "DEP": "advmod", "LOWER": {"IN": ["menos", "más"]}, "MORPH": {"IS_SUPERSET": ["Degree=Cmp"]}}
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">",
      "RIGHT_ID": "obj",
      "RIGHT_ATTRS": {"DEP": {"IN": ["nmod"]}},
    },
    {
      "LEFT_ID": "obj",
      "REL_OP": ">--",
      "RIGHT_ID": "de",
      "RIGHT_ATTRS": {"DEP": {"IN": ["case"]}, "LOWER": {"IN": ["de", "del"]}}
    }
  ]
  dep_matcher.add(rule_name, [det_cmp_adj_noun_de])

  matches = dep_matcher(doc)
  for index, (_, [noun_id, det_id, adj_id, cmp_id, obj_id, de_id]) in enumerate(matches):
    adj_core = doc[adj_id]
    obj_core = doc[obj_id]

    obj_tree = [e.i for e in obj_core.subtree]
    obj_tree.sort()

    obj_assertion = len(obj_tree)==obj_tree[-1]-obj_tree[0]+1
    de_assertion = de_id==obj_tree[0]

    if obj_assertion and de_assertion:
      raw_matches.append((det_id, max(adj_id, noun_id)+1, {"sign": "noun_core", "adj_lemma": adj_core.lemma_, "gid": base_index+index})) 
      raw_matches.append((de_id, de_id+1, {"sign": "de", "gid": base_index+index}))
      raw_matches.append((obj_tree[1], obj_tree[-1]+1, {"sign": "obj", "gid": base_index+index}))

  dep_matcher.remove(rule_name)

  base_index = len(raw_matches)//3

  # noun_core: el/los/la/las adjer noun de
  det_adjer_noun_de = [
    {
      "RIGHT_ID": "noun",
      "RIGHT_ATTRS": {"POS": "NOUN"}
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">--",
      "RIGHT_ID": "det",
      "RIGHT_ATTRS": {"POS": "DET", "LEMMA": "el"}
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">",
      "RIGHT_ID": "adjer",
      "RIGHT_ATTRS": {"DEP": {"IN": ["amod"]}, "MORPH": {"IS_SUPERSET": ["Degree=Cmp"]}},
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">",
      "RIGHT_ID": "obj",
      "RIGHT_ATTRS": {"DEP": {"IN": ["nmod"]}},
    },
    {
      "LEFT_ID": "obj",
      "REL_OP": ">--",
      "RIGHT_ID": "de",
      "RIGHT_ATTRS": {"DEP": {"IN": ["case"]}, "LOWER": {"IN": ["de", "del"]}}
    }
  ]
  dep_matcher.add(rule_name, [det_adjer_noun_de])

  matches = dep_matcher(doc)
  for index, (_, [noun_id, det_id, adjer_id, obj_id, de_id]) in enumerate(matches):
    adjer_core = doc[adjer_id]
    obj_core = doc[obj_id]

    obj_tree = [e.i for e in obj_core.subtree]
    obj_tree.sort()

    obj_assertion = len(obj_tree)==obj_tree[-1]-obj_tree[0]+1
    de_assertion = de_id==obj_tree[0]

    if obj_assertion and de_assertion:
      raw_matches.append((det_id, max(adjer_id, noun_id)+1, {"sign": "noun_core", "adj_lemma": adjer_core.lemma_, "gid": base_index+index})) 
      raw_matches.append((de_id, de_id+1, {"sign": "de", "gid": base_index+index}))
      raw_matches.append((obj_tree[1], obj_tree[-1]+1, {"sign": "obj", "gid": base_index+index}))

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)

