import sys

VOCAB_LABELS = ["NOUN", "VERB", "ADJ", "PREP", "PRON", "ADV"]

ADJ_RULES = ["adj_comparativo", "adj_igualdad_comparativo", "adj_superlativo", "adj_absoluto_superlativo", "adj_demostrativo", "adj_posesivo"]

ADV_RULES = ["adv_comparativo", "adv_igualdad_comparativo", "adv_superlativo", "adv_absoluto_superlativo"]

NOUN_RULES = ["noun_propio", "noun_comparativo"]

PREP_RULES = ["prep_con_verbo", "prep_con_adjetivo"]

PRON_RULES = ["pron_ablativo", "pron_personales_de_objeto", "pron_posesivo"]

VERB_RULES = ["verb_indicativo_presente", "verb_indicativo_pretérito", "verb_indicativo_pretérito_perfecto", "verb_indicativo_pretérito_imperfecto", "verb_indicativo_pretérito_pluscuamperfecto", "verb_indicativo_futuro", "verb_indicativo_futuro_perfecto", "verb_condicional_simple", "verb_condicional_compuesto", "verb_subjuntivo_presente", "verb_subjuntivo_pretérito_perfecto", "verb_subjuntivo_pretérito_imperfecto", "verb_subjuntivo_pretérito_pluscuamperfecto", "verb_imperativo", "verb_voz_pasiva", "verb_participio", "verb_gerundio", "verb_reflexivo"]

SEN_LABELS = ["SUBORDINADA"]

SUBORDINADA_RULES = ["subordinada_substantivo", "subordinada_relativo"]

LABELS = VOCAB_LABELS + SEN_LABELS

LABEL_RULES = {label: getattr(sys.modules[__name__], label+"_RULES") for label in LABELS}

