def iter_sentences(doc):
    for sentence in doc.sents:
        yield sentence

def search_prep_phrases(entity_map,token):
    results = []
    for child in token.children:
        if child.dep_ == "prep":
            prep = child.text
            for child2 in child.children:
                if child2.dep_ == "pobj":
                    if child2 in entity_map:
                        results.append((child.text,entity_map[child2]))
                    else:
                        results.append((child.text,child2.text))

    return results

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

            prep_results = search_prep_phrases(entity_map,child)
            if prep_results:
                for prep,pobj in prep_results:
                        token_list.append(" ".join(effective_compounds + [entity_map[child]])+"_"+prep+"_"+pobj)
            else:
                token_list.append(" ".join(effective_compounds + [entity_map[child]]))

            if effective_compounds == []:
                effective_compounds = None

            find_conjunctions(child,entity_map,token_list,effective_compounds)

