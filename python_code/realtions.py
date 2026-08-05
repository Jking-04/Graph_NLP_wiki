from lemminflect import getLemma
from python_code.utils import find_conjunctions,search_prep_phrases

def identify_clause_components(sentence):
    clause_constituents = {
        "attributes":[],
        "oComp":[],
        "iObjs":[],
        "objs":[],
        
    }
    
    for token in sentence:
        if token.dep_ == "ROOT":

            for child in token.children:
                if child.dep_ == "attr":
                    clause_constituents["attributes"].append(child)
                elif child.dep_ in ("ocomp"):
                    clause_constituents["oComp"].append(child)
                elif child.dep_ in ("iobj"):
                    clause_constituents["iObjs"].append(child)
                elif child.dep_ in ("dobj"):
                    clause_constituents["objs"].append(child)
                
    return clause_constituents

def determine_clause(clause_components):
    clause = ""
    if clause_components["attributes"]:
        clause = "SVC"
    elif clause_components["oComp"]:
        clause = "SVOC"
    elif clause_components["iObjs"] and clause_components["objs"] :
        clause = "SVOO"
    elif clause_components["objs"]:
        clause = "SVO"
    else:
        clause = "SV"

    return clause

def find_relations(sentence,entity_map,clause):
    for token in sentence:
        if token.dep_ == "ROOT":
            rel = getLemma(token.text,upos="VERB")[0] #lemmainflect seems to work much better for lemma

            if clause == "SVO":
                subjs = find_deps(token,entity_map,("nsubj", "nsubjpass"))
                objs = find_deps(token,entity_map,("dobj", "pobj"))

                v_prep_results = search_prep_phrases(entity_map,token)

                for subj in subjs:
                    for obj in objs:
                        if v_prep_results:
                            for v_prep,v_pobj in v_prep_results:
                                print(f"{subj}:{rel}:{obj}_{v_prep}_{v_pobj}")
                        else:
                            print(f"{subj}:{rel}:{obj}")

            if clause == "SVC":
                subjs = find_deps(token,entity_map,("nsubj", "nsubjpass"))
                attrs = find_deps(token,entity_map,("attr"))

                v_prep_results = search_prep_phrases(entity_map,token)
                            
                for subj in subjs:
                    for attr in attrs:
                        if v_prep_results:
                            for v_prep,v_pobj in v_prep_results:
                                print(f"{subj}:{rel}_{v_prep}:{attr}")
                        else:
                            print(f"{subj}:{rel}:{attr}")

            if clause == "SV":
                subjs = find_deps(token,entity_map,("nsubj", "nsubjpass"))
                v_prep_results = search_prep_phrases(entity_map,token)

                for subj in subjs:
                    
                    if v_prep_results:
                        for v_prep,v_pobj in v_prep_results:
                            print(f"{subj}:{rel}_{v_prep}:{v_pobj}")
                    else:
                        print(f"{subj}:{rel}")
    print("\n")

def find_deps(token,entity_map,dep_List):
    found = []

    for child in (token.children):
        if child in entity_map:                 
            if child.dep_ in dep_List:
                prep_results = search_prep_phrases(entity_map,child)
                if prep_results:
                    for prep,pobj in prep_results:
                        found.append(entity_map[child]+"_"+prep+"_"+pobj)
                else:
                    found.append(entity_map[child])

                find_conjunctions(child,entity_map,found)

    return found 
