from spacy.language import Language 
from spacy.tokens import Doc
from importlib import import_module

def get_all_rules(LABEL_RULES):
  RULES = []
  for r in LABEL_RULES.values():
    RULES += r
  return RULES

def get_rules(LABEL_RULES, labels, rules):
  rs = []
  for l in labels:
    rs += LABEL_RULES[l]
  rs += rules

  if len(rs) == 0:
    rs = get_all_rules(LABEL_RULES)

  return rs

class KG:

  def __init__(self, nlp: Language, labels: list=[], rules: list=[]): 
    lang = nlp.meta["lang"]
    self.ext_name = "kg"
    self.rule_pkg = 'kg_detective.{}.rules'.format(lang)
    self.nlp = nlp
    
    if not Doc.has_extension(self.ext_name):
      Doc.set_extension(self.ext_name, default={})

    self.LABEL_RULES = getattr(import_module('kg_detective.{}.kg_fn'.format(lang)), 'LABEL_RULES')
    self.rules = get_rules(self.LABEL_RULES, labels, rules)

  def __call__(self, doc: Doc):
    for rule_module_name in self.rules:
      rule_module = import_module('{}.{}'.format(self.rule_pkg, rule_module_name))    
      fn = getattr(rule_module, 'search_out')
      doc._.kg[rule_module_name] = fn(doc, self.nlp) 
    return doc
