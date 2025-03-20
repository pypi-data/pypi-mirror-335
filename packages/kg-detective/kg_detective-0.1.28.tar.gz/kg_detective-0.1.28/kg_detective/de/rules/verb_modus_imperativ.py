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
        "RIGHT_ATTRS": {"TAG": "VVIMP", "MORPH": {"IS_SUPERSET": ["Mood=Imp"]}}
      },
    ],
  ]
  dep_matcher.add("verb_modus_imperativ", dep_patterns)
  matches = dep_matcher(doc)

  for _, (verb, ) in matches:
    span_ids = [verb]
    svp_token_ids = [e.i for e in doc[verb].children if e.dep_=="svp"]
    if len(svp_token_ids) == 1:
      span_ids.append(svp_token_ids[0])
    
    sorted_span_ids = sorted(span_ids)
    span_text = " ".join([doc[e].text for e in sorted_span_ids])
    result.append({"text": span_text})


  return result
   
