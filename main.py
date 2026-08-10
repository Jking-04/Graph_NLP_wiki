


import spacy
from itertools import combinations
import networkx as nx
import matplotlib.pyplot as plt

from python_code.read_wikipedia import scrape_wiki
from python_code.entities import extract_entities
from python_code.preprocess import text_preprocess
from python_code.utils import iter_sentences
from python_code.realtions import find_relations,identify_clause_components,determine_clause,build_verb_frames,resolve_entity
from python_code.build_graph import find_all_entities,add_node,display_graph,build_relations,build_entity_prep_relations


from fastcoref import spacy_component

nlp = spacy.load('en_core_web_sm')
nlp.add_pipe("fastcoref")

class edge():
    def __init__(self,subj,rel,obj):
        self.subj = subj 
        self.rel = rel
        self.obj = obj



def main():
    url = "https://en.wikipedia.org/wiki/Thomas_Brenchley"
    text = scrape_wiki(url)

    doc = text_preprocess(nlp,text)

    graph = nx.DiGraph()

    for sentence in iter_sentences(doc):
        print(sentence)

        info = []
        for token in sentence:
            if token.dep_ == "pobj":
                info.append((token.text,[(child,child.dep_) for child in token.children]))
        print(info)

        verb_frames = build_verb_frames(sentence)
        entities = find_all_entities(verb_frames)

        print("verb_frames\n")
        print(verb_frames)

        print("entities\n")
        print(entities)

        node_list =[]
        for verb_frame in verb_frames:
            node_list.extend([resolve_entity(ent,verb_frame) for ent in entities])
        add_node(graph,node_list)
        
        
        for verb_frame in verb_frames:
            
            build_relations(graph,verb_frame)

        build_entity_prep_relations(graph,entities)

        print("\n")
        
    display_graph(graph=graph)

if __name__ == "__main__":
    main()
