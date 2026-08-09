from lemminflect import getLemma
from python_code.utils import find_conjunctions,search_prep_phrases,build_chunk_map
from python_code.entities import extract_entities,NodeRegistry

from python_code.data_classes import VerbFrame,Entity

node_registry = NodeRegistry()

def test_search_prep_phrases(token,chunk_map):
    results = []
    for child in token.children:
        if child.dep_ == "prep":
            prep = child.text
            for child2 in child.children:
                if child2.dep_ == "pobj":
                    results.append((prep,token_to_entity(child2,chunk_map)))

    return results

def get_conjuctions(token,token_list):
    for child in token.children:
        if child.dep_ == "conj":
            token_list.append(child)
            get_conjuctions(child,token_list)

def get_compounds(token):
    compounds = []
    for child in token.children:
        if child.dep_ == "compound":
            compounds.append(child.text)
    return compounds

def get_adjectives(token):
    adjectives = []
    for child in token.children:
        if child.dep_ == "amod":
            adjectives.append(child.text)
    return adjectives


def get_numbers(token):
    numbers = []
    for child in token.children:
        if child.dep_ == "nummod":
            numbers.append(child.text)
    return numbers


def get_determiners(token):
    determiners = []
    for child in token.children:
        if child.dep_ == "det":
            determiners.append(child.text)
    return determiners

def get_negations(token):
    for child in token.children:
        if child.dep_ == "neg":
            return True
    return False

def token_to_entity(token,chunk_map):

    p_noun_flag = token.pos_ == "PROPN"
    name = chunk_map.get(token, token.text)

    node_id = node_registry.get_or_create_prop_id(name) if p_noun_flag else node_registry.get_common_noun_id()

    entity = Entity(
        text = getLemma(token.text,upos="NOUN")[0],
        id = node_id,
        compounds=get_compounds(token),
        adjectives=get_adjectives(token),
        numbers=get_numbers(token),
        determiners=get_determiners(token),
        prep_phrases= test_search_prep_phrases(token,chunk_map)
    )
    return entity

def get_subjs(token,chunk_map):
    subjs = []
    for child in token.children:
        if child.dep_ in ("nsubj", "nsubjpass"):
            conjs = [child]
            get_conjuctions(child,conjs)
            subjs = [token_to_entity(t,chunk_map) for t in conjs]
    return subjs

def get_objs(token,chunk_map):
    dobjs = []
    iobjs = []
    for child in token.children:
        if child.dep_ in ("dobj","pobj"):
            conjs = [child]
            get_conjuctions(child,conjs)
            dobjs = [token_to_entity(t,chunk_map) for t in conjs]

        if child.dep_ in ("iobj"):
            conjs = [child]
            get_conjuctions(child,conjs)
            iobjs = [token_to_entity(t,chunk_map) for t in conjs]

    return dobjs,iobjs

def get_attrs(token,chunk_map):
    attrs = []
    for child in token.children:
        if child.dep_ in ("attr"):
            conjs = [child]
            get_conjuctions(child,conjs)
            attrs = [token_to_entity(t,chunk_map) for t in conjs]
    return attrs

def get_obj_comps(token,chunk_map):
    attrs = []
    for child in token.children:
        if child.dep_ in ("xcomp"):
            conjs = [child]
            get_conjuctions(child,conjs)
            attrs = [token_to_entity(t,chunk_map) for t in conjs]
    return attrs

def is_predicate(token):
    if token.dep_ == "conj":
        return False
    
    if token.pos_ == "VERB":
        return True

    if token.pos_ == "AUX" and token.dep_ == "ROOT":
        return True

    return False

def build_verb_frames(sentnece):
    frames = []

    chunk_map = build_chunk_map(sentnece)

    for token in sentnece:
        if is_predicate(token):

            verbs = [token]
            get_conjuctions(token,verbs)

            subjs = []
            attrs=[]
            dobjs = []
            iobjs = []
            obj_comp = []

            for potential_verb in verbs:
                if potential_verb.pos_ in ("VERB","AUX"):
                    verb = potential_verb
                    subjs = get_subjs(verb,chunk_map) or subjs

                    if (
                        not subjs
                        and verb.dep_ in {"advcl", "xcomp"}
                    ):
                        subjs = get_subjs(verb.head,chunk_map)

                    new_dobjs,new_iobjs = get_objs(verb,chunk_map)
                    dobjs = new_dobjs or dobjs
                    iobjs = new_iobjs or iobjs

                    attrs = get_attrs(verb,chunk_map) or attrs
                    obj_comp = get_obj_comps(verb,chunk_map) or obj_comp

                    frames.append(
                        VerbFrame(
                            verb = getLemma(verb.text,upos="VERB")[0],
                            negation=get_negations(verb),
                            subjects=subjs,
                            objects=dobjs,
                            i_objects=iobjs,
                            object_compliments=obj_comp,
                            attributes=attrs,
                            prep_phrases=test_search_prep_phrases(verb,chunk_map)
                        )
                    )
    return frames

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
