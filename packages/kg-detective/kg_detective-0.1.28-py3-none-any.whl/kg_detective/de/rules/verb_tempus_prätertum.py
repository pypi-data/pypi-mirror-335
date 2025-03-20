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
        "RIGHT_ATTRS": {"TAG": {"IN": ["VAFIN", "VVFIN"]}, "MORPH": {"IS_SUPERSET": ["Tense=Past", "Mood=Ind"]}}
      },
    ],
  ]
  dep_matcher.add("verb_tempus_past", dep_patterns)
  matches = dep_matcher(doc)

  for _, (verb, ) in matches:
    span_text = doc[verb].text
    result.append({"text": span_text})


  return result
   
