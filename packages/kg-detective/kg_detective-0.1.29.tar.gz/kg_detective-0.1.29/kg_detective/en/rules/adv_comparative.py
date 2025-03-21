from spacy.matcher import DependencyMatcher
from kg_detective.lib import clean_merge, mark

def search_out(doc, nlp):
  """Search for comparative adverbs  

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """

  dep_matcher = DependencyMatcher(nlp.vocab)

  # verb_adver
  verb_adver = [
    {
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": "VERB"}
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">",
      "RIGHT_ID": "adver",
      "RIGHT_ATTRS": {"POS": "ADV", "TAG": "RBR", "DEP": "advmod"}
    }
  ]

  # verb_more_adv
  verb_more_adv = [
    {
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": "VERB"}
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">",
      "RIGHT_ID": "adv",
      "RIGHT_ATTRS": {"POS": "ADV", "DEP": "advmod"}
    },
    {
      "LEFT_ID": "adv",
      "REL_OP": ">",
      "RIGHT_ID": "more",
      "RIGHT_ATTRS": {"DEP": "advmod", "LEMMA": {"IN": ["more", "less"]}}
    }
  ]


  dep_matcher.add("adv_comparative", [verb_adver, verb_more_adv])
  matches = dep_matcher(doc)

  raw_matches = []
  for index, (_, token_ids) in enumerate(matches):
    verb_core = doc[token_ids[0]]
    adv_core = doc[token_ids[1]]
    
    adver_tree = [e.i for e in adv_core.subtree]
    adver_tree.sort()

    adver_assertion = len(adver_tree) == adver_tree[-1]-adver_tree[0]+1
    verb_assertion = verb_core.i < adver_tree[0]

    if adver_assertion and verb_assertion:
      raw_matches.append((verb_core.i, verb_core.i+1, {"sign": "verb_core", "verb_lemma": verb_core.lemma_, "gid": index}))
      raw_matches.append((adver_tree[0], adver_tree[-1]+1, {"sign": "adver_tree", "gid": index}))

  dep_matcher.remove("adv_comparative")

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
