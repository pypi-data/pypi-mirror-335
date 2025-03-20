import os
from kg_detective.lib import mark

def search_out(doc, nlp):
  """Search for reflexive pronouns 

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Token
  """

  pkg_path = os.path.dirname(__file__)
  REFLEXIVE = open(pkg_path + '/pron_reflexive.txt', 'r').read().splitlines() 

  _result = [t for t in doc if t.text.lower() in REFLEXIVE]

  refined_matches = [(t.i, t.i+1, {"sign": "reflexive_pron", "gid": index}) for index, t in enumerate(_result)]

  return mark(doc, refined_matches)
