from spacy.matcher import DependencyMatcher
from kg_detective.lib import clean_merge, mark

def search_out(doc, nlp):
  """Search for transitive verbs   

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """

  dep_matcher = DependencyMatcher(nlp.vocab)

  #verb_dative_obj
  verb_dative_obj = [
    {
      "RIGHT_ID": "core_verb",
      "RIGHT_ATTRS": {"POS": "VERB"}
    },
    {
      "LEFT_ID": "core_verb",
      "REL_OP": ">++",
      "RIGHT_ID": "dobj",
      "RIGHT_ATTRS": {"DEP": {"IN": ["dobj"]}}
    },
    {
      "LEFT_ID": "core_verb",
      "REL_OP": ">++",
      "RIGHT_ID": "dative",
      "RIGHT_ATTRS": {"DEP": {"IN": ["dative"]}}
    },
  ]

  #verb_prt_obj
  verb_prt_obj = [
    {
      "RIGHT_ID": "core_verb",
      "RIGHT_ATTRS": {"POS": "VERB"}
    },
    {
      "LEFT_ID": "core_verb",
      "REL_OP": ">++",
      "RIGHT_ID": "dobj",
      "RIGHT_ATTRS": {"DEP": {"IN": ["dobj"]}}
    },
    {
      "LEFT_ID": "core_verb",
      "REL_OP": ">++",
      "RIGHT_ID": "dative",
      "RIGHT_ATTRS": {"DEP": {"IN": ["prt"]}, "POS": {"IN": ["ADP", "ADV"]}}
    },
  ]

  verb_obj = [
    {
      "RIGHT_ID": "core_verb",
      "RIGHT_ATTRS": {"POS": "VERB"}
    },
    {
      "LEFT_ID": "core_verb",
      "REL_OP": ">++",
      "RIGHT_ID": "dobj",
      "RIGHT_ATTRS": {"DEP": {"IN": ["dobj"]}}
    },
  ]

  dep_matcher.add("verb_transitive", [verb_dative_obj])
  matches = dep_matcher(doc)

  raw_matches = []
  for index, (_, [verb_id, obj_id, dative_id]) in enumerate(matches):
    obj_tree = [e.i for e in doc[obj_id].subtree]
    obj_assertion = obj_tree[-1]-obj_tree[0]+1==len(obj_tree)

    dative_tree = [e.i for e in doc[dative_id].subtree]
    dative_assertion = dative_tree[-1]-dative_tree[0]+1==len(dative_tree)

    if obj_assertion and dative_assertion:
      raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": doc[verb_id].lemma_, "gid": index}))
      raw_matches.append((dative_tree[0], dative_tree[-1]+1, {"sign": "dative", "gid": index}))
      raw_matches.append((obj_tree[0], obj_tree[-1]+1, {"sign": "obj", "gid": index}))

  dep_matcher.remove("verb_transitive")

  base_index = len(raw_matches)
  dep_matcher.add("verb_transitive", [verb_prt_obj])
  matches = dep_matcher(doc)
  for index, (_, [verb_id, obj_id, prt_id]) in enumerate(matches):
    obj_tree = [e.i for e in doc[obj_id].subtree]
    obj_assertion = obj_tree[-1]-obj_tree[0]+1==len(obj_tree)

    if obj_assertion:
      raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": doc[verb_id].lemma_, "gid": base_index+index}))
      raw_matches.append((prt_id, prt_id+1, {"sign": "prt", "gid": base_index+index}))
      raw_matches.append((obj_tree[0], obj_tree[-1]+1, {"sign": "obj", "gid": base_index+index}))

  dep_matcher.remove("verb_transitive")

  base_index = len(raw_matches)
  dep_matcher.add("verb_transitive", [verb_obj])
  matches = dep_matcher(doc)

  for index, (_, [verb_id, obj_id]) in enumerate(matches):
    obj_tree = [e.i for e in doc[obj_id].subtree]

    obj_assertion = verb_id<obj_id and obj_tree[-1]-obj_tree[0]+1==len(obj_tree)

    if obj_assertion:
      raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": doc[verb_id].lemma_, "gid": base_index+index}))
      raw_matches.append((obj_tree[0], obj_tree[-1]+1, {"sign": "obj", "gid": base_index+index}))

  dep_matcher.remove("verb_transitive")

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
