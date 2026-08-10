from python_code.data_classes import Entity,VerbFrame,Node
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

def add_node(graph:nx.digraph,node_list:list[Node]):
    for node in node_list:
        graph.add_node(
            node.id,
            label = node.label
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
        for subj in vf.subjects:
            for attr in vf.attributes:
                add_edge(graph, subj.id, attr.id, vf.verb)

    elif clause_type == "SVOO":
        for subj in vf.subjects:
            for obj in vf.objects:
                add_edge(graph, subj.id, obj.id, vf.verb)

                for iobj in vf.i_objects:
                    add_edge(graph, obj.id, iobj.id, "to")

    elif clause_type == "SVOC":
        for subj in vf.subjects:
            for obj in vf.objects:
                add_edge(graph, subj.id, obj.id, vf.verb)

                for comp in vf.object_compliments:
                    add_edge(graph, obj.id, comp.id, "complement")

    elif clause_type == "SVO":
        for subj in vf.subjects:
            for obj in vf.objects:
                add_edge(graph, subj.id, obj.id, vf.verb)

    elif clause_type == "SV":
        for subj in vf.subjects:
            for prep, entity in vf.prep_phrases:
                add_edge(
                    graph,
                    subj.id,
                    entity.id,
                    f"{vf.verb}_{prep}"
                )

    else:
        print(f"not recognized clause_type {clause_type}")

def build_entity_prep_relations(graph, entities):
    for entity in entities:
        for prep, target in entity.prep_phrases:
            add_edge(
                graph,
                entity.id,
                target.id,
                prep
            )
        
def display_graph(graph):

    g = Network(height = "800px",width = "800px",notebook=False,directed=True)
    g.toggle_drag_nodes(True)
    g.toggle_physics(False)

    g.barnes_hut()
    g.from_nx(graph)


    g.write_html("ex.html")