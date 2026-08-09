class NodeRegistry():
    def __init__(self):
        self.proper_nodes = {}
        self.next_id = 0

    def get_or_create_prop_id(self,name):
        if name not in self.proper_nodes:
            self.proper_nodes[name] = self._generate_new_id()

        return self.proper_nodes[name]

    def get_common_noun_id(self):
        return self._generate_new_id()

    def _generate_new_id(self):
        new_id = f"node_{self.next_id}"
        self.next_id +=1
        
        return new_id

def chunk_to_entity(chunk):
    words = []

    for token in chunk:
        if token.dep_ in ("det"):
            continue
        if token == chunk.root and token.pos_ == "NOUN":
            words.append(token.lemma_)
        else:
            words.append(token.text)

    return " ".join(words)

def extract_entities(sentence):
    entity_map = {}
        
    for chunk in sentence.noun_chunks:
        if chunk.root in entity_map:
            continue

        if chunk.root.pos_ == "PRON":
            continue

        entity_map[chunk.root] = chunk_to_entity(chunk)
    
    #temporary catch
    for token in sentence:
        if token.pos_ in ("NOUN","PROPN") and token not in entity_map:
            entity_map[token] = token.text

    return entity_map