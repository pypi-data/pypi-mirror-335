from spacy.matcher import DependencyMatcher
from kg_detective.lib import clean_merge, mark

def search_out(doc, nlp):
  """Search for prepositions with adj 

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """

  # pattern: as ... as ...
  dep_matcher = DependencyMatcher(nlp.vocab)
  dep_patterns = [
    [
      {
        "RIGHT_ID": "aux",
        "RIGHT_ATTRS": {"POS": {"IN": ["AUX", "VERB"]}, "LEMMA": "be"}
      },
      {
        "LEFT_ID": "aux",
        "REL_OP": ">",
        "RIGHT_ID": "adj",
        "RIGHT_ATTRS": {"DEP": "acomp", "POS": {"IN": ["ADJ", "VERB"]}}
      },
      {
        "LEFT_ID": "adj",
        "REL_OP": ">+",
        "RIGHT_ID": "prep",
        "RIGHT_ATTRS": {"DEP": "prep", "POS": "ADP"}
      },
    ],
  ]
  dep_matcher.add("prep_with_adj", dep_patterns)
  matches = dep_matcher(doc)

  raw_matches = []
  for index, (_, [aux, adj, prep]) in enumerate(matches):
    adj_assertion = "as" not in [e.lemma_ for e in doc[adj].lefts]
    if adj_assertion:
      rt = doc[aux+1]
      aux_end = aux+2 if rt.head==doc[aux] and rt.lemma_=="not" and rt.dep_=="neg" else aux+1
      raw_matches.append((aux, aux_end, {"sign": "aux", "aux_lemma": doc[aux].lemma_, "gid": index}))
      raw_matches.append((adj, prep+1, {"sign": "adj_prep", "adj_lemma": doc[adj].lemma_, "gid": index}))

  dep_matcher.remove("prep_with_adj")

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
