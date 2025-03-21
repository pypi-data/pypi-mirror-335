from spacy.matcher import Matcher, PhraseMatcher, DependencyMatcher
from kg_detective.lib import merge

def search_out(doc, nlp):
  """Search for  

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """
  result = []

  dep_matcher = DependencyMatcher(nlp.vocab)
  dep_patterns = [
    [
      {
        "RIGHT_ID": "aux",
        "RIGHT_ATTRS": {"POS": "AUX", "LEMMA": "werden"}
      },
      {
        "LEFT_ID": "aux",
        "REL_OP": ">",
        "RIGHT_ID": "verb",
        "RIGHT_ATTRS": {"DEP": "oc", "TAG": "VVPP"}
      },
    ],
  ]
  dep_matcher.add("verb_genus_passiv", dep_patterns)
  matches = dep_matcher(doc)

  for _, (aux, verb) in matches:
    span_ids = [aux, verb]
    aux_token = doc[aux] 
    aux_aux = aux_token.head
    if aux_token.dep_ == "oc" and aux_aux.pos_ == "AUX" and aux_aux.tag_ in ["VAFIN", "VMFIN"]:
      span_ids.append(aux_aux.i)
    sbp_token_ids = [e.i for e in doc[verb].children if e.dep_ == "sbp"]
    if len(sbp_token_ids) == 1:
      sbp = doc[sbp_token_ids[0]]
      sbp_tree_ids = [e.i for e in sbp.subtree]
      span_ids.extend(sbp_tree_ids)
    sorted_span_ids = sorted(span_ids)
    span_text = " ".join([doc[e].text for e in sorted_span_ids])
    result.append({"text": span_text})


  return result
   
