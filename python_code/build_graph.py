from python_code.data_classes import Entity,VerbFrame 
def determine_cluase(vf:VerbFrame):
    if vf.attributes:
        return "SVC"
    elif vf.i_objects and vf.object:
        return "SVOO"
    elif vf.object_compliments and vf.object:
        return "SVOC"
    elif vf.object:
        return "SVO"
    else:
        return "SV"

def build_relations(vf:VerbFrame):
    clause_type = determine_cluase(vf)

    nodes = []
    edges = []

    if clause_type == "SVC":
        pass
    elif clause_type == "SVOO":
        pass
    elif clause_type == "SVOC":
        pass
    elif clause_type == "SVO":
        pass
    elif clause_type == "SV":

        for subj in vf.subjects:
            
        pass
    else:
        print(f"not recognized clause_type {clause_type}")

def build_graph_count(text):
    nodes = set()
    edges = []

    for sentence in iter_sentences(text):
        named_entities = sentence.ents
        #allowed = ["PERSON","ORG"]

        #filtered_entities = [ent for ent in named_entities if ent.label_ in allowed]
        filtered_entities = named_entities
        '''
        for node in filtered_entities:
            nodes.add(node.text.strip().casefold())
            entity_map[node.root] = node.text.strip().casefold()
        '''
        
        for token in sentence:
            
            if token.dep_ == "ROOT":

                rel = getLemma(token.text,upos="VERB")[0] #lemmainflect seems to work much better for lemma
                subj = None
                obj = None


                for child in (token.children):
                    if child.dep_ in ("nsubj", "nsubjpass"):
                        subj = child.text
                                            
                    elif child.dep_ in ("dobj", "pobj", "attr"):
                        obj = child.text

                if (subj and obj):
                    new_edge = edge(subj,rel,obj)

                    nodes.add(subj)
                    nodes.add(obj)
                    edges.append(new_edge)
    return nodes,edges

def build_graph_object(nodes,edges):
    G = nx.DiGraph()
    
    for node in nodes:
        G.add_node(node)

    for edge in edges:
        G.add_edge(edge.subj,edge.obj,label=edge.rel)

    return G
        
def display_graph(graph):

    g = Network(height = "800px",width = "800px",notebook=False)
    g.toggle_drag_nodes(True)
    g.toggle_physics(False)

    g.barnes_hut()
    g.from_nx(graph)


    g.write_html("ex.html")