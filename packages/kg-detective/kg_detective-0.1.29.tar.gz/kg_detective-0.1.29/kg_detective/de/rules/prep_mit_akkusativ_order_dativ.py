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
        "RIGHT_ID": "verb",
        "RIGHT_ATTRS": {"POS": "VERB"}
      },
      {
        "LEFT_ID": "verb",
        "REL_OP": ">",
        "RIGHT_ID": "prep",
        "RIGHT_ATTRS": {"DEP": "mo", "POS": "ADP"}
      },
      {
        "LEFT_ID": "prep",
        "REL_OP": ">",
        "RIGHT_ID": "akk",
        "RIGHT_ATTRS": {"DEP": "nk", "POS": {"IN": ["NOUN", "PRON", "PROPN"]}, "MORPH": {"IS_SUPERSET": ["Case=Acc"]}}
      },
    ],
    [
      {
        "RIGHT_ID": "verb",
        "RIGHT_ATTRS": {"POS": "VERB"}
      },
      {
        "LEFT_ID": "verb",
        "REL_OP": ">",
        "RIGHT_ID": "prep",
        "RIGHT_ATTRS": {"DEP": "mo", "POS": "ADP"}
      },
      {
        "LEFT_ID": "prep",
        "REL_OP": ">",
        "RIGHT_ID": "dat",
        "RIGHT_ATTRS": {"DEP": "nk", "POS": {"IN": ["NOUN", "PRON", "PROPN"]}, "MORPH": {"IS_SUPERSET": ["Case=Dat"]}}
      },
    ],
  ]
  dep_matcher.add("prep_mit_akkusativ_order_dativ", dep_patterns)
  matches = dep_matcher(doc)

  for _, (verb, prep, obj) in matches:
    span_ids = [verb, prep]
    obj_ids = [e.i for e in doc[obj].subtree]
    span_ids.extend(obj_ids)
    sorted_span_ids = sorted(span_ids)
    span_text = " ".join([doc[e].text for e in sorted_span_ids])
    result.append({"text": span_text})


  return result
   
