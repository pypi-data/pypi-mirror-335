from kg_detective.lib import mark

def search_out(doc, nlp):
  """Search for interrogative pronouns 

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Token
  """


  _result = [t for t in doc if t.pos_ in ["PRON", "DET"] and t.tag_ in ["WDT", "WP", "WP$", "WRB"]]

  refined_matches = [(t.i, t.i+1, {"sign": "interrogative_pron", "gid": index}) for index, t in enumerate(_result)]

  return mark(doc, refined_matches)
