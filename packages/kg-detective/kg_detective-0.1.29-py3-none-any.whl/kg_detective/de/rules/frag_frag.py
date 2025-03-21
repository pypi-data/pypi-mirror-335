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
        "RIGHT_ID": "frag",
        "RIGHT_ATTRS": {"TAG": {"IN": ["PWAV", "PWS", "PWAT"]}, "MORPH": {"IS_SUPERSET": ["PronType=Int"]}}
      },
    ],
  ]
  dep_matcher.add("frag_frag", dep_patterns)
  matches = dep_matcher(doc)

  for _, (frag, ) in matches:
    span_text = doc[frag].text 
    result.append({"text": span_text})

  return result
