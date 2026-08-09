from python_code.data_classes import Entity,VerbFrame
import networkx as nx
from pyvis.network import Network

def find_all_nested_entities(Ent:Entity):
    entities = [Ent]

    for _,pobj in Ent.prep_phrases:
        entities.extend(find_all_nested_entities(pobj))

    return entities

def find_all_entities(vf_list: list[VerbFrame]):
    entities = []

    for vf in vf_list:
        for subj in vf.subjects:
            entities.extend(find_all_nested_entities(subj))

        for obj in vf.objects:
            entities.extend(find_all_nested_entities(obj))

        for iobj in vf.i_objects:
            entities.extend(find_all_nested_entities(iobj))

        for comp in vf.object_compliments:
            entities.extend(find_all_nested_entities(comp))

        for attr in vf.attributes:
            entities.extend(find_all_nested_entities(attr))

        for _, pobj in vf.prep_phrases:
            entities.extend(find_all_nested_entities(pobj))

    return entities

def add_node(graph:nx.digraph,entity_list:list[Entity]):
    for ent in entity_list:
        graph.add_node(
            ent.id,
            label = ent.node_name()
        )

def add_edge(graph:nx.digraph,origin_id,target_id,rel):
    graph.add_edge(origin_id,target_id,label=rel)

def determine_clause(vf:VerbFrame):
    if vf.attributes:
        return "SVC"
    elif vf.i_objects and vf.objects:
        return "SVOO"
    elif vf.object_compliments and vf.objects:
        return "SVOC"
    elif vf.objects:
        return "SVO"
    else:
        return "SV"

def build_relations(graph: nx.DiGraph, vf: VerbFrame):
    clause_type = determine_clause(vf)

    if clause_type == "SVC":
        rel = vf.verb
        for subj in vf.subjects:
            for attr in vf.attributes:
                add_edge(graph, subj.id, attr.id, rel)

    elif clause_type == "SVOO":
        subj = vf.subjects[0]
        obj = vf.objects[0]
        iobj = vf.i_objects[0]
        rel = vf.verb

        add_edge(graph, subj.id, obj.id, rel)
        add_edge(graph, obj.id, iobj.id, "to")

    elif clause_type == "SVOC":
        subj = vf.subjects[0]
        obj = vf.objects[0]
        comp = vf.object_compliments[0]
        rel = vf.verb

        add_edge(graph, subj.id, obj.id, rel)
        add_edge(graph, obj.id, comp.id, "complement")

    elif clause_type == "SVO":
        rel = vf.verb

        for subj in vf.subjects:
            for obj in vf.objects:
                add_edge(graph, subj.id, obj.id, rel)

    elif clause_type == "SV":
        subj = vf.subjects[0]

        if not vf.prep_phrases:
            return

        for prep, entity in vf.prep_phrases:
            rel = f"{vf.verb}_{prep}"
            add_edge(graph, subj.id, entity.id, rel)

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