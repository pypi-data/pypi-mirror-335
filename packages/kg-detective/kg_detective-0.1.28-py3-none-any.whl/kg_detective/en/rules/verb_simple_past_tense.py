from spacy.matcher import DependencyMatcher
from kg_detective.lib import clean_merge, mark

def search_out(doc, nlp):
  """Search for verbs with simple past tense  

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """

  dep_matcher = DependencyMatcher(nlp.vocab)

  # was/were
  was_were = [
    {
      "RIGHT_ID": "was_were",
      "RIGHT_ATTRS": {"TAG": "VBD", "DEP": "ROOT", "LEMMA": "be"}
    }
  ]

  # verb_ed
  verbed = [
    {
      "RIGHT_ID": "verbed",
      "RIGHT_ATTRS": {"TAG": "VBD", "DEP": "ROOT", "LEMMA": {"NOT_IN": ["be"]}}
    }
  ]

  # didn't verb
  did_not_verb = [
    {
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"TAG": "VB", "DEP": "ROOT"}
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">--",
      "RIGHT_ID": "not",
      "RIGHT_ATTRS": {"LEMMA": "not", "POS": "PART", "DEP": "neg"}
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">--",
      "RIGHT_ID": "aux",
      "RIGHT_ATTRS": {"TEXT": "did", "POS": "AUX", "DEP": "aux", "TAG": "VBD"}
    }
  ]

  # was_verbed, was_not_verbed
  was_verbed = [
    {
      "RIGHT_ID": "verbed",
      "RIGHT_ATTRS": {"TAG": "VBN", "DEP": "ROOT"}
    },
    {
      "LEFT_ID": "verbed",
      "REL_OP": ">--",
      "RIGHT_ID": "was_were",
      "RIGHT_ATTRS": {"TEXT": {"IN": ["was", "were"]}, "POS": "AUX", "DEP": "auxpass", "TAG": "VBD"}
    }
  ]

  raw_matches = []

  dep_matcher.add("simple_past_tense", [was_verbed])
  matches = dep_matcher(doc)
  for index, (_, [verb_id, was_id]) in enumerate(matches):
    raw_matches.append((was_id, verb_id+1, {"sign": "was_verbed", "verb_lemma": doc[was_id].lemma_+" "+doc[verb_id].text, "gid": index}))
  dep_matcher.remove("simple_past_tense")

  base_index = len(raw_matches)

  dep_matcher.add("simple_past_tense", [verbed])
  matches = dep_matcher(doc)
  for index, (_, [verb_id]) in enumerate(matches):
    t = doc[verb_id]
    raw_matches.append((t.i, t.i+1, {"sign": "verbed", "verb_lemma": t.lemma_, "gid": base_index+index}))
  dep_matcher.remove("simple_past_tense")

  base_index = len(raw_matches)

  dep_matcher.add("simple_past_tense", [was_were])
  matches = dep_matcher(doc)
  for index, (_, [verb_id]) in enumerate(matches):
    t = doc[verb_id]
    t_end = verb_id+2 if doc[verb_id+1].head==t and doc[verb_id+1].dep_=="neg" and doc[verb_id+1].lemma_=="not" else verb_id+1
    raw_matches.append((verb_id, t_end, {"sign": "was_were", "verb_lemma": t.lemma_, "gid": base_index+index}))
  dep_matcher.remove("simple_past_tense")

  base_index = len(raw_matches)

  dep_matcher.add("simple_past_tense", [did_not_verb])
  matches = dep_matcher(doc)
  for index, (_, [verb_id, not_id, did_id]) in enumerate(matches):
    aux_assertion = did_id+1==not_id
    verb_assertion = not_id+1==verb_id
    if aux_assertion and verb_assertion:
      raw_matches.append((did_id, verb_id+1, {"sign": "did_not_verb", "verb_lemma": doc[verb_id].lemma_, "gid": base_index+index}))
  dep_matcher.remove("simple_past_tense")

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
