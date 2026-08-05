


import spacy
from itertools import combinations
import networkx as nx
import matplotlib.pyplot as plt

from python_code.read_wikipedia import scrape_wiki
from python_code.entities import extract_entities
from python_code.preprocess import text_preprocess
from python_code.utils import iter_sentences
from python_code.realtions import find_relations,identify_clause_components,determine_clause

from pyvis.network import Network
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

    for sentence in iter_sentences(doc):
        print(sentence)

        ent_map = extract_entities(sentence)

        clause_components = identify_clause_components(sentence)
        clause = determine_clause(clause_components)
        print(clause)
                
        find_relations(sentence,ent_map,clause)
    
    #text = "Joe Smith called London. Joe Smith helps Jane. Craig loves London. Bob hated London. The Cat ate The Mouse "

    #nodes,edges = build_graph_count(text)
    #graph = build_graph_object(nodes=nodes,edges=edges)
    #display_graph(graph=graph)

if __name__ == "__main__":
    main()
