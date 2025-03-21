from spacy.matcher import Matcher, DependencyMatcher
from kg_detective.lib import clean_merge, mark

def search_out(doc, nlp):
  """Search for  

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """
  raw_matches = []

  rule_name = "adj_posesivo"

  dep_matcher = DependencyMatcher(nlp.vocab)

  # poss noun
  pattern = [
    {
      "RIGHT_ID": "noun",
      "RIGHT_ATTRS": {"POS": "NOUN"}
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">--",
      "RIGHT_ID": "poss",
      "RIGHT_ATTRS": {"POS": "DET", "DEP": "det", "MORPH": {"IS_SUPERSET": ["Poss=Yes"]}}
    }
  ]

  dep_matcher.add(rule_name, [pattern])

  matches = dep_matcher(doc)
  for index, (_, [noun_id, poss_id]) in enumerate(matches):
    raw_matches.append((poss_id, noun_id+1, {"sign": "poss_noun", "gid": index})) 

  dep_matcher.remove(rule_name)

  base_index = len(raw_matches)

  # ser poss
  pattern = [
    {
      "RIGHT_ID": "poss",
      "RIGHT_ATTRS": {"POS": {"IN": ["DET", "PRON"]}, "MORPH": {"IS_SUPERSET": ["Poss=Yes"]}}
    },
    {
      "LEFT_ID": "poss",
      "REL_OP": ">--",
      "RIGHT_ID": "ser",
      "RIGHT_ATTRS": {"POS": "AUX", "DEP": "cop", "LEMMA": "ser"}
    }
  ]

  dep_matcher.add(rule_name, [pattern])

  matches = dep_matcher(doc)
  for index, (_, [poss_id, cop_id]) in enumerate(matches):
    cop_core = doc[cop_id]
    raw_matches.append((cop_id, cop_id+1, {"sign": "aux", "aux_lemma": cop_core.lemma_, "gid": base_index+index})) 
    raw_matches.append((poss_id, poss_id+1, {"sign": "poss", "gid": base_index+index})) 

  dep_matcher.remove(rule_name)

  base_index = (len(raw_matches)-base_index)//2 + base_index

  # lo poss
  pattern = [
    {
      "RIGHT_ID": "poss",
      "RIGHT_ATTRS": {"POS": {"IN": ["DET", "PRON"]}, "MORPH": {"IS_SUPERSET": ["Poss=Yes"]}}
    },
    {
      "LEFT_ID": "poss",
      "REL_OP": ">-",
      "RIGHT_ID": "lo",
      "RIGHT_ATTRS": {"DEP": "det", "LOWER": {"IN": ["lo", "el", "la", "los", "las"]}}
    }
  ]

  dep_matcher.add(rule_name, [pattern])

  matches = dep_matcher(doc)
  for index, (_, [poss_id, lo_id]) in enumerate(matches):
    raw_matches.append((lo_id, poss_id+1, {"sign": "lo_poss", "gid": base_index+index})) 

  dep_matcher.remove(rule_name)

  gids = [m[2]["gid"] for m in raw_matches]
  base_index = max(gids) if len(gids)>0 else 0

  # noun poss
  pattern = [
    {
      "RIGHT_ID": "noun",
      "RIGHT_ATTRS": {"POS": "NOUN"}
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">++",
      "RIGHT_ID": "poss",
      "RIGHT_ATTRS": {"DEP": {"IN": ["det", "amod"]}, "MORPH": {"IS_SUPERSET": ["Poss=Yes"]}}
    }
  ]

  dep_matcher.add(rule_name, [pattern])

  matches = dep_matcher(doc)
  for index, (_, [noun_id, poss_id]) in enumerate(matches):
    noun_core = doc[noun_id]
    noun_tree = [list(e.subtree) for e in noun_core.lefts]
    noun_tree = sum(noun_tree, [])
    noun_tree = [e.i for e in noun_tree]
    noun_tree.append(noun_id)
    noun_tree.sort()

    assertion = len(noun_tree)==noun_tree[-1]-noun_tree[0]+1 and noun_tree[-1]+1==poss_id
    if assertion:
      raw_matches.append((noun_tree[0], poss_id+1, {"sign": "noun_poss", "gid": base_index+index})) 

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)

