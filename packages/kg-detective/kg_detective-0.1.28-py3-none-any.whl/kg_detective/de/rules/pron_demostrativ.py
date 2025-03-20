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
        "RIGHT_ID": "pron",
        "RIGHT_ATTRS": {"POS": "PRON", "MORPH": {"IS_SUPERSET": ["PronType=Dem"]}}
      },
    ],
  ]
  dep_matcher.add("pron_demostrativ", dep_patterns)
  matches = dep_matcher(doc)

  for _, (pron, ) in matches:
    span_text = doc[pron].text 
    result.append({"text": span_text})

  return result
