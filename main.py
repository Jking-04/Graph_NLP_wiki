
import wikipediaapi
from urllib.parse import urlparse,unquote
import spacy
from itertools import combinations
import networkx as nx
import matplotlib.pyplot as plt
import os

from lemminflect import getLemma



nlp = spacy.load('en_core_web_sm')


PROJECT_NAME = "Graph_NLP_wiki"
EMAIL = os.getenv("WIKIMEDIA_API_EMAIL")

print("spaCy version:", spacy.__version__)
print("Model:", nlp.meta["name"])
print("Model version:", nlp.meta["version"])

print(nlp.pipe_names)
print(nlp.get_pipe("lemmatizer").mode)

class edge():
    def __init__(self,subj,rel,obj):
        self.subj = subj 
        self.rel = rel
        self.obj = obj

def url_to_title(http_url):
    path = urlparse(http_url).path
    title = path.split("/wiki/")[-1]
    return unquote(title)

def scrape_wiki(http_url):
    wiki_wiki = wikipediaapi.Wikipedia(
        user_agent=f'{PROJECT_NAME} ({EMAIL})' if EMAIL else PROJECT_NAME,
        language='en'
        )

    title = url_to_title(http_url)
    page_py = wiki_wiki.page(title=title)
    return page_py.text

def iter_sentences(text):
    doc = nlp(text)

    for sentence in doc.sents:
        yield sentence

def build_graph_count(text):
    nodes = set()
    edges = []
    entity_map = {}

    for sentence in iter_sentences(text):
        named_entities = sentence.ents
        #allowed = ["PERSON","ORG"]

        #filtered_entities = [ent for ent in named_entities if ent.label_ in allowed]
        filtered_entities = named_entities

        for node in filtered_entities:
            nodes.add(node.text.strip().casefold())
            entity_map[node.root] = node.text.strip().casefold()

        for token in sentence:
            if token.pos_ == "VERB":
                rel = getLemma(token.text,upos="VERB")[0]

                obj = None
                subj = None

                [child for child in token.children]
                for child in token.children:
                    if child in entity_map.keys():
                    
                        if child.dep_ in ("nsubj", "nsubjpass"):
                            subj = entity_map[child]
                        
                        elif child.dep_ in ("dobj", "pobj", "attr"):
                            obj = entity_map[child]

                if (subj and obj):
                    new_edge = edge(subj,rel,obj)
                    edges.append(new_edge)

        

    return nodes,edges

def build_graph_object(nodes,edges):
    G = nx.DiGraph()
    
    for node in nodes:
        G.add_node(node)

    for edge in edges:
        G.add_edge(edge.subj,edge.obj,rel=edge.rel)

    return G
        
def display_graph(graph):
    # Visualize the knowledge graph with colored nodes
    # Calculate node degrees
    print(graph.number_of_nodes())
    print(graph.number_of_edges())
    
    node_degrees = dict(graph.degree)

    # Assign colors based on node degrees
    node_colors = ['lightgreen' if degree == max(node_degrees.values()) else 'lightblue' for degree in node_degrees.values()]

    # Adjust the layout for better spacing
    pos = nx.spring_layout(graph, seed=42, k=1.5)

    labels = nx.get_edge_attributes(graph, 'rel')
    nx.draw(graph, pos, with_labels=True, font_weight='bold', node_size=700, node_color=node_colors, font_size=8, arrowsize=10)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels, font_size=8)
    plt.show()

def main():
    #url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    #text = scrape_wiki(url)

    text = "Joe Smith called London. Joe Smith helps Jane. Craig loves London. Bob hated London. "

    nodes,edges = build_graph_count(text)
    graph = build_graph_object(nodes=nodes,edges=edges)
    display_graph(graph=graph)

if __name__ == "__main__":
    main()
