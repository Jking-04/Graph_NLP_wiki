def iter_sentences(doc):
    for sentence in doc.sents:
        yield sentence

def find_conjunctions(token,entity_map,token_list,compounds = None):
    if compounds == None:
        compounds=[]

    local_compounds = []

    for child in token.children:
        if child.dep_ == "compound":
            local_compounds.append(child.text)

        if child.dep_ == "conj":
            if any(sub_child.dep_ in ["det","amod","compound"] for sub_child in child.children):
                effective_compounds = []
            elif local_compounds:
                effective_compounds = local_compounds
            else:
                effective_compounds = compounds

            token_list.append(" ".join(effective_compounds + [entity_map[child]]))

            if effective_compounds == []:
                effective_compounds = None

            find_conjunctions(child,entity_map,token_list,effective_compounds)