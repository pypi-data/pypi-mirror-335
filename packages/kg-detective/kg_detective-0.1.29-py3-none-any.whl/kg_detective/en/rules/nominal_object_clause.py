from spacy.matcher import DependencyMatcher
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
  excluded_lemmas = ["be", "let", "want", "make", "help", "allow", "seem"]
  dep_patterns = [
    [
      {
        "RIGHT_ID": "verb",
        "RIGHT_ATTRS": {"POS": {"IN": ["VERB", "AUX"]}, "DEP": {"IN": ["ROOT"]}, "LEMMA": {"NOT_IN": excluded_lemmas}}
      },
      {
        "LEFT_ID": "verb",
        "REL_OP": ">--",
        "RIGHT_ID": "subj",
        "RIGHT_ATTRS": {"DEP": "nsubj"}
      },
      {
        "LEFT_ID": "verb",
        "REL_OP": ">++",
        "RIGHT_ID": "obj",
        "RIGHT_ATTRS": {"DEP": "ccomp", "POS": {"IN": ["VERB", "AUX"]}}
      },
      {
        "LEFT_ID": "obj",
        "REL_OP": ">>",
        "RIGHT_ID": "sconj",
        "RIGHT_ATTRS": {"POS": "SCONJ"}
      }
    ],
  ]
  dep_matcher.add("nominal_object_clause", dep_patterns)
  matches = dep_matcher(doc)

  raw_matches = []
  for index, (_, [verb_id, _, clause_id, sconj_id]) in enumerate(matches):
    obj_tree = [e.i for e in doc[clause_id].subtree]
    obj_tree.sort()

    obj_assertion = len(obj_tree) == obj_tree[-1]-obj_tree[0]+1 and sconj_id < clause_id
    if obj_assertion:
      raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": doc[verb_id].lemma_, "gid": index}))
      raw_matches.append((obj_tree[0], obj_tree[-1]+1, {"sign":"obj_clause", "gid": index})) 

  dep_matcher.remove("nominal_object_clause")

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
