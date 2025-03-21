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
        "RIGHT_ID": "verb_konjunktiv_2",
        "RIGHT_ATTRS": {"POS": {"IN": ["VERB", "AUX"]}, "MORPH": {"IS_SUPERSET" : ["Mood=Sub"]}}
      },
      {
        "LEFT_ID": "verb_konjunktiv_2",
        "REL_OP": ">",
        "RIGHT_ID": "verb",
        "RIGHT_ATTRS": {"DEP": "oc", "POS": {"IN": ["VERB", "AUX"]}}
      },
    ],
  ]
  dep_matcher.add("verb_modus_konjunktiv_2", dep_patterns)
  matches = dep_matcher(doc)

  for _, (verb_konjunktiv, verb) in matches:
    span_ids = [verb_konjunktiv, verb]
    verb_more = [e.i for e in doc[verb].children if e.dep_ == "oc" and e.pos_ == "VERB"]
    span_ids.extend(verb_more)
    
    sorted_span_ids = sorted(span_ids)
    span_text = " ".join([doc[e].text for e in sorted_span_ids])
    result.append({"text": span_text})


  return result
   
