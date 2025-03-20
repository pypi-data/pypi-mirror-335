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
        "RIGHT_ID": "conj",
        "RIGHT_ATTRS": {"TAG": "KON", "POS": "CCONJ", "DEP": "cd"}
      },
    ],
  ]
  dep_matcher.add("conj_einfache", dep_patterns)
  matches = dep_matcher(doc)

  for _, (conj, ) in matches:
    span_text = doc[conj].text 
    result.append({"text": span_text})

  return result
