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
        "RIGHT_ATTRS": {"POS": "AUX", "TAG": "VAFIN", "LEMMA": "werden", "MORPH": {"IS_SUPERSET": ["Tense=Pres", "Mood=Ind"]}}
      },
      {
        "LEFT_ID": "aux",
        "REL_OP": ">",
        "RIGHT_ID": "verb",
        "RIGHT_ATTRS": {"DEP": "oc", "TAG": "VVINF"}
      },
    ],
  ]
  dep_matcher.add("verb_tempus_futur_1", dep_patterns)
  matches = dep_matcher(doc)

  for _, (aux, verb) in matches:
    span_ids = [aux, verb]
   
    sorted_span_ids = sorted(span_ids)
    span_text = " ".join([doc[e].text for e in sorted_span_ids])
    result.append({"text": span_text})


  return result
   
