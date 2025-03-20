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

  rule_name = "pron_ablativo"

  dep_matcher = DependencyMatcher(nlp.vocab)

  prep_pron = [
    {
      "RIGHT_ID": "pron",
      "RIGHT_ATTRS": {"POS": "PRON", "LOWER": {"IN": ["mí", "ti", "él", "ella", "usted", "nosotros", "nosotras", "vosotros", "vosotras", "ellos", "ellas", "ustedes"]}}
    },
    {
      "LEFT_ID": "pron",
      "REL_OP": ">-",
      "RIGHT_ID": "prep",
      "RIGHT_ATTRS": {"POS": "ADP", "DEP": "case"}
    }
  ]

  dep_matcher.add(rule_name, [prep_pron])

  matches = dep_matcher(doc)
  for index, (_, [pron_id, prep_id]) in enumerate(matches):

    pron_tree = [list(e.subtree) for e in doc[pron_id].rights if e.dep_=="conj"]
    pron_tree = sum(pron_tree, [])
    pron_tree = [e.i for e in pron_tree]
    pron_tree.append(pron_id)
    pron_tree.sort()

    pron_assertion = len(pron_tree)==pron_tree[-1]-pron_tree[0]+1

    raw_matches.append((prep_id, prep_id+1, {"sign": "prep", "gid": index})) 
    raw_matches.append((pron_tree[0], pron_tree[-1]+1, {"sign": "pron", "gid": index})) 

  dep_matcher.remove(rule_name)

  base_index = len(raw_matches)//2

  prepron = [
    {
      "RIGHT_ID": "pron",
      "RIGHT_ATTRS": {"POS": "PRON", "MORPH": {"IS_SUPERSET": ["Case=Com", "PrepCase=Pre", "PronType=Prs"]}}
    }
  ]

  dep_matcher.add(rule_name, [prepron])

  matches = dep_matcher(doc)
  for index, (_, [prepron_id]) in enumerate(matches):
    raw_matches.append((prepron_id, prepron_id+1, {"sign": "prepron", "gid": base_index+index})) 

  dep_matcher.remove(rule_name)

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
   
