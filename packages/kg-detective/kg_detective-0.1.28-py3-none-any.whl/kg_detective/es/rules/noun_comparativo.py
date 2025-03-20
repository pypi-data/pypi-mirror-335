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

  rule_name = "noun_comparativo"

  dep_matcher = DependencyMatcher(nlp.vocab)

  cmp_noun = [
    {
      "RIGHT_ID": "noun",
      "RIGHT_ATTRS": {"POS": "NOUN"}
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">-",
      "RIGHT_ID": "cmp",
      "RIGHT_ATTRS": {"POS": "ADV", "LOWER": {"IN": ["menos", "más"]}},
    }
  ]

  dep_matcher.add(rule_name, [cmp_noun])

  matches = dep_matcher(doc)
  for index, (_, [noun_id, cmp_id]) in enumerate(matches):
    raw_matches.append((cmp_id, noun_id+1, {"sign": "cmp_noun", "gid": index})) 

  dep_matcher.remove(rule_name)

  base_index = len(raw_matches)

  cmp_de_noun = [
    {
      "RIGHT_ID": "noun",
      "RIGHT_ATTRS": {"POS": "NOUN"}
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">>",
      "RIGHT_ID": "cmp",
      "RIGHT_ATTRS": {"POS": "ADV", "LOWER": {"IN": ["menos", "más"]}},
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">>",
      "RIGHT_ID": "de",
      "RIGHT_ATTRS": {"POS": "ADP", "LOWER": "de"},
    }
  ]

  dep_matcher.add(rule_name, [cmp_de_noun])

  matches = dep_matcher(doc)
  for index, (_, [noun_id, cmp_id, de_id]) in enumerate(matches):
    noun_core = doc[noun_id]
    noun_left_children = [list(e.subtree) for e in noun_core.lefts]
    noun_left_tree = [t.i for t in sum(noun_left_children,[])]
    noun_left_tree.append(noun_id)
    noun_left_tree.sort()

    cmp_de_assertion = cmp_id+1==de_id and cmp_id==noun_left_tree[0]
    noun_assertion = len(noun_left_tree)==noun_left_tree[-1]-noun_left_tree[0]+1 and noun_left_tree[-1]==noun_id

    if cmp_de_assertion and noun_assertion:
      raw_matches.append((cmp_id, de_id+1, {"sign": "cmp_de", "gid": base_index+index})) 
      raw_matches.append((de_id+1, noun_id+1, {"sign": "noun", "gid": base_index+index})) 

  dep_matcher.remove(rule_name)


  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)

