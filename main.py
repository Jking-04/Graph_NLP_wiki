


import spacy
from itertools import combinations
import networkx as nx
import matplotlib.pyplot as plt

from python_code.read_wikipedia import scrape_wiki
from python_code.entities import extract_entities
from python_code.preprocess import text_preprocess
from python_code.utils import iter_sentences
from python_code.realtions import find_relations,identify_clause_components,determine_clause,build_verb_frames
from python_code.build_graph import find_all_entities,add_node,display_graph,build_relations


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

        verb_frames = build_verb_frames(sentence)
        enteties = find_all_entities(verb_frames)

        print("verb_frames\n")
        print(verb_frames)

        print("entities\n")
        print(enteties)

        add_node(graph,enteties)
        
        for verb_frame in verb_frames:
            build_relations(graph,verb_frame)

        print("\n")
        
    display_graph(graph=graph)

if __name__ == "__main__":
    main()
