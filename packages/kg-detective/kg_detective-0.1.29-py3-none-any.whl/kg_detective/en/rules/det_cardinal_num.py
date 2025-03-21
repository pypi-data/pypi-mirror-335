from spacy.matcher import DependencyMatcher
from kg_detective.lib import clean_merge, mark

def search_out(doc, nlp):
  """Search for cardinal number with noun 

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """

  dep_matcher = DependencyMatcher(nlp.vocab)
  dep_patterns = [
    [
      {
        "RIGHT_ID": "noun",
        "RIGHT_ATTRS": {"POS":"NOUN"}
      },
      {
        "LEFT_ID": "noun",
        "REL_OP": ">>",
        "RIGHT_ID": "card_num",
        "RIGHT_ATTRS": {"POS": "NUM", "TAG": "CD"}
      },
    ],
  ]
  dep_matcher.add("det_cardinal_num", dep_patterns)
  matches = dep_matcher(doc)

  raw_matches = []
  for index, (_, [noun_id, card_num_id]) in enumerate(matches):
    noun_subtree = [list(e.subtree) for e in doc[noun_id].lefts]  
    noun_tree = [e.i for e in sum(noun_subtree, [])]
    noun_tree.append(noun_id)
    noun_tree.sort()

    card_num_assertion = card_num_id in noun_tree 
    noun_assertion = len(noun_tree)>1 and noun_tree[-1]-noun_tree[0]+1==len(noun_tree) and noun_id==noun_tree[-1]
    
    if card_num_assertion and noun_assertion:
      raw_matches.append((noun_tree[0], noun_tree[-1]+1, {"sign": "card_num", "card_num": doc[card_num_id].text, "gid": index}))
  
  dep_matcher.remove("det_cardinal_num")

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
