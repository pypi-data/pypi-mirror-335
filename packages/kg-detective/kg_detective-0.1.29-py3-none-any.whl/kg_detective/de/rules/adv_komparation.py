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
        "RIGHT_ID": "adv",
        "RIGHT_ATTRS": {"POS": "ADV", "MORPH": {"IS_SUPERSET": ["Degree=Sup"]}}
      },
      {
        "LEFT_ID": "adv",
        "REL_OP": ">",
        "RIGHT_ID": "am",
        "RIGHT_ATTRS": {"DEP": "pm", "POS": "PART", "TAG": "PTKA", "LOWER": "am"}
      },
    ],
  ]
  dep_matcher.add("adv_komparation", dep_patterns)
  matches = dep_matcher(doc)

  for _, (adv, part) in matches:
    span_ids = [adv, part]
   
    sorted_span_ids = sorted(span_ids)
    span_text = " ".join([doc[e].text for e in sorted_span_ids])
    result.append({"text": span_text})


  return result
   
