from spacy.matcher import DependencyMatcher
from kg_detective.lib import clean_merge, mark

def search_out(doc, nlp):
  """Search for verbs with past perfect tense  

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """

  dep_matcher = DependencyMatcher(nlp.vocab)
  had_verb_ed = [
    {
      "RIGHT_ID": "core_verb",
      "RIGHT_ATTRS": {"POS": {"IN": ["VERB", "AUX"]}, "TAG": "VBN", "DEP": "ROOT"}
    },
    {
      "LEFT_ID": "core_verb",
      "REL_OP": ">--",
      "RIGHT_ID": "aux",
      "RIGHT_ATTRS": {"DEP": "aux", "POS": "AUX", "lemma": "have", "TAG": "VBD"}
    }
  ]

  dep_patterns = [had_verb_ed]
  dep_matcher.add("verb_past_perfect_tense", dep_patterns)
  matches = dep_matcher(doc)

  raw_matches = []
  for index, (_, [verb_id, aux_id]) in enumerate(matches):
    verb = doc[verb_id]
    aux = doc[aux_id]

    aux_end = aux_id+2 if doc[aux_id+1].head==verb and doc[aux_id+1].lemma_=="not" and doc[aux_id+1].dep_=="neg" else aux_id+1
    raw_matches.append((aux_id, aux_end, {"sign": "aux", "aux_lemma": aux.lemma_, "gid": index}))

    passive_tokens = [e for e in verb.lefts if e.dep_=="auxpass"]
    if len(passive_tokens)==1:
      auxpass = passive_tokens[0]
      raw_matches.append((auxpass.i, auxpass.i+1, {"sign": "auxpass", "auxpass_lemma": auxpass.lemma_, "gid": index}))

    raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": verb.lemma_, "gid": index})) 

  dep_matcher.remove("verb_past_perfect_tense")

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
