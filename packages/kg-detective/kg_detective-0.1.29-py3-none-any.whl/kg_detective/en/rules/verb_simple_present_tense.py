from kg_detective.lib import mark

def search_out(doc, nlp):
  """Search for verbs with simple present tense  

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """

  _result = [t for t in doc if t.tag_ in ["VBZ", "VBP", "VB"] and t.dep_ == "ROOT" and "Tense=Pres" in t.morph]

  refined_matches = [(t.i, t.i+1, {"sign": "verb", "verb_lemma": t.lemma_, "gid": index}) for index, t in enumerate(_result)]

  return mark(doc, refined_matches)
