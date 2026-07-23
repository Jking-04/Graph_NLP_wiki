
import wikipediaapi
from urllib.parse import urlparse,unquote
import spacy
from itertools import combinations
import networkx as nx
import matplotlib.pyplot as plt

nlp = spacy.load('en_core_web_sm')

def url_to_title(http_url):
    path = urlparse(http_url).path
    title = path.split("/wiki/")[-1]
    return unquote(title)

def scrape_wiki(http_url):
    wiki_wiki = wikipediaapi.Wikipedia(user_agent='Graph_NLP_wiki (example_email@email.com)', language='en')

    title = url_to_title(http_url)

    page_py = wiki_wiki.page(title=title)

    return page_py.text

def iter_sentences(text):
    doc = nlp(text)

    for sentence in doc.sents:
        yield sentence

def build_graph_count(text):
    nodes = set()
    edge_count = {}

    for sentence in iter_sentences(text):
        named_entities = sentence.ents
        allowed = ["PERSON","ORG"]
        filtered_entities = [ent for ent in named_entities if ent.label_ in allowed]

        if(len(filtered_entities)>=2):
            for node in filtered_entities:
                nodes.add(node.text)
            for entity_pairs in combinations(filtered_entities,2):
                key = tuple(sorted([entity_pairs[0].text,entity_pairs[1].text]))

                edge_count[key] = edge_count.get(key,0)+1
        elif(len(filtered_entities)==1):
            nodes.add(filtered_entities[0])

    return nodes,edge_count

def build_graph_object(nodes,edge_count):
    G = nx.Graph()

    for node in nodes:
        G.add_node(node)

    for edge_key,edge_val in edge_count.items():
        G.add_node(edge_key[0])
        G.add_node(edge_key[1])

        G.add_edge(edge_key[0],edge_key[1],count = edge_val)

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

    labels = nx.get_edge_attributes(graph, 'count')
    nx.draw(graph, pos, with_labels=True, font_weight='bold', node_size=700, node_color=node_colors, font_size=8, arrowsize=10)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels, font_size=8)
    plt.show()

def main():
    url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    text = scrape_wiki(url)
    nodes,edge_count = build_graph_count(text)
    graph = build_graph_object(nodes=nodes,edge_count=edge_count)
    display_graph(graph=graph)

if __name__ == "__main__":
    main()
