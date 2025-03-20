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
        "RIGHT_ID": "modal_verb",
        "RIGHT_ATTRS": {"TAG": {"IN": ["VMFIN", "VMINF"]}}
      },
    ],
  ]
  dep_matcher.add("verb_modal", dep_patterns)
  matches = dep_matcher(doc)

  for _, (modal_verb, ) in matches:
    span_text = doc[modal_verb].text
    result.append({"text": span_text})

  return result
   
