from spacy.matcher import DependencyMatcher
from kg_detective.lib import clean_merge, mark

def search_out(doc, nlp):
  """Search for adjective for equal comparisons 

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """

  # pattern: as ... as ...
  dep_matcher = DependencyMatcher(nlp.vocab)
  dep_patterns = [
    [
      {
        "RIGHT_ID": "A",
        "RIGHT_ATTRS": {"POS": "ADJ"}
      },
      {
        "LEFT_ID": "A",
        "REL_OP": ">",
        "RIGHT_ID": "left_as",
        "RIGHT_ATTRS": {"DEP": "advmod", "LOWER": {"IN": ["as", "so"]}}
      },
      {
        "LEFT_ID": "A",
        "REL_OP": ">",
        "RIGHT_ID": "right_as",
        "RIGHT_ATTRS": {"DEP": "prep", "LOWER": "as"}
      },
      {
        "LEFT_ID": "right_as",
        "REL_OP": ">",
        "RIGHT_ID": "B",
        "RIGHT_ATTRS": {"DEP": "pobj"}
      },
    ],
    [
      {
        "RIGHT_ID": "same",
        "RIGHT_ATTRS": {"LOWER": "same"}
      },
      {
        "LEFT_ID": "same",
        "REL_OP": ";",
        "RIGHT_ID": "the",
        "RIGHT_ATTRS": {"LOWER": "the"}
      },
      {
        "LEFT_ID": "same",
        "REL_OP": ">",
        "RIGHT_ID": "right_as",
        "RIGHT_ATTRS": {"DEP": "prep", "LOWER": "as"}
      },
      {
        "LEFT_ID": "right_as",
        "REL_OP": ">",
        "RIGHT_ID": "B",
        "RIGHT_ATTRS": {"DEP": "pobj"}
      },
    ],
  ]

  dep_matcher.add("adj_equal_comprison", dep_patterns)
  matches = dep_matcher(doc)

  raw_matches = []
  for index, (_, [adj_core_id, left_as_id, right_as_id, obj_core_id]) in enumerate(matches):
    adj_core = doc[adj_core_id]
    obj_core = doc[obj_core_id]

    adj_subtree = [list(e.subtree) for e in adj_core.children if e.dep_ not in ["cc", "conj", "punct"]]
    adj_tree = [e.i for e in sum(adj_subtree, [])]
    adj_tree.append(adj_core_id)
    adj_tree.sort()
    obj_tree = [e.i for e in obj_core.subtree]
    obj_tree.sort()

    adj_assertion = len(adj_tree) == adj_tree[-1]-adj_tree[0]+1
    obj_assertion = len(obj_tree) == obj_tree[-1]-obj_tree[0]+1 and obj_tree[0]==right_as_id+1

    print(adj_assertion)
    print(obj_assertion)
    if adj_assertion and obj_assertion:    
      raw_matches.append((adj_tree[0], obj_tree[0], {"sign": "as_adj_as", "adj_lemma": adj_core.lemma_, "gid": index}))
      raw_matches.append((obj_tree[0], obj_tree[-1]+1, {"sign": "as_obj", "gid": index}))

  dep_matcher.remove("adj_equal_comprison")

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
