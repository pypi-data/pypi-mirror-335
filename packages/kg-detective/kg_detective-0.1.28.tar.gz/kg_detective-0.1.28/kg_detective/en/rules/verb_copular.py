from spacy.matcher import DependencyMatcher
from kg_detective.lib import clean_merge, mark

def search_out(doc, nlp):
  """Search for copular verbs   

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """

  dep_matcher = DependencyMatcher(nlp.vocab)

  attr_dep = [
    {
      "RIGHT_ID": "core_verb",
      "RIGHT_ATTRS": {"POS": "VERB", "LEMMA": "become"}
    },
    {
      "LEFT_ID": "core_verb",
      "REL_OP": ">",
      "RIGHT_ID": "attr",
      "RIGHT_ATTRS": {"DEP": "attr"}
    },
  ]
  acomp_dep = [
    {
      "RIGHT_ID": "core_verb",
      "RIGHT_ATTRS": {"POS": {"IN": ["VERB", "AUX"]}, "LEMMA": {"IN": ["come", "look", "sound", "taste", "be", "smell", "go", "get", "feel"]}}
    },
    {
      "LEFT_ID": "core_verb",
      "REL_OP": ">",
      "RIGHT_ID": "acomp",
      "RIGHT_ATTRS": {"DEP": {"IN": ["acomp", "advcl"]}}
    }
  ]

  oprd_dep = [
    {
      "RIGHT_ID": "core_verb",
      "RIGHT_ATTRS": {"POS": {"IN": ["VERB"]}, "LEMMA": {"IN": ["appear"]}}
    },
    {
      "LEFT_ID": "core_verb",
      "REL_OP": ">",
      "RIGHT_ID": "oprd",
      "RIGHT_ATTRS": {"DEP": "oprd"}
    }
  ]


  dep_patterns = [attr_dep, acomp_dep, oprd_dep]
  dep_matcher.add("verb_copular", dep_patterns)
  matches = dep_matcher(doc)

  raw_matches = []
  for index, (_, [copular_id, pred_id]) in enumerate(matches):
    pred_tree = [e.i for e in doc[pred_id].subtree]
    pred_tree.sort()

    copular_assertion = copular_id<pred_id
    pred_tree_assertion = len(pred_tree)==pred_tree[-1]-pred_tree[0]+1 

    if copular_assertion and pred_tree_assertion:
      raw_matches.append((copular_id, copular_id+1, {"sign": "copular_part", "copular_lemma": doc[copular_id].lemma_, "gid": index}))
      raw_matches.append((pred_tree[0], pred_tree[-1]+1, {"sign": "pred_part", "gid": index}))

  dep_matcher.remove("verb_copular")

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
