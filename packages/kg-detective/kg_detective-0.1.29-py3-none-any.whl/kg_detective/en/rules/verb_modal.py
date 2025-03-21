from kg_detective.lib import mark

def search_out(doc, nlp):
  """Search for verbs with verb modal   

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed

  Returns:
    list: list of spacy.tokens.Span
  """


  _result = [t for t in doc if t.tag_=="MD"]

  refined_matches = [(t.i, t.i+1, {"sign": "verb_modal", "verb_lemma": t.lemma_, "gid": index}) for index, t in enumerate(_result)]

  return mark(doc, refined_matches)
