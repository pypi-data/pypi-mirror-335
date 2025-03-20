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
        "RIGHT_ATTRS": {"TAG": {"IN": ["ADJD", "ADJA"]}, "MORPH": {"IS_SUPERSET": ["Degree=Pos"]}}
      },
      {
        "LEFT_ID": "adj",
        "REL_OP": ">",
        "RIGHT_ID": "so",
        "RIGHT_ATTRS": {"DEP": "mo", "POS": "ADV", "LOWER": "so"}
      },
      {
        "LEFT_ID": "so",
        "REL_OP": ">",
        "RIGHT_ID": "compared",
        "RIGHT_ATTRS": {"DEP": "cc"}
      },
      {
        "LEFT_ID": "compared",
        "REL_OP": ">",
        "RIGHT_ID": "cm",
        "RIGHT_ATTRS": {"DEP": "cm", "POS": "ADP", "LOWER": "wie"}
      },
    ],
  ]
  dep_matcher.add("adj_ohne_steigerung", dep_patterns)
  matches = dep_matcher(doc)

  for _, (adj, so, compared, wie) in matches:
    span_ids = [adj, so, wie]
   
    sorted_span_ids = sorted(span_ids)
    span_text = " ".join([doc[e].text for e in sorted_span_ids])
    result.append({"text": span_text})


  return result
   
