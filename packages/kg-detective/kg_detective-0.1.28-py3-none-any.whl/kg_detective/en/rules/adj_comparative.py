from spacy.matcher import DependencyMatcher
from kg_detective.lib import clean_merge, mark

def search_out(doc, nlp):
  """Search for comparative adjectives  

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """

  dep_matcher = DependencyMatcher(nlp.vocab)

  # adjer_noun
  adjer_noun = [
    {
      "RIGHT_ID": "noun",
      "RIGHT_ATTRS": {"POS": "NOUN"}
    },
    {
      "LEFT_ID": "noun",
      "REL_OP": ">",
      "RIGHT_ID": "adjer",
      "RIGHT_ATTRS": {"DEP": "amod", "TAG": "JJR", "POS": "ADJ"}
    }
  ]

  # adjer than (prep)
  adjer_than = [
    {
      "RIGHT_ID": "adjer",
      "RIGHT_ATTRS": {"TAG": "JJR", "POS": "ADJ"}
    },
    {
      "LEFT_ID": "adjer",
      "REL_OP": ">",
      "RIGHT_ID": "than",
      "RIGHT_ATTRS": {"LEMMA": "than", "POS": "ADP", "DEP": "prep"}
    }
  ]

  # more/less adj than (prep)
  adv_adj_than = [
    {
      "RIGHT_ID": "adjer",
      "RIGHT_ATTRS": {"TAG": "JJ", "POS": "ADJ"}
    },
    {
      "LEFT_ID": "adjer",
      "REL_OP": ">",
      "RIGHT_ID": "than",
      "RIGHT_ATTRS": {"LEMMA": "than", "POS": "ADP", "DEP": "prep"}
    },
    {
      "LEFT_ID": "adjer",
      "REL_OP": ">",
      "RIGHT_ID": "adv",
      "RIGHT_ATTRS": {"TEXT": {"IN": ["more", "less"]}, "POS": "ADV", "DEP": "advmod"}
    }
  ]

  raw_matches = []

  dep_matcher.add("adj_comparative", [adjer_noun])
  matches = dep_matcher(doc)
  for index, (_, [noun_core_id, adjer_id]) in enumerate(matches):
    noun_core = doc[noun_core_id]
    adj_core = doc[adjer_id]
    
    noun_tree = [e.i for e in noun_core.subtree]
    noun_tree.sort()

    noun_assertion = len(noun_tree) == noun_tree[-1]-noun_tree[0]+1
    if noun_assertion:
      raw_matches.append((noun_tree[0], noun_tree[-1]+1, {"sign": "adjer_noun", "adj_lemma": adj_core.lemma_, "gid": index})) 
  dep_matcher.remove("adj_comparative")


  base_index = len(raw_matches)
  dep_matcher.add("adj_comparative", [adjer_than, adv_adj_than])
  matches = dep_matcher(doc)
  
  for index, (_, token_ids) in enumerate(matches):
    adj_core = doc[token_ids[0]]
    prep_core = doc[token_ids[1]]
    
    adj_tree = [e.i for e in adj_core.subtree]
    adj_tree.sort()
    prep_tree = [e.i for e in prep_core.subtree]
    prep_tree.sort()

    adj_assertion = len(adj_tree)==adj_tree[-1]-adj_tree[0]+1 and adj_tree[-1]==prep_tree[-1]
    prep_assertion = len(prep_tree)==prep_tree[-1]-prep_tree[0]+1 and prep_core.i==prep_tree[0] and len(prep_tree)>1
    
    if adj_assertion and prep_assertion:
      prep_part = prep_tree[1:]
      adj_part = list(set(adj_tree)-set(prep_part))
      adj_part.sort()

      raw_matches.append((adj_part[0], adj_part[-1]+1, {"sign": "adjer_than", "adj_lemma": adj_core.lemma_, "gid": base_index+index})) 
      raw_matches.append((prep_part[0], prep_part[-1]+1, {"sign": "than_obj", "gid": base_index+index}))

  dep_matcher.remove("adj_comparative")

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
