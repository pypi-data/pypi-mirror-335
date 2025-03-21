from spacy.matcher import DependencyMatcher
from kg_detective.lib import clean_merge, mark


def search_out(doc, nlp):
  """Search for superlative adjectives 

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed

  Returns:
    list: list of spacy.tokens.Span
    nlp (spacy.language.Language): context language
  """

  dep_matcher = DependencyMatcher(nlp.vocab)

  # the adj-est noun
  the_adjest_noun = [
    { 
      "RIGHT_ID": "noun",
      "RIGHT_ATTRS": {"POS": "NOUN"}
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">",
      "RIGHT_ID": "the",
      "RIGHT_ATTRS": {"DEP": "det", "LEMMA": "the"}
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">",
      "RIGHT_ID": "adjest",
      "RIGHT_ATTRS": {"DEP": "amod", "TAG": "JJS", "POS": "ADJ"}
    }
  ]

  # the most adj noun
  the_most_adj_noun = [
    { 
      "RIGHT_ID": "noun",
      "RIGHT_ATTRS": {"POS": "NOUN"}
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">",
      "RIGHT_ID": "the",
      "RIGHT_ATTRS": {"DEP": "det", "LEMMA": "the"}
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">",
      "RIGHT_ID": "adj",
      "RIGHT_ATTRS": {"DEP": "amod", "POS": "ADJ"}
    },
    {
      "LEFT_ID": "adj",
      "REL_OP": ">",
      "RIGHT_ID": "most",
      "RIGHT_ATTRS": {"DEP": "advmod", "POS": "ADV", "LEMMA": "most"}
    }
  ]


  raw_matches = []

  dep_patterns = [the_adjest_noun, the_most_adj_noun]
  dep_matcher.add("adj_superlative", dep_patterns)

  matches = dep_matcher(doc)

  for index, (_, token_ids) in enumerate(matches):
    noun_core = doc[token_ids[0]]
    det = doc[token_ids[1]]
    adj_core = doc[token_ids[2]]

    _phrase = [list(e.subtree) for e in noun_core.lefts]# left tree of noun
    np = [e.i for e in sum(_phrase, [])]
    np.sort()
    np_assertion = len(np) == np[-1]-np[0]+1 and np[-1] == noun_core.i-1 and np[0] == det.i 

    adj_part = [e.i for e in list(adj_core.subtree)] # tree of adj
    adj_part.sort()

    adj_assertion = len(adj_part) == adj_part[-1]-adj_part[0]+1 and adj_part[0] == det.i+1
    
    if np_assertion and adj_assertion:
      np.append(noun_core.i)
      noun_part = list(set(np) - set([det.i]) - set(adj_part))
      noun_part.sort()
    
      raw_matches.append((adj_part[0]-1, adj_part[-1]+1, {"sign": "det_adj_part", "adj_lemma": adj_core.lemma_, "gid": index}))
      raw_matches.append((noun_part[0], noun_part[-1]+1, {"sign": "noun_part", "gid": index}))

  dep_matcher.remove("adj_superlative")

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
