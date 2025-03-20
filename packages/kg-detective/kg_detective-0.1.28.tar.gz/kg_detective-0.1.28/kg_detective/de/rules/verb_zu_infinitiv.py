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

  dep_patterns_1 = [
    [
      {
        "RIGHT_ID": "zu_in_verb",
        "RIGHT_ATTRS": {"TAG": "VVIZU"}
      },
    ],
  ]
  dep_matcher.add("zu_in_verb", dep_patterns_1)

  dep_patterns_2 = [
    [
      {
        "RIGHT_ID": "verb",
        "RIGHT_ATTRS": {"TAG": {"IN": ["VVINF", "VMINF"]}}
      },
      {
        "LEFT_ID": "verb",
        "REL_OP": ">",
        "RIGHT_ID": "zu",
        "RIGHT_ATTRS": {"DEP": "pm", "TAG": "PTKZU", "LOWER": "zu"}
      },
    ],
  ]
  dep_matcher.add("zu_verb", dep_patterns_2)
  matches = dep_matcher(doc)

  #match_name = nlp.vocab.strings[match_id]
  for match_id, seq in matches:
    span_ids = seq 
    verb_token = doc[seq[0]] 
    verb_aux = verb_token.head
    if verb_token.dep_ == "oc" and verb_aux.pos_ in ["AUX", "VERB"] and verb_aux.tag_ in ["VAFIN", "VMFIN", "VVFIN"]:
      span_ids.append(verb_aux.i)

    sorted_span_ids = sorted(span_ids)
    span_text = " ".join([doc[e].text for e in sorted_span_ids])
    result.append({"text": span_text})

  return result
   
