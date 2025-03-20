import sys

VOCAB_LABELS = ["NOUN", "ART", "VERB", "ADJ", "PREP", "PRON", "ADV", "ZAHL", "CONJ", "FRAG"]

NOUN_RULES = ["noun_kasus", "noun_genus", "noun_pluralform"]

ART_RULES = ["art_bestimmer", "art_unbestimmer", "art_null", "art_possessiv", "art_demostrativ"]

VERB_RULES = ["verb_tempus_perfekt", "verb_tempus_prätertum", "verb_tempus_präsens", "verb_tempus_futur_1", "verb_tempus_plusquaperfekt", "verb_modus_imperativ", "verb_modus_konjunktiv_1", "verb_modus_konjunktiv_2", "verb_genus_passiv", "verb_trennbare", "verb_untrennbare", "verb_modal", "verb_reflexive", "verb_ergänzungen_im_akkusativ", "verb_ergänzungen_im_dativ", "verb_ergänzungen_im_dativ_akkusativ", "verb_ergänzungen_im_akkusativ_akkusativ", "verb_ergänzungen_im_genitiv", "verb_ergänzungen_mit_präposition", "verb_zu_infinitiv", "verb_partizip_1", "verb_partizip_2", "verb_funktionsverbgefüge", "verb_nominalisierung"]

ADJ_RULES = ["adj_ohne_steigerung", "adj_komparativ", "adj_superlativ", "adj_deklination", "adj_norminalisierte", "adj_ergänzung_mit_präposition"]

PREP_RULES = ["prep_mit_akkusativ", "prep_mit_dativ", "prep_mit_akkusativ_order_dativ", "prep_mit_genitiv", "prep_temporale"]

PRON_RULES = ["pron_personal", "pron_indefinit", "pron_possessiv", "pron_reflexiv", "pron_relativ", "pron_demostrativ"]

ADV_RULES = ["adv_temporal", "adv_lokal", "adv_modal", "adv_grad", "adv_kasual", "adv_komparation"]

ZAHL_RULES = ["zahl_grund", "zahl_ordnung", "zahl_verteilung", "zahl_wiederholung", "zahl_vervielfältigung", "zahl_bruch"]

CONJ_RULES = ["conj_einfache", "conj_zweiteilige"]

FRAG_RULES = ["frag_frag"]

SEN_LABELS = ["NEBENSATZ"]

NEBENSATZ_RULES = ["satz_adverbial", "satz_relativ", "satz_subjekt", "satz_objekt", "satz_prädikativ"]

LABELS = VOCAB_LABELS + SEN_LABELS

LABEL_RULES = {label: getattr(sys.modules[__name__], label+"_RULES") for label in LABELS}


