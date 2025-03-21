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
        "RIGHT_ID": "adj",
        "RIGHT_ATTRS": {"TAG": {"IN": ["ADJD", "ADJA"]}, "MORPH": {"IS_SUPERSET": ["Degree=Cmp"]}}
      },
    ],
  ]
  dep_matcher.add("adj_komparation", dep_patterns)
  matches = dep_matcher(doc)

  for _, (adj, ) in matches:
    span_text = doc[adj].text
    result.append({"text": span_text})

  return result
