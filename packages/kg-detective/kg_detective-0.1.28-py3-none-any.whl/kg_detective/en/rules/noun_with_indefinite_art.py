from spacy.matcher import DependencyMatcher
from kg_detective.lib import combine_merge, mark

def search_out(doc, nlp):
  """Search for indefinite article with noun 

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
        "RIGHT_ID": "indefart",
        "RIGHT_ATTRS": {"POS": "DET", "LEMMA": {"IN": ["a", "an"]}}
      },
    ],
  ]
  dep_matcher.add("det_indefinite_art", dep_patterns)
  matches = dep_matcher(doc)

  raw_matches = []
  for index, (_, [noun_id, indef_art_id]) in enumerate(matches):
    noun_subtree = [list(e.subtree) for e in doc[noun_id].lefts]  
    noun_tree = [e.i for e in sum(noun_subtree, [])]
    noun_tree.append(noun_id)
    noun_tree.sort()

    indef_art_assertion = indef_art_id in noun_tree 
    noun_assertion = len(noun_tree)>0 and noun_tree[-1]-noun_tree[0]+1==len(noun_tree) and noun_id== noun_tree[-1]
    
    if indef_art_assertion and noun_assertion:
      raw_matches.append((noun_tree[0], noun_tree[-1]+1, {"sign": "indef_art_noun", "gid": index}))
  
  dep_matcher.remove("det_indefinite_art")

  refined_matches = combine_merge(raw_matches)

  return mark(doc, refined_matches)
